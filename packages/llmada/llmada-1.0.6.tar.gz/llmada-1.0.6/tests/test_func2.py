import pytest
import asyncio
import time
import random
from typing import AsyncGenerator, AsyncIterator

# 假设这是你的大模型函数，现在支持异步流式生成
async def my_awesome_llm_async_stream(prompt: str, temperature: float = 0.7, max_tokens: int = 50) -> AsyncGenerator[str, None]:
    """
    模拟一个大模型的异步流式响应。
    在实际使用中，这里会调用你的LLM API或本地模型的异步流式接口。
    """
    if not isinstance(prompt, str):
        raise TypeError("Prompt must be a string.")
    if not prompt:
        yield ""
        return

    # 模拟一些异步处理前的等待
    await asyncio.sleep(0.05)

    full_response = ""
    # 简单的基于关键词的响应
    if "hello" in prompt.lower():
        messages = ["Hello", " there!", " How", " can", " I", " assist", " you", " today?"]
    elif "weather" in prompt.lower():
        messages = ["I'm", " sorry,", " I", " cannot", " provide", " real-time", " weather", " information."]
    elif "sum" in prompt.lower() or "add" in prompt.lower():
        try:
            parts = prompt.lower().split()
            nums = [int(s) for s in parts if s.isdigit()]
            if len(nums) >= 2:
                result = sum(nums)
                messages = [f"The sum of", " the numbers", " is", f" {result}."]
            else:
                messages = ["Please", " provide", " at", " least", " two", " numbers", " to", " sum."]
        except ValueError:
            messages = ["I", " can", " try", " to", " sum", " numbers,", " but", " please", " provide", " valid", " integers."]
    elif "long" in prompt.lower():
        long_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        messages = [word + " " for word in long_text.split()]
    elif "error" in prompt.lower():
        # 模拟一个LLM内部可能遇到的错误情况
        if random.random() < 0.5: # 模拟有时在开始就抛错
            raise ValueError("Simulated initial async LLM processing error for streaming.")
        else: # 有时生成一部分后才抛错
            yield "Partial async response... "
            await asyncio.sleep(0.1) # 异步等待
            raise RuntimeError("Simulated mid-stream async LLM processing error.")
    else:
        messages = [f"You", f" said:", f" '{prompt}'.", f" This", f" is", f" a", f" generic", f" response", f" from", f" the", f" model."]

    for token in messages:
        if len(full_response) + len(token) > max_tokens:
            break
        full_response += token
        yield token
        await asyncio.sleep(random.uniform(0.01, 0.05)) # 模拟每个token之间的异步延迟

# ---------------------------------------------------------------------------------------
# Pytest 测试用例
# ---------------------------------------------------------------------------------------

# 使用 @pytest_asyncio.fixture 而不是 @pytest.fixture
@pytest.fixture(scope="module")
async def llm_async_stream_instance():
    """
    为异步流式LLM测试提供一个fixture。
    """
    print("\n--- Setting up Async Streaming LLM instance for testing ---")
    yield my_awesome_llm_async_stream
    print("--- Tearing down Async Streaming LLM instance ---")

# 所有的异步测试函数都必须用 @pytest.mark.asyncio 标记
# 1. 基本异步流式响应测试
@pytest.mark.asyncio
async def test_basic_async_streaming_response(llm_async_stream_instance):
    """
    测试LLM异步流式生成是否能产生一个非空、包含字符串的序列。
    """
    prompt = "Tell me a short async story."
    # 直接调用fixture返回的异步函数
    response_generator = llm_async_stream_instance(prompt)

    collected_tokens = []
    # 使用 async for 迭代异步生成器
    async for token in response_generator:
        assert isinstance(token, str)
        collected_tokens.append(token)
    
    assert len(collected_tokens) > 0
    assert "".join(collected_tokens).strip() != "" # 确保总响应不为空

# 2. 验证异步流式令牌（token）的类型和数量
@pytest.mark.asyncio
async def test_async_streaming_token_types_and_count(llm_async_stream_instance):
    """
    测试异步流式生成的每个令牌都是字符串，并且生成的令牌数量符合预期。
    """
    prompt = "Hello async world."
    response_generator = llm_async_stream_instance(prompt)

    total_tokens = 0
    async for token in response_generator:
        assert isinstance(token, str)
        total_tokens += 1
    
    assert total_tokens > 0 # 应该至少生成一些令牌

