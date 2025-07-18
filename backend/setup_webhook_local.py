#!/usr/bin/env python3
"""
本地 Webhook 配置助手
"""
import os
import sys
import subprocess
import webbrowser
import time

def check_ngrok():
    """检查 ngrok 是否安装"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ ngrok 已安装: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ ngrok 未安装")
    print("\n请先安装 ngrok:")
    print("1. 访问 https://ngrok.com/download")
    print("2. 下载并解压")
    print("3. 将 ngrok.exe 添加到 PATH")
    print("\n或使用 Chocolatey: choco install ngrok")
    return False

def start_ngrok(port=5000):
    """启动 ngrok 隧道"""
    print(f"\n正在启动 ngrok 隧道 (端口 {port})...")
    
    # 在新窗口中启动 ngrok
    if sys.platform == 'win32':
        subprocess.Popen(['start', 'cmd', '/k', 'ngrok', 'http', str(port)], shell=True)
    else:
        subprocess.Popen(['gnome-terminal', '--', 'ngrok', 'http', str(port)])
    
    print("⏳ 等待 ngrok 启动...")
    time.sleep(3)
    
    # 打开 ngrok 管理界面
    print("\n📊 打开 ngrok 管理界面: http://localhost:4040")
    webbrowser.open('http://localhost:4040')
    
    print("\n✅ ngrok 已启动！")
    print("\n请在 ngrok 窗口中查找你的公网 URL，格式如：")
    print("   https://abc123.ngrok-free.app")
    
    return True

def show_webhook_config():
    """显示 webhook 配置说明"""
    print("\n" + "="*60)
    print("📝 Webhook 配置步骤")
    print("="*60)
    
    print("\n1. 从 ngrok 窗口复制 HTTPS URL (如: https://abc123.ngrok-free.app)")
    
    print("\n2. Webhook URL 格式:")
    print("   https://你的ngrok域名.ngrok-free.app/api/webhooks/github")
    
    print("\n3. 在 GitHub 仓库设置中:")
    print("   - Payload URL: 上面的 webhook URL")
    print("   - Content type: application/json")
    print("   - Secret: 你的 webhook 密钥")
    print("   - Events: 选择需要的事件")
    
    print("\n4. 在 ClaudeTask 设置中:")
    print("   - GitHub Webhook 密钥: 与 GitHub 相同的密钥")
    
    print("\n5. 设置环境变量 (可选):")
    print("   Windows CMD:")
    print("     set GITHUB_WEBHOOK_SECRET=your-secret-key")
    print("   Windows PowerShell:")
    print("     $env:GITHUB_WEBHOOK_SECRET=\"your-secret-key\"")

def main():
    print("🚀 ClaudeTask 本地 Webhook 配置助手")
    print("="*60)
    
    # 检查 ngrok
    if not check_ngrok():
        return
    
    # 询问是否启动 ngrok
    response = input("\n是否启动 ngrok 隧道？(y/n): ")
    if response.lower() == 'y':
        # 询问端口
        port_input = input("Flask 服务端口 (默认 5000): ").strip()
        port = int(port_input) if port_input else 5000
        
        if start_ngrok(port):
            show_webhook_config()
            
            print("\n💡 提示:")
            print("- ngrok 免费版 URL 会在重启后改变")
            print("- 每次重启 ngrok 需要更新 GitHub webhook URL")
            print("- 可以注册 ngrok 账号获得更稳定的服务")
    else:
        print("\n手动启动 ngrok:")
        print("  ngrok http 5000")
        show_webhook_config()
    
    print("\n✨ 配置完成后，你可以:")
    print("1. 在 GitHub 上触发事件（如 push）")
    print("2. 在 ngrok 管理界面查看请求")
    print("3. 在 ClaudeTask 后端查看日志")

if __name__ == '__main__':
    main()