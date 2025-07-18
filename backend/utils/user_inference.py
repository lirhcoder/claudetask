"""
从项目路径推断用户信息的工具函数
"""
import re
from typing import Optional, Tuple

def infer_user_from_project_path(project_path: str) -> Optional[Tuple[str, Optional[str]]]:
    """
    从项目路径推断用户信息
    返回: (用户标识, 可能的域名) 或 None
    
    例如:
    - /path/to/rh-li-0718-001 -> ('rh.li', None)
    - /path/to/john.doe@company.com/project -> ('john.doe@company.com', 'company.com')
    - C:\\Users\\john.doe\\projects\\test -> ('john.doe', None)
    """
    
    # 标准化路径分隔符
    normalized_path = project_path.replace('\\', '/')
    
    # 模式1: 直接包含邮箱地址
    email_pattern = r'([\w\.-]+@[\w\.-]+\.\w+)'
    email_match = re.search(email_pattern, normalized_path)
    if email_match:
        email = email_match.group(1)
        domain = email.split('@')[1]
        return (email, domain)
    
    # 模式2: Windows用户路径 (C:\Users\username\...)
    windows_user_pattern = r'/Users/([^/]+)/'
    windows_match = re.search(windows_user_pattern, normalized_path)
    if windows_match:
        username = windows_match.group(1)
        # 清理Windows用户名中的空格和特殊字符
        username = username.lower().replace(' ', '.')
        return (username, None)
    
    # 模式3: 项目名称格式 (xx-yy-date-number)
    path_parts = normalized_path.split('/')
    for part in path_parts:
        # 匹配 firstname-lastname-数字-数字 格式
        project_pattern = r'^([a-zA-Z]+)-([a-zA-Z]+)-\d{4}-\d+'
        match = re.match(project_pattern, part)
        if match:
            first = match.group(1).lower()
            last = match.group(2).lower()
            # 构造可能的邮箱用户名
            username = f"{first}.{last}"
            return (username, None)
        
        # 匹配 firstname.lastname 格式
        name_pattern = r'^([a-zA-Z]+)\.([a-zA-Z]+)$'
        match = re.match(name_pattern, part)
        if match:
            return (part.lower(), None)
    
    # 模式4: 包含用户名的其他格式
    # 查找路径中可能的用户名 (至少3个字符的字母组合)
    username_pattern = r'/([a-zA-Z]{3,}(?:[.-][a-zA-Z]+)*?)/'
    matches = re.findall(username_pattern, normalized_path)
    for match in matches:
        # 跳过常见的系统目录名
        if match.lower() not in ['home', 'users', 'documents', 'projects', 'development', 'work', 'code', 'src']:
            return (match.lower(), None)
    
    return None


def get_domain_from_config() -> str:
    """获取系统配置的默认域名"""
    try:
        from models.user import UserManager
        user_manager = UserManager()
        config = user_manager.get_system_config()
        if config.allowed_email_domain:
            domain = config.allowed_email_domain
            if not domain.startswith('@'):
                domain = '@' + domain
            return domain
    except:
        pass
    return '@sparticle.com'  # 默认域名


def construct_email(username: str, domain: Optional[str] = None) -> str:
    """构造完整的邮箱地址"""
    if '@' in username:
        return username
    
    if not domain:
        domain = get_domain_from_config()
    
    if domain.startswith('@'):
        domain = domain[1:]
    
    return f"{username}@{domain}"