#!/bin/bash

echo -e "\033[36m>>> 正在检查环境...\033[0m"

# 检查 .env 是否存在
if [ ! -f ".env" ]; then
    echo -e "\033[31m错误: 未找到 .env 文件。请先创建并配置 DEEPSEEK_API_KEY。\033[0m"
    exit 1
fi

echo -e "\033[36m>>> 正在同步依赖...\033[0m"
uv sync

echo -e "\033[32m>>> 启动 LangGraph Document Agent...\033[0m"
echo -e "\033[33m>>> 请在浏览器访问: http://127.0.0.1:8000\033[0m"

# 启动服务
uv run main.py