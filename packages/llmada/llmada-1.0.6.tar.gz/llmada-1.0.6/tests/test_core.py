import sys
import os
from dotenv import load_dotenv
import pytest
from llmada import BianXieAdapter, KimiAdapter, ArkAdapter, GoogleAdapter


load_dotenv()





@pytest.fixture(scope="module")
def llm_instance():
    """
    如果你的LLM需要实例化或加载，可以在这里完成。
    例如：model = LLMClass(config_path="config.yaml")
    return model
    """
    print("\n--- Setting up LLM instance for testing ---")
    yield my_awesome_llm # 返回函数本身
    print("--- Tearing down LLM instance ---")











class Test_Bianxie:
    @pytest.fixture
    def bianxie(self):
        return BianXieAdapter()

    # @pytest.mark.skip("通过")
    @pytest.mark.base
    def test_get_model(self,bianxie):
        print(bianxie.get_model())

    # @pytest.mark.skip("通过")
    @pytest.mark.base
    def test_get_modal_model(self,bianxie):
        print(bianxie.get_modal_model())

    # @pytest.mark.skip("通过")
    @pytest.mark.function
    def test_product(self,bianxie):
        bianxie.set_model('gpt-4o')
        result = bianxie.product(prompt='你好')
        assert type(result) == str

    def test_product_modal(self,bianxie):
        pass

    @pytest.mark.skip("通过")
    def test_product_stream(self,bianxie):
        rus = bianxie.product_stream(prompt='你好')
        for i in rus:
            print(i)
            assert type(i) == str
        
    @pytest.mark.skip("未通过")
    def test_chat(self,bianxie):
        result = bianxie.chat(messages=[{'role': 'user', 'content': '你好'}])
        print(result)
        assert type(result) == str

    def test_chat_modal(self,bianxie):
        pass

    @pytest.mark.skip("通过")
    def test_chat_stream(self,bianxie):
        rus = bianxie.chat_stream(messages=[{'role': 'user', 'content': '你好'}])
        for i in rus:
            print(i)
            assert type(i) == str


class Test_Kimi:

    @pytest.fixture
    def kimi(self):
        return KimiAdapter()

    @pytest.mark.skip("通过")
    def test_product(self,kimi):
        result = kimi.product(prompt='你好')
        print(result)
        assert type(result) == str

    @pytest.mark.skip("通过")
    def test_chat(self,kimi):
        result = kimi.chat(messages=[{'role': 'user', 'content': '你好'}])
        print(result)
        assert type(result) == str


class Test_Ark:

    @pytest.fixture
    def ark(self):
        return ArkAdapter()

    @pytest.mark.skip("通过")
    def test_product(self,ark):
        result = ark.product(prompt='你好')
        print(result)
        assert type(result) == str

    @pytest.mark.skip("通过")
    def test_chat(self,ark):
        result = ark.chat(messages=[{'role': 'user', 'content': '你好'}])
        print(result)
        assert type(result) == str


class Test_GoogleAdapter:

    @pytest.fixture
    def google(self):
        return GoogleAdapter()

    @pytest.mark.skip("通过")
    def test_product(self,google):
        result = google.product(prompt='你好')
        print(result)
        assert type(result) == str

    @pytest.mark.skip("通过")
    def test_chat(self,google):
        result = google.chat(messages=[{'role': 'user', 'content': '你好'}])
        print(result)
        assert type(result) == str

