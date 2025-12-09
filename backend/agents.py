# backend/agents.py
from typing import Literal
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langchain.agents import create_agent
from backend.states import TranslationState
from backend.nodes import init_node, translate_node, merge_node, read_text_from_file, save_text_to_file
from backend.utils import get_llm
import os

# ==========================================
# Part 1: 原有的翻译子图逻辑
# ==========================================

def should_continue(state: TranslationState) -> Literal["translate_node", "merge_node"]:
    if state["current_index"] < len(state["chunks"]):
        return "translate_node"
    return "merge_node"

def build_translation_graph():
    workflow = StateGraph(TranslationState)
    workflow.add_node("init_node", init_node)
    workflow.add_node("translate_node", translate_node)
    workflow.add_node("merge_node", merge_node)
    
    workflow.add_edge(START, "init_node")
    workflow.add_edge("init_node", "translate_node")
    workflow.add_conditional_edges("translate_node", should_continue)
    workflow.add_edge("merge_node", END)
    
    return workflow.compile()

# 编译子图实例
translation_app = build_translation_graph()


# ==========================================
# Part 2: 封装为 Tool (隔绝上下文)
# ==========================================

@tool
def document_translator_tool(file_path: str) -> str:
    """
    专门用于翻译长文档的工具。
    输入：源文件的路径 (file_path)。
    输出：翻译结果文件的路径。
    
    注意：此工具会自动读取文件内容，进行分段翻译，最后保存结果。
    """
    try:
        print(f"--- [Tool] Called with file: {file_path} ---")
        
        # 1. 即使主 Agent 不看全文，工具内部需要看
        source_text = read_text_from_file(file_path)
        
        # 2. 调用翻译子图
        initial_state = {
            "source_text": source_text,
            "chunks": [],
            "current_index": 0,
            "translated_chunks": [],
            "context_buffer": "",
            "final_output": None
        }
        
        # 运行子图
        result_state = translation_app.invoke(initial_state)
        final_text = result_state["final_output"]
        
        # 3. 保存结果到新文件
        output_filename = f"translated_{os.path.basename(file_path)}"
        output_path = save_text_to_file(final_text, output_filename)
        
        return f"翻译成功！结果已保存至: {output_path}"
        
    except Exception as e:
        return f"翻译过程中出错: {str(e)}"


# ==========================================
# Part 3: 主控 Agent (Supervisor)
# ==========================================

def get_main_agent():
    """
    创建主控 ReAct Agent。
    它只能看到工具的描述和返回值（文件路径），看不到文件全文。
    """
    llm = get_llm(temperature=0) # 主控需要精确决策
    
    tools = [document_translator_tool]
    
    system_prompt = (
        "你是一个智能文档处理助手。你的目标是帮助用户处理文件任务。\n"
        "你可以使用工具来完成任务。请注意：\n"
        "1. 用户会给你一个文件路径。\n"
        "2. 不要试图直接读取文件内容，因为文件可能非常大。\n"
        "3. 如果用户要求翻译，请使用 document_translator_tool。\n"
        "4. 任务完成后，告诉用户结果文件的位置。"
    )
    
    # LangGraph 提供的预构建 ReAct Agent
    agent = create_agent(model=llm, tools=tools, system_prompt=system_prompt)
    
    return agent

# 实例化主 Agent
main_agent = get_main_agent()