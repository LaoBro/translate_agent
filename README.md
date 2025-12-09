# Translate Agent 

这是一个基于 **LangGraph** 和 **LangChain** 的智能文档处理 Agent。并采用易于扩展的的 Multi-Agent 架构，能够根据用户的自然语言指令，自主调用工具处理长文档（目前只实现了 TXT 文件翻译）。

## 技术栈

*   **编排**: LangGraph, LangChain
*   **LLM**: DeepSeek (兼容 OpenAI 协议)
*   **后端**: FastAPI, Uvicorn
*   **前端**: HTML5, JavaScript, Jinja2
*   **工具**: TikToken (Token 计算), Python-Multipart

## 快速开始

### 1. 环境准备

确保你已经安装了 [uv](https://github.com/astral-sh/uv)。

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd langgraph-translator

# 2. 配置环境变量
# 复制 .env.example (如果有) 或者直接创建 .env
touch .env
```

在 `.env` 文件中填入你的 API Key：
```ini
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 2. 安装依赖

项目使用 `uv` 管理，无需手动激活虚拟环境，`uv run` 会自动处理。

```bash
uv sync
```

### 3. 启动服务

使用提供的启动脚本一键运行：

**Windows:**
```powershell
.\start.ps1
```

**Linux / macOS:**
```bash
chmod +x start.sh
./start.sh
```

或者手动运行：
```bash
uv run main.py
```

### 4. 使用

1.  打开浏览器访问 `http://127.0.0.1:8000`。
2.  点击 **" 点击选择 TXT 文档"** 上传一个文件。
3.  在输入框中输入指令，例如：`请帮我把这个文件翻译成中文`。
4.  点击 **"发送指令"**，等待 Agent 处理完成。

## 文件结构

```text
.
├── backend/
│   ├── agents.py     # 图编排：定义 Main Agent 和 Sub-Graph
│   ├── nodes.py      # 节点逻辑：切分、翻译、合并
│   ├── states.py     # 数据结构：定义 State Schema
│   └── utils.py      # 工具库：LLM 初始化
├── templates/
│   └── index.html    # 前端界面
├── temp/             # 临时文件存储 (自动生成)
├── main.py           # FastAPI 入口
├── pyproject.toml    # 依赖配置
└── README.md         # 说明文档
```

## 未实现的功能

- [ ] 支持 PDF、Word 文档解析。
- [ ] 添加 "文档总结" 工具 (Summary Tool)。
- [ ] 优化前端，支持流式输出 (Streaming)。
- [ ] 支持更多 LLM 模型切换。
