#!/bin/bash
# 启动后端服务的脚本

echo "=== ClaudeTask 后端启动脚本 ==="

# 切换到后端目录
cd "$(dirname "$0")"

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "✅ 找到虚拟环境"
    
    # 激活虚拟环境
    echo "📦 激活虚拟环境..."
    source venv/bin/activate
    
    # 检查 Flask 是否安装
    if python -c "import flask" 2>/dev/null; then
        echo "✅ Flask 已安装"
    else
        echo "❌ Flask 未安装，正在安装依赖..."
        pip install -r requirements.txt
    fi
else
    echo "❌ 未找到虚拟环境"
    echo "请先创建虚拟环境："
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# 检查数据库
if [ -f "tasks.db" ]; then
    echo "✅ 数据库文件存在"
else
    echo "⚠️  数据库文件不存在，创建管理员账号..."
    python create_admin.py
fi

# 显示可用账号
echo ""
echo "📋 可用的登录账号："
echo "  管理员: admin@claudetask.local / admin123"
echo "  或运行: python create_admin.py 创建 admin@sparticle.com"
echo ""

# 启动 Flask 应用
echo "🚀 启动 Flask 应用..."
echo "   访问地址: http://localhost:5000"
echo "   按 Ctrl+C 停止服务"
echo ""

# 运行应用
python run.py