# backend/utils.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 模块被导入时自动加载环境变量，防止忘记加载
load_dotenv()

def get_llm(temperature: float = 0.1) -> ChatOpenAI:
    """
    获取配置好的 LLM 实例 (默认 DeepSeek)。
    
    Args:
        temperature (float): 温度值，翻译任务建议设置较低 (0.1 - 0.3) 以保证准确性。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL")
    
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY 未在 .env 文件中配置")

    # 使用 LangChain 的 OpenAI 客户端适配 DeepSeek
    llm = ChatOpenAI(
        model="deepseek-chat", 
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        stream_usage=True, # 允许查看 token 使用量
    )
    
    return llm