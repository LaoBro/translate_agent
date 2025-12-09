# backend/states.py
from typing import List, Optional,Annotated
from typing_extensions import TypedDict
import operator

class TranslationState(TypedDict):
    """
    定义翻译工作流的状态字典。
    LangGraph 会在节点之间传递这个字典，节点可以读取并更新它。
    """
    
    # --- 输入 ---
    source_text: str                # 用户上传的原始完整文本
    
    # --- 中间处理状态 ---
    chunks: List[str]               # 经切分后的原文片段列表
    current_index: int              # 循环计数器：当前正在处理第几个片段
    # --- 关键修改 ---
    # Annotated[List[str], operator.add] 告诉 LangGraph：
    # 当节点返回这个字段时，把它加到旧列表后面，而不是覆盖。
    translated_chunks: Annotated[List[str], operator.add]
    context_buffer: str             # "历史记忆"：存储上一段译文的末尾，用于下一段的上下文提示
    
    # --- 输出 ---
    final_output: Optional[str]     # 最终合并后的完整译文