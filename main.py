# main.py
import os
import shutil
# 新增导入 Form
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from backend.agents import main_agent
from backend.nodes import read_text_from_file

app = FastAPI(title="LangGraph Document Agent")

templates = Jinja2Templates(directory="templates")
os.makedirs("temp", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 修改 endpoint 名称为 /process 显得更通用，并增加 instruction 参数
@app.post("/process")
async def process_document(
    file: UploadFile = File(...),
    instruction: str = Form(...) # 接收前端传来的 instruction 字段
):
    """
    接收文件 + 用户指令 -> 调用 Agent -> 返回结果
    """
    try:
        filename = file.filename
        input_path = os.path.join("temp", filename)
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"--- [API] Received file: {input_path} ---")
        print(f"--- [API] User Instruction: {instruction} ---")

        # --- 关键修改：动态构建 Prompt ---
        # 我们把文件路径和用户的指令结合起来告诉 Agent
        agent_prompt = (
            f"用户上传了一个文件，路径是: {input_path}。\n"
            f"用户的指令是: {instruction}\n"
            "请根据用户的指令，使用合适的工具处理该文件。"
        )

        print("--- [API] Awaiting Agent (Async)... ---")
        
        response = await main_agent.ainvoke({"messages": [("user", agent_prompt)]})
        agent_output = response["messages"][-1].content

        print(f"--- [API] Agent Response: {agent_output} ---")

        # --- 结果获取逻辑 ---
        # Agent 执行完后，我们检查一下是否有对应的 output 文件生成。
        # 目前我们的 Tool 逻辑是写死的生成 "translated_" 开头的文件。
        # 如果用户只是问 "这个文件名叫什么"，可能不会生成文件，所以要容错。
        
        expected_output_path = os.path.join("temp", f"translated_{filename}")
        file_content = ""
        
        if os.path.exists(expected_output_path):
            # 如果生成了翻译文件，就读取出来
            file_content = read_text_from_file(expected_output_path)
        
        return {
            "status": "success",
            "original_filename": filename,
            "agent_response": agent_output,
            "translated_content": file_content # 如果没有生成文件，这里就是空字符串
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
def clear_temp_folder():
    """清空temp文件夹"""
    if os.path.exists("temp"):
        shutil.rmtree("temp")
    os.makedirs("temp", exist_ok=True)

if __name__ == "__main__":
    # 在应用启动时清空temp文件夹
    clear_temp_folder()
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    