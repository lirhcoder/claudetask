"""
本地执行结果上传器
"""
import json
import requests
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ResultUploader:
    """上传本地执行结果到服务器"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.api_endpoint = f"{self.base_url}/api/tasks/{{task_id}}/local-result"
    
    def upload_result(self, task_id: str, result_file: Path) -> bool:
        """上传执行结果"""
        try:
            # 读取结果文件
            if not result_file.exists():
                logger.error(f"结果文件不存在: {result_file}")
                return False
            
            with open(result_file, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            
            # 发送到服务器
            url = self.api_endpoint.format(task_id=task_id)
            response = requests.post(url, json=result_data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"成功上传任务 {task_id} 的执行结果")
                return True
            else:
                logger.error(f"上传失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"上传执行结果时出错: {e}")
            return False
    
    def create_result_file(self, task_id: str, output_file: Path, 
                          exit_code: int, duration: float,
                          interrupted: bool = False) -> Path:
        """创建结果文件"""
        result_data = {
            'task_id': task_id,
            'completed_at': datetime.now().isoformat(),
            'exit_code': exit_code,
            'duration': duration,
            'interrupted': interrupted,
            'status': 'cancelled' if interrupted else ('completed' if exit_code == 0 else 'failed')
        }
        
        # 读取输出内容
        if output_file.exists():
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    result_data['output'] = f.read()
            except:
                result_data['output'] = "无法读取输出文件"
        
        # 保存结果文件
        result_file = output_file.parent / f"{task_id}_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        return result_file

def upload_task_result(task_id: str, output_file: Path, 
                      exit_code: int, duration: float,
                      interrupted: bool = False,
                      base_url: str = "http://localhost:5000") -> bool:
    """便捷函数：创建并上传任务结果"""
    uploader = ResultUploader(base_url)
    
    # 创建结果文件
    result_file = uploader.create_result_file(
        task_id, output_file, exit_code, duration, interrupted
    )
    
    # 上传结果
    success = uploader.upload_result(task_id, result_file)
    
    # 清理结果文件
    try:
        result_file.unlink()
    except:
        pass
    
    return success