"""
client.py 用于管理client
"""

import requests
import time
import json
import base64
import httpx
from .log import Log

logger = Log.logger

class OpenAIClient:
    """
    使用 openai 官方包对接 OpenAI API，支持简单对话和流式对话
    """

    def __init__(
        self, api_key: str, api_base: str = "https://api.bianxie.ai/v1/chat/completions"
    ):
        """
        初始化 OpenAI 客户端
        """
        self.api_key = api_key
        self.api_base = api_base
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

    def request(self, params: dict) -> dict:
        """
        简单对话：直接调用 OpenAI API 并返回完整响应
        """

        try:
            logger.info('request running')
            time1 = time.time()
            response = requests.post(self.api_base, headers=self.headers, json=params)
            time2 = time.time()
            logger.debug(time2 - time1)
            return response.json()
        except Exception as e:
            logger.error(e)
            raise Exception(f"API request failed: {e}") from e

    def request_stream_http2(self, params: dict) -> dict:
        """
        简单对话：直接调用 OpenAI API 并返回流式响应
        """
        logger.info("request_stream_http2")
        try:
            self.headers["Accept"] = "text/event-stream"

            payload = params
            with httpx.Client(http2=True, timeout=None) as client:
                with client.stream(
                    "POST", self.api_base, headers=self.headers, json=payload
                ) as response:
                    response.raise_for_status()
                    buffer = b""
                    for chunk in response.iter_bytes():
                        buffer += chunk
                        while b"\n" in buffer:
                            line_bytes, _, buffer = buffer.partition(b"\n")
                            decoded_line = line_bytes.decode("utf-8")

                            if decoded_line.startswith("data:"):
                                json_str = decoded_line[len("data:") :].strip()

                                if json_str == "[DONE]":
                                    return  # End the generator

                                try:
                                    data = json.loads(json_str)
                                    # Extract content based on common LLM API response structure
                                    if "choices" in data and data["choices"]:
                                        chunk_content = data["choices"][0]["delta"].get(
                                            "content", ""
                                        )
                                        if chunk_content:
                                            yield chunk_content  # Yield the generated content chunk
                                except json.JSONDecodeError:
                                    yield f"[ERROR: Malformed data received: {json_str}]"

        except httpx.RequestError as e:
            error_msg = f"Request failed: {e}"
            raise ConnectionError(
                error_msg
            ) from e  # Re-raise as a custom error or simpler Exception
        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            raise RuntimeError(error_msg) from e

    async def arequest_stream_http2(self, params: dict):
        """
        简单对话：直接调用 OpenAI API 并返回流式响应 (异步版本)
        """
        logger.info("arequest_stream_http2")
        try:
            # 设置 Accept 头为 text/event-stream，表示期望流式事件
            self.headers["Accept"] = "text/event-stream"
            payload = params

            # 使用 httpx.AsyncClient 进行异步 HTTP 请求
            # timeout=None 表示不设置请求超时时间，由底层 TCP/TLS 决定
            async with httpx.AsyncClient(http2=True, timeout=None) as client:
                # 发送 POST 请求并获取异步响应流
                async with client.stream(
                    "POST", self.api_base, headers=self.headers, json=payload
                ) as response:
                    # 检查 HTTP 响应状态码，如果不是 2xx，则抛出异常
                    response.raise_for_status()

                    buffer = b""
                    # 异步迭代响应的字节块
                    async for chunk in response.aiter_bytes():
                        buffer += chunk
                        # 处理可能包含多行或不完整行的缓冲区
                        while b"\n" in buffer:
                            line_bytes, _, buffer = buffer.partition(b"\n")
                            decoded_line = line_bytes.decode("utf-8")

                            if decoded_line.startswith("data:"):
                                json_str = decoded_line[len("data:") :].strip()

                                if json_str == "[DONE]":
                                    return  # 结束生成器

                                try:
                                    data = json.loads(json_str)
                                    # 根据常见的 LLM API 响应结构提取内容
                                    if "choices" in data and data["choices"]:
                                        chunk_content = data["choices"][0]["delta"].get(
                                            "content", ""
                                        )
                                        if chunk_content:
                                            # 异步 yield 生成的内容块
                                            yield chunk_content
                                except json.JSONDecodeError:
                                    yield f"[ERROR: Malformed data received: {json_str}]"

        except httpx.RequestError as e:
            error_msg = f"Request failed: {e}"
            # 异步函数中也抛出异常
            raise ConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            # 异步函数中也抛出异常
            raise RuntimeError(error_msg) from e

    def request_stream(self, params: dict) -> dict:
        """
        简单对话：直接调用 OpenAI API 并返回流式响应
        """
        try:
            time1 = time.time()
            response = requests.post(
                self.api_base, headers=self.headers, json=params, stream=True
            )

            # 检查HTTP状态码
            if response.status_code == 200:
                print("Received streaming response:")
                # 逐行处理响应内容
                # iter_lines() 迭代响应内容，按行分割，并解码
                time2 = time.time()
                for line in response.iter_lines():
                    # lines are bytes, convert to string
                    line = line.decode("utf-8")

                    # Server-Sent Events (SSE) messages start with 'data: '
                    # and the stream ends with 'data: [DONE]'
                    if line.startswith("data:"):
                        # Extract the JSON string after 'data: '
                        json_str = line[len("data:") :].strip()

                        if json_str == "[DONE]":
                            break  # End of stream

                        if json_str:  # Ensure it's not an empty data line
                            try:
                                # Parse the JSON string into a dictionary
                                chunk = json.loads(json_str)

                                # Extract the content chunk (similar structure to OpenAI API)
                                # Check if choices and delta exist before accessing content
                                if (
                                    chunk
                                    and "choices" in chunk
                                    and len(chunk["choices"]) > 0
                                ):
                                    delta = chunk["choices"][0].get("delta")
                                    if delta and "content" in delta:
                                        content_chunk = delta["content"]
                                        # Print the chunk without a newline, immediately flushing the output
                                        # print(content_chunk, end='', flush=True)
                                        yield content_chunk

                            except json.JSONDecodeError as e:
                                print(
                                    f"\nError decoding JSON chunk: {e}\nChunk: {json_str}"
                                )
                            except Exception as e:
                                print(
                                    f"\nError processing chunk: {e}\nChunk data: {chunk}"
                                )

                print(
                    f"\n(Streaming finished) {time2-time1}"
                )  # Add a newline after the stream is complete

            else:
                # Handle non-200 responses
                print(f"Error: Received status code {response.status_code}")
                print("Response body:")
                print(response.text)  # Print the full error response if not streaming

        except requests.exceptions.RequestException as e:
            # TODO if "439" in ccc
            print(f"Request Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def request_modal(self):
        #TODO 图像理解
        def get_img_content(inputs=str):
            if is_url:
                return "https://github.com/dianping/cat/raw/master/cat-home/src/main/webapp/images/logo/cat_logo03.png"
            else:

                def image_to_base64(image_path):
                    with open(image_path, "rb") as image_file:
                        image_data = image_file.read()
                        base64_encoded_data = base64.b64encode(image_data)
                        base64_encoded_str = base64_encoded_data.decode("utf-8")
                        return base64_encoded_str

                image_base64 = image_to_base64(inputs)
                return f"data:image/jpeg;base64,{image_base64}"

        data = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "这张图片的图标是个什么动物？"},
                        {
                            "type": "image_url",
                            "image_url": {"url": get_img_content("111.png")},
                        },
                    ],
                }
            ],
        }

        response = requests.post(self.api_base, headers=self.headers, json=data)
        return response.json()
