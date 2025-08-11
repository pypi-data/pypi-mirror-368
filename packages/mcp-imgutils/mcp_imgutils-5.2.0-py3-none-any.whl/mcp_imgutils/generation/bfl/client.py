import asyncio
import json
import random
from collections.abc import Callable
from typing import Any

import httpx

from ...common.errors import BFLError
from .config import (
    API_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_SIZE,
    DEFAULT_TIMEOUT,
    MODEL_CONFIGS,
    FluxModel,
    FluxTool,
    is_ultra_model,
    size_to_aspect_ratio,
    validate_bfl_url,
)


class FluxClient:
    """
    Black Forest Labs API 客户端

    支持上下文管理器和自动重试机制，提供强健的API调用能力。

    Example:
        async with FluxClient(api_key, send_log) as client:
            image_data, url = await client.generate_image("A beautiful sunset")
    """

    def __init__(
        self,
        api_key: str,
        send_log: Callable[[str, str], None],
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        初始化客户端

        Args:
            api_key: BFL API密钥
            send_log: 日志记录函数
            max_retries: 最大重试次数
            retry_delay: 重试延迟基础时间（秒）
        """
        if not api_key or not api_key.strip():
            raise ValueError("API密钥不能为空")

        self.api_key = api_key.strip()
        self.base_url = API_BASE_URL
        self.send_log = send_log
        self.max_retries = max(0, max_retries)
        self.retry_delay = max(0.1, retry_delay)
        self._client = None

        self.send_log("debug", f"初始化客户端完成: {self.base_url}, 最大重试: {self.max_retries}")

    @property
    def client(self) -> httpx.AsyncClient:
        """获取HTTP客户端实例"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=DEFAULT_TIMEOUT,
                headers={
                    "x-key": self.api_key,
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
        return self._client

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

    async def close(self):
        """关闭客户端"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            self.send_log("debug", "客户端已关闭")

    async def _retry_request(self, request_func, *args, **kwargs):
        """
        带重试机制的请求执行器

        Args:
            request_func: 要执行的请求函数
            *args, **kwargs: 传递给请求函数的参数

        Returns:
            请求函数的返回值

        Raises:
            BFLError: 重试耗尽后的最后一个错误
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await request_func(*args, **kwargs)
            except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as e:
                last_exception = e
                if attempt < self.max_retries:
                    # 指数退避 + 随机抖动
                    delay = self.retry_delay * (2 ** attempt) + random.uniform(0, 1)
                    self.send_log("warning", f"请求失败，{delay:.1f}秒后重试 (第{attempt + 1}/{self.max_retries + 1}次): {str(e)}")
                    await asyncio.sleep(delay)
                else:
                    self.send_log("error", f"重试耗尽，请求最终失败: {str(e)}")
            except Exception as e:
                # 非网络错误不重试
                self.send_log("error", f"请求出现非网络错误，不重试: {str(e)}")
                raise

        # 重试耗尽，抛出最后一个异常
        if isinstance(last_exception, httpx.TimeoutException):
            raise BFLError(408, f"请求超时，重试{self.max_retries}次后失败: {str(last_exception)}")
        elif isinstance(last_exception, httpx.ConnectError | httpx.NetworkError):
            raise BFLError(503, f"网络连接失败，重试{self.max_retries}次后失败: {str(last_exception)}")
        else:
            raise BFLError(500, f"未知网络错误，重试{self.max_retries}次后失败: {str(last_exception)}")

    def _validate_prompt(self, prompt: str) -> None:
        """
        验证提示词参数

        Args:
            prompt: 要验证的提示词

        Raises:
            ValueError: 提示词无效时抛出
        """
        if not prompt or not prompt.strip():
            raise ValueError("提示词不能为空")

        prompt = prompt.strip()

        # 检查长度限制
        if len(prompt) > 2000:
            raise ValueError(f"提示词过长，最大支持2000字符，当前{len(prompt)}字符")

        # 检查是否包含有害内容的基本关键词（可以根据需要扩展）
        forbidden_keywords = ['nsfw', 'nude', 'naked', 'porn', 'sex']
        prompt_lower = prompt.lower()
        for keyword in forbidden_keywords:
            if keyword in prompt_lower:
                raise ValueError(f"提示词包含不当内容: {keyword}")

        self.send_log("debug", f"提示词验证通过: {len(prompt)}字符")

    def _validate_size(self, size: tuple[int, int], model: FluxModel) -> None:
        """
        验证图片尺寸参数

        Args:
            size: 图片尺寸 (width, height)
            model: FLUX模型

        Raises:
            ValueError: 尺寸无效时抛出
        """
        width, height = size

        if not isinstance(width, int) or not isinstance(height, int):
            raise ValueError("图片尺寸必须是整数")

        if width <= 0 or height <= 0:
            raise ValueError("图片尺寸必须大于0")

        # 检查最小尺寸
        min_size = 256
        if width < min_size or height < min_size:
            raise ValueError(f"图片尺寸过小，最小支持{min_size}x{min_size}")

        # 检查模型特定的尺寸限制
        model_config = MODEL_CONFIGS[model]
        max_width, max_height = model_config.max_size

        if not is_ultra_model(model) and (width > max_width or height > max_height):
            raise ValueError(f"图片尺寸超出限制: 最大允许 {max_width}x{max_height}, 请求 {width}x{height}")

        self.send_log("debug", f"尺寸验证通过: {width}x{height}")

    async def _get_status_response(self, request_id: str, polling_url: str = None) -> httpx.Response:
        """获取状态响应"""
        if polling_url:
            # 验证 polling_url 来自可信域名
            if not validate_bfl_url(polling_url):
                self.send_log("error", f"不可信的轮询URL: {polling_url}")
                raise BFLError(400, f"不可信的轮询URL: {polling_url}")

            return await self.client.get(polling_url)
        else:
            # 回退到传统方式 (向后兼容)
            return await self.client.get(
                f"{self.base_url}/get_result",
                params={"id": request_id}
            )

    async def _process_status_response(self, request_id: str, status_response: httpx.Response) -> tuple[bytes, str] | None:
        """处理状态响应，返回None表示需要继续轮询"""
        self.send_log("debug", f"任务 {request_id} HTTP状态码: {status_response.status_code}")
        self.send_log("debug", f"任务 {request_id} 原始响应: {status_response.text}")

        status_json = status_response.json()
        self.send_log("debug", f"任务 {request_id} 状态: {json.dumps(status_json, ensure_ascii=False)}")

        if status_response.status_code != 200:
            error_msg = status_json.get('detail') or status_json.get('error', '获取结果失败')
            self.send_log("error", f"任务 {request_id} 出错 (HTTP {status_response.status_code}): {error_msg}")
            raise BFLError(status_response.status_code, error_msg)

        status = status_json.get("status")
        if status == "Ready":
            result = status_json.get("result", {})
            image_url = result.get("sample")
            if not image_url:
                self.send_log("error", f"任务 {request_id} 未返回图片URL")
                raise BFLError(500, "未返回图片URL")

            self.send_log("info", f"任务 {request_id} 完成，下载图片: {image_url}")
            image_response = await self.client.get(image_url)

            if image_response.status_code != 200:
                self.send_log("error", f"任务 {request_id} 图片下载失败")
                raise BFLError(500, "图片下载失败")

            return image_response.content, image_url

        elif status == "Failed":
            error_msg = status_json.get("error", "生成失败，无具体原因")
            self.send_log("error", f"任务 {request_id} 失败: {error_msg}")
            raise BFLError(500, error_msg)

        self.send_log("debug", f"任务 {request_id} 进行中: {status}")
        return None

    async def _poll_status(self, request_id: str, polling_url: str = None, timeout: int = 60) -> tuple[bytes, str]:
        """
        轮询任务状态并获取结果

        Args:
            request_id: 任务ID
            polling_url: BFL 返回的轮询 URL (如果提供，将使用此 URL 而不是构造 URL)
            timeout: 超时时间(秒)

        Returns:
            Tuple[bytes, str]: 生成的图片数据和原始图片URL

        Raises:
            BFLError: API 调用错误
        """
        start_time = asyncio.get_event_loop().time()
        interval = 1.0  # 初始轮询间隔
        max_interval = 5.0  # 最大轮询间隔

        while True:
            if (asyncio.get_event_loop().time() - start_time) > timeout:
                self.send_log("error", f"任务 {request_id} 等待超时")
                raise BFLError(408, "任务等待超时")

            try:
                # 获取状态响应
                status_response = await self._get_status_response(request_id, polling_url)

                # 处理响应
                result = await self._process_status_response(request_id, status_response)
                if result:
                    return result

                # 继续轮询，增加间隔
                interval = min(interval * 1.5, max_interval)
                await asyncio.sleep(interval)

            except (TimeoutError, httpx.TimeoutException) as e:
                self.send_log("warning", f"任务 {request_id} 状态查询超时: {str(e)}")
                interval = min(interval * 2, max_interval)
                await asyncio.sleep(interval)
            except BFLError:
                # 重新抛出BFL错误
                raise
            except Exception as e:
                self.send_log("error", f"任务 {request_id} 状态查询失败: {str(e)}")
                raise BFLError(500, f"状态查询异常: {str(e)}")

    async def generate_image(
        self,
        prompt: str,
        model: FluxModel = DEFAULT_MODEL,
        size: tuple[int, int] = DEFAULT_SIZE,
        **kwargs: Any
    ) -> tuple[bytes, str]:
        """
        生成图片

        Args:
            prompt: 图片描述
            model: FLUX 模型
            size: 图片尺寸 (width, height)
            **kwargs: 其他参数

        Returns:
            Tuple[bytes, str]: 生成的图片数据和原始图片URL

        Raises:
            BFLError: API 调用错误
            ValueError: 参数验证失败
        """
        # 输入验证
        self._validate_prompt(prompt)
        self._validate_size(size, model)

        width, height = size

        # 构造请求数据
        if is_ultra_model(model):
            # flux-pro-1.1-ultra 使用 aspect_ratio 参数
            aspect_ratio = size_to_aspect_ratio(width, height)
            self.send_log("debug", f"Ultra模型使用宽高比: {aspect_ratio}")
            request_data = {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                **kwargs
            }
        else:
            # 其他模型使用 width/height 参数
            request_data = {
                "prompt": prompt,
                "width": width,
                "height": height,
                **kwargs
            }

        # 使用重试机制发起请求
        async def _make_request():
            self.send_log("debug", f"发起生成请求: {json.dumps(request_data, ensure_ascii=False)}")
            request_url = f"{self.base_url}/{model.value}"

            response = await self.client.post(
                request_url,
                json=request_data
            )

            response_json = response.json()
            self.send_log("debug", f"创建任务响应: {json.dumps(response_json, ensure_ascii=False)}")

            if response.status_code != 200:
                error_msg = response_json.get('detail') or response_json.get('error', '生成请求失败')
                self.send_log("error", f"创建任务失败: {error_msg}")
                raise BFLError(response.status_code, error_msg)

            return response_json

        try:
            response_json = await self._retry_request(_make_request)

            request_id = response_json.get("id")
            polling_url = response_json.get("polling_url")

            if not request_id:
                self.send_log("error", "响应中缺少任务ID")
                raise BFLError(500, "响应中缺少任务ID")

            self.send_log("info", f"成功创建任务: {request_id}")

            if polling_url:
                self.send_log("debug", f"使用BFL提供的轮询URL: {polling_url}")
                return await self._poll_status(request_id, polling_url)
            else:
                self.send_log("debug", "未提供轮询URL，使用传统方式")
                return await self._poll_status(request_id)

        except httpx.TimeoutException as e:
            self.send_log("error", f"请求超时: {str(e)}")
            raise BFLError(408, f"请求超时: {str(e)}")
        except httpx.RequestError as e:
            self.send_log("error", f"请求错误: {str(e)}")
            raise BFLError(500, f"请求错误: {str(e)}")
        except asyncio.CancelledError:
            self.send_log("warning", "任务被取消")
            raise
        except Exception as e:
            self.send_log("error", f"处理异常: {str(e)}")
            raise BFLError(500, f"处理异常: {str(e)}")

    async def use_tool(self, tool: FluxTool, image: bytes, prompt: str, **kwargs: Any) -> bytes:
        raise NotImplementedError("工具功能尚未实现")
