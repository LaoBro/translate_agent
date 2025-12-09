# backend/nodes.py
from typing import Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from backend.states import TranslationState
from backend.utils import get_llm
# backend/nodes.py 增加 helper 函数
import os


# --- 配置常量 ---
CHUNK_SIZE = 2000      # 每一块的 Token 数量限制
CHUNK_OVERLAP = 0      # 切分重叠（这里设为0，因为我们有专门的 context_buffer 机制）
CONTEXT_SIZE = 500     # 保留上一段译文的多少字符作为下一段的提示

def init_node(state: TranslationState) -> Dict[str, Any]:
    """
    节点 1: 初始化与切分
    接收原始文本，将其切分为小片段。
    """
    print("--- [Node: Init] Start Splitting ---")
    source_text = state["source_text"]
    
    # 使用 tiktoken 进行精确的 Token 切分，防止 LLM 上下文溢出
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="gpt-4", # 使用通用的 cl100k_base 编码器，DeepSeek 兼容
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    
    chunks = splitter.split_text(source_text)
    print(f"--- [Node: Init] Split into {len(chunks)} chunks ---")
    
    # 返回更新的状态字段
    return {
        "chunks": chunks,
        "current_index": 0,
        "translated_chunks": [],
        "context_buffer": "",
        "final_output": None
    }

def translate_node(state: TranslationState) -> Dict[str, Any]:
    """
    节点 2: 翻译工作者
    读取当前索引的片段，调用 LLM 进行翻译，并更新上下文记忆。
    """
    current_index = state["current_index"]
    chunks = state["chunks"]
    context = state["context_buffer"]
    
    current_text = chunks[current_index]
    
    print(f"--- [Node: Translate] Processing Chunk {current_index + 1}/{len(chunks)} ---")

    # 1. 构建 Prompt
    # 这里的技巧是：将上一段的译文作为 reference 传入，要求 LLM 保持连贯
    system_prompt = (
        "你是一个专业的文档翻译助手。你的任务是将提供的文本准确翻译成中文。\n"
        "你需要保持翻译的连贯性。如果提供了【上文译文摘要】，请参考它来保持语境、人名和专业术语的一致性。\n"
        "直接输出翻译结果，不要包含'好的'、'翻译如下'等废话。"
    )
    
    user_content = f"【待翻译文本】:\n{current_text}\n"
    
    if context:
        user_content = f"【上文译文摘要（仅供参考语境）】:\n...{context}\n\n" + user_content

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_content)
    ])

    # 2. 调用 LLM
    llm = get_llm(temperature=0.3) # 稍微增加一点温度，让行文更流畅，但不要太高
    chain = prompt | llm
    response = chain.invoke({})
    translation = response.content.strip()

    # 3. 更新状态
    # 计算新的上下文 buffer (取本次译文的后 CONTEXT_SIZE 个字符)
    new_buffer = translation[-CONTEXT_SIZE:] if len(translation) > CONTEXT_SIZE else translation
    
    return {
        "translated_chunks": [translation], # LangGraph 会自动根据 Reducer 逻辑处理列表，但这里我们先手动在外部或通过 reducer 追加。
                                            # 注意：在 LangGraph 中，如果 state 类型是 TypedDict，
                                            # 默认行为是覆盖 (Overwrite)。
                                            # 为了简单，我们这里返回更新后的完整列表，或者利用 LangGraph 的 Annotated reducer。
                                            # *修正策略*：为了保持简单，我们在这个函数里手动做 append 操作再返回。
        "context_buffer": new_buffer,
        "current_index": current_index + 1
    }

def merge_node(state: TranslationState) -> Dict[str, Any]:
    """
    节点 3: 合并结果
    """
    print("--- [Node: Merge] Joining results ---")
    # 这里的 translated_chunks 应该是一个列表
    # 注意：在 translate_node 中我们需要处理好列表的追加
    
    full_text = "\n\n".join(state["translated_chunks"])
    
    return {
        "final_output": full_text
    }

def save_text_to_file(text: str, filename: str) -> str:
    """辅助函数：保存文本到 temp 目录"""
    os.makedirs("temp", exist_ok=True)
    filepath = os.path.join("temp", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    return filepath

def read_text_from_file(filepath: str) -> str:
    """辅助函数：读取文本"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()