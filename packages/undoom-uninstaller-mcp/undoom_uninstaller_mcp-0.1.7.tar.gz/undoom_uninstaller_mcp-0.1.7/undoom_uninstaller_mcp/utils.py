"""工具函数模块"""

import os
import shutil
from typing import Optional, Tuple, List
from datetime import datetime


def format_size(size: int) -> str:
    """格式化文件大小
    
    Args:
        size: 文件大小（字节）
        
    Returns:
        格式化后的大小字符串
    """
    if size == 0:
        return "N/A"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    for unit in units:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def get_directory_size(path: str) -> int:
    """获取目录大小（优化版本，避免长时间阻塞）
    
    Args:
        path: 目录路径
        
    Returns:
        目录总大小（字节）
    """
    if not path or not os.path.isdir(path):
        return 0
    
    total_size = 0
    try:
        # 限制扫描深度和文件数量，避免长时间阻塞
        file_count = 0
        max_files = 500   # 最多扫描500个文件
        max_depth = 2     # 最大深度2层
        
        for root, dirs, files in os.walk(path):
            # 计算当前深度
            depth = root[len(path):].count(os.sep)
            if depth >= max_depth:
                dirs[:] = []  # 不再深入子目录
                continue
            
            for filename in files:
                if file_count >= max_files:
                    return total_size  # 达到文件数量限制，返回当前大小
                
                filepath = os.path.join(root, filename)
                try:
                    total_size += os.path.getsize(filepath)
                    file_count += 1
                except (OSError, IOError):
                    continue
                    
    except (OSError, IOError, KeyboardInterrupt):
        pass
    
    return total_size


def safe_remove_directory(path: str) -> Tuple[bool, str]:
    """安全删除目录
    
    Args:
        path: 目录路径
        
    Returns:
        (成功标志, 消息)
    """
    if not path or not os.path.exists(path):
        return True, "路径不存在"
    
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
            return True, f"成功删除目录: {path}"
        else:
            os.remove(path)
            return True, f"成功删除文件: {path}"
    except Exception as e:
        return False, f"删除失败 {path}: {str(e)}"


def format_install_date(date_str: str) -> str:
    """格式化安装日期
    
    Args:
        date_str: 原始日期字符串（YYYYMMDD格式）
        
    Returns:
        格式化后的日期字符串（YYYY-MM-DD格式）
    """
    if not date_str or len(date_str) != 8:
        return "未知"
    
    try:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    except (ValueError, IndexError):
        return "未知"


def get_drive_letter(path: str) -> str:
    """获取路径的盘符
    
    Args:
        path: 文件路径
        
    Returns:
        盘符字符串
    """
    if not path:
        return "未知"
    
    if len(path) >= 2 and path[1] == ':':
        return path[0].upper() + ":"
    elif path.startswith("\\\\"):  # UNC路径
        return "网络路径"
    else:
        return "未知"


def escape_markdown(text: str) -> str:
    """转义Markdown特殊字符
    
    Args:
        text: 原始文本
        
    Returns:
        转义后的文本
    """
    if not text:
        return ""
    return text.replace("|", "\\|")


def truncate_text(text: str, max_length: int) -> str:
    """截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        
    Returns:
        截断后的文本
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def get_common_residue_paths(program_name: str) -> List[str]:
    """获取程序常见残留路径
    
    Args:
        program_name: 程序名称
        
    Returns:
        可能的残留路径列表
    """
    paths = []
    
    env_vars = ["APPDATA", "LOCALAPPDATA", "PROGRAMDATA", "USERPROFILE"]
    
    for env_var in env_vars:
        base_path = os.environ.get(env_var, "")
        if base_path:
            if env_var == "USERPROFILE":
                # 用户目录下的特殊路径
                paths.extend([
                    os.path.join(base_path, "AppData", "Local", program_name),
                    os.path.join(base_path, "AppData", "Roaming", program_name)
                ])
            else:
                paths.append(os.path.join(base_path, program_name))
    
    return paths