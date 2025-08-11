import sys
import os
import time
from dotenv import load_dotenv
import pytest
from llmada import BianXieAdapter, KimiAdapter, ArkAdapter, GoogleAdapter

# 超市式的测试用例编写方案

# load_dotenv()


@pytest.fixture(scope="module")
def bx():
    """
    如果你的LLM需要实例化或加载，可以在这里完成。
    例如：model = LLMClass(config_path="config.yaml")
    return model
    """
    yield BianXieAdapter() # 返回函数本身

@pytest.mark.skip("通过")
def test_product_response(bx):
    """
    测试LLM是否能对一个简单输入产生响应。
    """
    prompt = "Hello, world!"
    response = bx.product(prompt)
    assert isinstance(response, str)
    assert len(response) > 0 # 响应不应该为空

@pytest.mark.skip("通过")
def test_product_stream_response(bx):
    """
    测试LLM是否能对一个简单输入产生响应。
    """

    prompt = "Tell me a short story."
    response_generator = bx.product_stream(prompt)

    collected_tokens = []
    for token in response_generator:
        assert isinstance(token, str)
        collected_tokens.append(token)

    assert len(collected_tokens) > 0
    assert "".join(collected_tokens).strip() != ""


# # 3. max_tokens 限制测试 (流式)
# def test_max_tokens_limit_streaming(bx):
#     """
#     测试流式生成中 max_tokens 参数是否有效限制了总响应长度。
#     """
#     prompt = "Write a very long detailed explanation about quantum physics."
#     max_len = 30 # 设置一个较小的max_tokens以便测试
#     response_generator = bx.product_stream(prompt, max_tokens=max_len)

#     collected_response = ""
#     for token in response_generator:
#         collected_response += token
    
#     # 因为是模拟，可能截断在词中间，所以允许略微超出，但不能显著超出
#     assert len(collected_response) <= max_len + 5 # 允许因为词边界稍微超出一点点

# 5. 空Prompt处理（流式）
@pytest.mark.skip("通过")
def test_empty_prompt_streaming(bx):
    """
    测试流式模型对空Prompt的处理。
    """
    prompt = ""
    response_generator = bx.product_stream(prompt)

    collected_tokens = [token for token in response_generator]
    print(collected_tokens,'collected_tokens')
    assert len(collected_tokens) == 1
    assert collected_tokens[0] == ""



# 9. 性能测试 (流式 - 首个token延迟和总延迟)
def test_streaming_performance(bx):
    """
    测试流式生成的首个token延迟 (Time To First Token - TTFT) 和总生成时间。
    """
    prompt = "Generate a moderate length response to test performance."
    
    start_time = time.perf_counter()
    response_generator = bx.product_stream(prompt)
    
    first_token_received = False
    total_tokens = 0
    
    for i, token in enumerate(response_generator):
        if not first_token_received:
            ttft = time.perf_counter() - start_time
            print(f"\nTTFT: {ttft:.4f} seconds")
            assert ttft < 2 # 首个token应该在0.5秒内（根据模拟的sleep时间调整）
            first_token_received = True
        
        assert isinstance(token, str)
        total_tokens += 1
    
    end_time = time.perf_counter()
    total_duration = end_time - start_time
    print(f"Total duration for {total_tokens} tokens: {total_duration:.4f} seconds")
    
    assert total_tokens > 0
    # 总时间应该在合理范围内，例如，模拟中每个token 0.01-0.05s，加上初始延迟
    assert total_duration < 10.0 # 根据模拟的复杂度和期望响应长度调整

