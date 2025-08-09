"""程序管理核心模块"""

import os
import winreg
import subprocess
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from .config import REGISTRY_PATHS
from .utils import (
    get_directory_size, 
    format_size, 
    format_install_date, 
    get_drive_letter,
    safe_remove_directory,
    get_common_residue_paths
)


class ProgramInfo:
    """程序信息类"""
    
    def __init__(self, data: Dict[str, any]):
        self.name = data.get("name", "")
        self.publisher = data.get("publisher", "")
        self.version = data.get("version", "")
        self.size = data.get("size", 0)
        self.install_location = data.get("install_location", "")
        self.uninstall_string = data.get("uninstall_string", "")
        self.install_date = data.get("install_date", "未知")
        self.drive_letter = data.get("drive_letter", "未知")
        self.reg_key = data.get("reg_key", "")
        self.hive = data.get("hive", winreg.HKEY_LOCAL_MACHINE)
    
    def to_dict(self) -> Dict[str, any]:
        """转换为字典"""
        return {
            "name": self.name,
            "publisher": self.publisher,
            "version": self.version,
            "size": self.size,
            "install_location": self.install_location,
            "uninstall_string": self.uninstall_string,
            "install_date": self.install_date,
            "drive_letter": self.drive_letter,
            "reg_key": self.reg_key,
            "hive": self.hive
        }


class ProgramManager:
    """程序管理器"""
    
    def __init__(self):
        self.programs: List[ProgramInfo] = []
        self.load_installed_programs()
    
    def load_installed_programs(self) -> None:
        """从注册表加载已安装程序列表"""
        self.programs = []
        
        for hive, path in REGISTRY_PATHS:
            self._load_from_registry_path(hive, path)
        
        # 按名称排序
        self.programs.sort(key=lambda x: x.name.lower())
    
    def _load_from_registry_path(self, hive: int, path: str) -> None:
        """从指定注册表路径加载程序"""
        try:
            with winreg.OpenKey(hive, path) as key:
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        program_info = self._extract_program_info(hive, path, subkey_name)
                        if program_info:
                            self.programs.append(program_info)
                    except (WindowsError, ValueError):
                        continue
        except WindowsError:
            pass
    
    def _extract_program_info(self, hive: int, path: str, subkey_name: str) -> Optional[ProgramInfo]:
        """从注册表子键提取程序信息"""
        try:
            with winreg.OpenKey(winreg.OpenKey(hive, path), subkey_name) as subkey:
                # 获取程序名称
                try:
                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    if not name:
                        return None
                except:
                    return None
                
                # 获取其他信息
                publisher = self._get_registry_value(subkey, "Publisher", "")
                version = self._get_registry_value(subkey, "DisplayVersion", "")
                install_location = self._get_registry_value(subkey, "InstallLocation", "")
                uninstall_string = self._get_registry_value(subkey, "UninstallString", "")
                
                # 处理安装日期
                install_date_raw = self._get_registry_value(subkey, "InstallDate", "")
                install_date = format_install_date(install_date_raw)
                
                # 获取盘符
                drive_letter = get_drive_letter(install_location)
                
                # 获取程序大小
                size = get_directory_size(install_location)
                
                program_data = {
                    "name": name,
                    "publisher": publisher,
                    "version": version,
                    "size": size,
                    "install_location": install_location,
                    "uninstall_string": uninstall_string,
                    "install_date": install_date,
                    "drive_letter": drive_letter,
                    "reg_key": f"{path}\\{subkey_name}",
                    "hive": hive
                }
                
                return ProgramInfo(program_data)
                
        except (WindowsError, ValueError):
            return None
    
    def _get_registry_value(self, key, value_name: str, default: str = "") -> str:
        """安全获取注册表值"""
        try:
            return winreg.QueryValueEx(key, value_name)[0] or default
        except:
            return default
    
    def search_programs(self, query: str) -> List[ProgramInfo]:
        """搜索程序"""
        query = query.lower()
        results = []
        for program in self.programs:
            if (query in program.name.lower() or 
                query in program.publisher.lower()):
                results.append(program)
        return results
    
    def get_program_by_name(self, name: str) -> Optional[ProgramInfo]:
        """根据名称获取程序"""
        for program in self.programs:
            if program.name == name:
                return program
        return None
    
    def uninstall_program(self, program: ProgramInfo) -> Tuple[bool, str]:
        """卸载程序"""
        if not program.uninstall_string:
            return False, "该程序没有找到卸载命令！"
        
        try:
            # 运行卸载命令
            if program.uninstall_string.lower().endswith(".msi"):
                # MSI 包
                cmd = f'msiexec /x "{program.uninstall_string}" /quiet'
            else:
                # 普通卸载程序
                cmd = program.uninstall_string
            
            subprocess.Popen(cmd, shell=True)
            return True, f"正在卸载 {program.name}..."
        except Exception as e:
            return False, f"启动卸载程序失败: {str(e)}"
    
    def force_remove_program(self, program: ProgramInfo) -> Tuple[bool, str]:
        """强制删除程序"""
        errors = []
        
        # 删除安装目录
        if program.install_location and os.path.isdir(program.install_location):
            success, message = safe_remove_directory(program.install_location)
            if not success:
                errors.append(f"删除安装目录失败: {message}")
        
        # 删除注册表项
        try:
            key_parts = program.reg_key.split("\\")
            parent_path = "\\".join(key_parts[:-1])
            subkey_name = key_parts[-1]
            
            with winreg.OpenKey(program.hive, parent_path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.DeleteKey(key, subkey_name)
        except Exception as e:
            errors.append(f"删除注册表项失败: {str(e)}")
        
        if errors:
            return False, "; ".join(errors)
        else:
            return True, f"{program.name} 已被强制删除！"
    
    def clean_residues(self, program: ProgramInfo) -> Tuple[bool, str]:
        """清理程序残留"""
        residue_paths = []
        
        # 检查安装目录
        if program.install_location and os.path.isdir(program.install_location):
            residue_paths.append(program.install_location)
        
        # 检查常见残留位置
        common_paths = get_common_residue_paths(program.name)
        for path in common_paths:
            if os.path.exists(path):
                residue_paths.append(path)
        
        if not residue_paths:
            return True, "该程序没有找到残留文件。"
        
        # 删除残留文件
        errors = []
        deleted = []
        for path in residue_paths:
            success, message = safe_remove_directory(path)
            if success:
                deleted.append(path)
            else:
                errors.append(message)
        
        if errors:
            return False, "; ".join(errors)
        else:
            return True, f"已删除残留文件: {', '.join(deleted)}"
    
    def get_statistics(self) -> Dict[str, any]:
        """获取统计信息"""
        total_programs = len(self.programs)
        
        # 按盘符统计
        drive_stats = {}
        for program in self.programs:
            drive = program.drive_letter
            drive_stats[drive] = drive_stats.get(drive, 0) + 1
        
        # 按发布商统计
        publisher_stats = {}
        for program in self.programs:
            publisher = program.publisher
            if publisher and publisher != "未知":
                publisher_stats[publisher] = publisher_stats.get(publisher, 0) + 1
        
        return {
            "total_programs": total_programs,
            "drive_distribution": drive_stats,
            "publisher_distribution": publisher_stats
        }