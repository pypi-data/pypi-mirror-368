"""配置管理模块"""

import os
from typing import Dict, List, Tuple
import winreg

# 注册表路径配置
REGISTRY_PATHS: List[Tuple[int, str]] = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
]

# 常见残留文件位置
COMMON_RESIDUE_LOCATIONS: List[str] = [
    "APPDATA",
    "LOCALAPPDATA", 
    "PROGRAMDATA"
]

# 文件大小单位
SIZE_UNITS: List[str] = ['B', 'KB', 'MB', 'GB', 'TB']

# 默认配置
DEFAULT_CONFIG: Dict[str, any] = {
    "max_programs_display": 100,
    "default_sort_by": "name",
    "include_stats": True,
    "report_filename": "system_programs_report"
}