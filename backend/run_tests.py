#!/usr/bin/env python3
"""
运行所有测试并生成报告
"""
import os
import sys
import subprocess
from datetime import datetime


def main():
    """主函数"""
    print("=" * 80)
    print(f"运行单元测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 设置环境变量
    os.environ['TESTING'] = '1'
    os.environ['DATABASE_PATH'] = ':memory:'  # 使用内存数据库进行测试
    
    # 切换到 backend 目录
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # 确保在 Python 路径中
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    # 运行 pytest
    test_args = [
        'pytest',
        'tests/',
        '-v',  # 详细输出
        '--tb=short',  # 简短的错误追踪
        '--cov=.',  # 代码覆盖率
        '--cov-report=term-missing',  # 显示未覆盖的行
        '--cov-report=html',  # 生成 HTML 报告
        '--durations=10',  # 显示最慢的 10 个测试
    ]
    
    print(f"\n执行命令: {' '.join(test_args)}")
    print("-" * 80)
    
    try:
        result = subprocess.run(test_args, capture_output=False)
        
        if result.returncode == 0:
            print("\n" + "=" * 80)
            print("✅ 所有测试通过！")
            print("=" * 80)
            print("\n📊 测试报告:")
            print("- 覆盖率报告: htmlcov/index.html")
            print("- 在浏览器中打开查看详细的代码覆盖情况")
        else:
            print("\n" + "=" * 80)
            print("❌ 测试失败！")
            print("=" * 80)
            print("\n请检查上面的错误信息并修复问题。")
            
        return result.returncode
        
    except FileNotFoundError:
        print("\n❌ 错误: 未找到 pytest")
        print("请安装 pytest: pip install pytest pytest-cov")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())