# 3. max_tokens 限制测试 (异步流式)
@pytest.mark.asyncio
async def test_max_tokens_limit_async_streaming(llm_async_stream_instance):
    """
    测试异步流式生成中 max_tokens 参数是否有效限制了总响应长度。
    """
    prompt = "Write a very long detailed explanation about quantum physics for async testing."
    max_len = 30 # 设置一个较小的max_tokens以便测试
    response_generator = llm_async_stream_instance(prompt, max_tokens=max_len)

    collected_response = ""
    async for token in response_generator:
        collected_response += token
    
    assert len(collected_response) <= max_len + 5 # 允许因为词边界稍微超出一点点

# 4. 确保异步生成器在完成后停止
@pytest.mark.asyncio
async def test_async_generator_exhaustion(llm_async_stream_instance):
    """
    测试异步流式生成器在所有内容生成完毕后是否会停止。
    """
    prompt = "End of async stream."
    response_generator = llm_async_stream_instance(prompt)

    # 异步地耗尽生成器
    async for _ in response_generator:
        pass
    
    # 再次尝试从已耗尽的生成器中获取，预期 StopAsyncIteration
    with pytest.raises(StopAsyncIteration):
        await response_generator.__anext__() # 获取下一个元素的异步方法

# 5. 空Prompt处理（异步流式）
@pytest.mark.asyncio
async def test_empty_prompt_async_streaming(llm_async_stream_instance):
    """
    测试异步流式模型对空Prompt的处理。
    """
    prompt = ""
    response_generator = llm_async_stream_instance(prompt)
    
    collected_tokens = []
    async for token in response_generator:
        collected_tokens.append(token)

    assert len(collected_tokens) == 1
    assert collected_tokens[0] == ""

# 6. 无效输入类型处理（异步流式）
@pytest.mark.asyncio
async def test_invalid_input_type_async_streaming(llm_async_stream_instance):
    """
    测试异步流式模型对非字符串Prompt的处理，预期抛出TypeError。
    """
    with pytest.raises(TypeError):
        # 尝试迭代生成器，因为异常可能在生成器被迭代时才抛出
        async for _ in llm_async_stream_instance(123):
            pass
    
    with pytest.raises(TypeError):
        async for _ in llm_async_stream_instance(["list"]):
            pass

# 7. 错误处理测试 (异步流式)
@pytest.mark.asyncio
async def test_async_streaming_error_handling(llm_async_stream_instance):
    """
    测试异步流式生成过程中抛出异常的情况。
    """
    prompt = "Simulate an error"
    response_generator = llm_async_stream_instance(prompt)

    with pytest.raises((ValueError, RuntimeError)) as excinfo:
        # 异步迭代生成器直到遇到异常
        async for _ in response_generator:
            pass
    
    assert "error" in str(excinfo.value).lower()

# 8. 响应的完整性 (拼接所有token后与预期结果的比较)
@pytest.mark.asyncio
async def test_async_streaming_response_content(llm_async_stream_instance):
    """
    测试异步流式生成拼接后的完整内容是否符合预期。
    """
    prompt = "Hello, async model!"
    response_generator = llm_async_stream_instance(prompt)
    
    full_response = ""
    async for token in response_generator:
        full_response += token
    
    full_response = full_response.strip()
    assert "hello" in full_response.lower()
    assert "assist" in full_response.lower()

# 9. 性能测试 (异步流式 - 首个token延迟和总延迟)
@pytest.mark.asyncio
async def test_async_streaming_performance(llm_async_stream_instance):
    """
    测试异步流式生成的首个token延迟 (Time To First Token - TTFT) 和总生成时间。
    """
    prompt = "Generate a moderate length async response to test performance."
    
    start_time = time.perf_counter()
    response_generator = llm_async_stream_instance(prompt)
    
    first_token_received = False
    total_tokens = 0
    
    async for i, token in enumerate(response_generator):
        if not first_token_received:
            ttft = time.perf_counter() - start_time
            print(f"\nAsync TTFT: {ttft:.4f} seconds")
            assert ttft < 0.5 # 根据模拟的sleep时间调整
            first_token_received = True
        
        assert isinstance(token, str)
        total_tokens += 1
    
    end_time = time.perf_counter()
    total_duration = end_time - start_time
    print(f"Total duration for {total_tokens} async tokens: {total_duration:.4f} seconds")
    
    assert total_tokens > 0
    assert total_duration < 2.0 # 根据模拟的复杂度和期望响应长度调整