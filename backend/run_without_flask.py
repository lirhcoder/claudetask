#!/usr/bin/env python3
"""
在没有 Flask 的情况下运行一个简单的 HTTP 服务器
"""
import json
import sqlite3
import bcrypt
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleAPIHandler(BaseHTTPRequestHandler):
    """简单的 API 处理器"""
    
    def do_OPTIONS(self):
        """处理 CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()
    
    def do_POST(self):
        """处理 POST 请求"""
        if self.path == '/api/auth/login':
            self.handle_login()
        else:
            self.send_error(404, 'Not Found')
    
    def handle_login(self):
        """处理登录请求"""
        try:
            # 读取请求体
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            logger.info(f"Login attempt for: {email}")
            
            # 连接数据库
            conn = sqlite3.connect('tasks.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查找用户
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user_row = cursor.fetchone()
            
            if user_row:
                # 验证密码
                stored_password = user_row['password_hash'].encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    # 登录成功
                    response_data = {
                        'message': '登录成功',
                        'user': {
                            'id': user_row['id'],
                            'email': user_row['email'],
                            'username': user_row['username'],
                            'is_admin': bool(user_row['is_admin'])
                        }
                    }
                    self.send_json_response(200, response_data)
                    logger.info(f"Login successful for: {email}")
                else:
                    self.send_json_response(401, {'error': '邮箱或密码错误'})
                    logger.warning(f"Invalid password for: {email}")
            else:
                self.send_json_response(401, {'error': '邮箱或密码错误'})
                logger.warning(f"User not found: {email}")
                
            conn.close()
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            self.send_json_response(500, {'error': f'服务器错误: {str(e)}'})
    
    def send_json_response(self, status_code, data):
        """发送 JSON 响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

def check_database():
    """检查数据库和用户"""
    try:
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        # 检查 users 表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            logger.error("users 表不存在！")
            return False
        
        # 检查是否有用户
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        logger.info(f"数据库中有 {user_count} 个用户")
        
        # 列出所有用户
        cursor.execute("SELECT email, is_admin FROM users")
        for row in cursor.fetchall():
            logger.info(f"  - {row[0]} (管理员: {'是' if row[1] else '否'})")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"数据库检查失败: {e}")
        return False

def run_server(port=5000):
    """运行服务器"""
    logger.info("=== 简单 API 服务器 ===")
    logger.info(f"监听端口: {port}")
    logger.info("这是一个临时解决方案，用于处理 Flask 未安装的情况")
    
    # 检查数据库
    if not check_database():
        logger.error("数据库检查失败，请确保已运行 create_admin.py")
        return
    
    # 启动服务器
    server = HTTPServer(('localhost', port), SimpleAPIHandler)
    logger.info(f"服务器已启动: http://localhost:{port}")
    logger.info("按 Ctrl+C 停止服务器")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n服务器已停止")

if __name__ == '__main__':
    run_server()