# start.ps1
Write-Host ">>> 正在检查环境..." -ForegroundColor Cyan

# 检查 .env 是否存在
if (-not (Test-Path ".env")) {
    Write-Host "错误: 未找到 .env 文件。请先创建并配置 DEEPSEEK_API_KEY。" -ForegroundColor Red
    exit 1
}

Write-Host ">>> 正在同步依赖..." -ForegroundColor Cyan
uv sync

Write-Host ">>> 启动 LangGraph Document Agent..." -ForegroundColor Green
Write-Host ">>> 请在浏览器访问: http://127.0.0.1:8000" -ForegroundColor Yellow

# 启动服务
uv run main.py