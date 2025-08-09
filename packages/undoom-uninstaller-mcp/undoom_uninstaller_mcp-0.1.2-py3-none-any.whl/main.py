import asyncio
import json
import os
import winreg
import subprocess
import shutil
from typing import Any, Sequence
from datetime import datetime

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

server = Server("undoom-uninstaller-mcp")

class UninstallerMCP:
    def __init__(self):
        self.programs = []
        self.load_installed_programs()
    
    def load_installed_programs(self):
        """从注册表加载已安装程序列表"""
        self.programs = []
        
        # 从注册表获取已安装程序
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        
        for hive, path in reg_paths:
            try:
                with winreg.OpenKey(hive, path) as key:
                    for i in range(0, winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    if not name:
                                        continue
                                    
                                    try:
                                        publisher = winreg.QueryValueEx(subkey, "Publisher")[0]
                                    except:
                                        publisher = ""
                                    
                                    try:
                                        version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                    except:
                                        version = ""
                                    
                                    try:
                                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                    except:
                                        install_location = ""
                                    
                                    try:
                                        uninstall_string = winreg.QueryValueEx(subkey, "UninstallString")[0]
                                    except:
                                        uninstall_string = ""
                                    
                                    # 获取安装日期
                                    try:
                                        install_date = winreg.QueryValueEx(subkey, "InstallDate")[0]
                                        if install_date and len(install_date) == 8:
                                            # 格式: YYYYMMDD
                                            install_date_formatted = f"{install_date[:4]}-{install_date[4:6]}-{install_date[6:8]}"
                                        else:
                                            install_date_formatted = "未知"
                                    except:
                                        install_date_formatted = "未知"
                                    
                                    # 获取盘符
                                    drive_letter = "未知"
                                    if install_location:
                                        if len(install_location) >= 2 and install_location[1] == ':':
                                            drive_letter = install_location[0].upper() + ":"
                                        elif install_location.startswith("\\\\"): # UNC路径
                                            drive_letter = "网络路径"
                                    
                                    size = self.get_program_size(install_location)
                                    
                                    program = {
                                        "name": name,
                                        "publisher": publisher,
                                        "version": version,
                                        "size": size,
                                        "install_location": install_location,
                                        "uninstall_string": uninstall_string,
                                        "install_date": install_date_formatted,
                                        "drive_letter": drive_letter,
                                        "reg_key": f"{path}\\{subkey_name}",
                                        "hive": hive
                                    }
                                    
                                    self.programs.append(program)
                                    
                                except (WindowsError, ValueError):
                                    continue
                        except (WindowsError, ValueError):
                            continue
            except WindowsError:
                continue
        
        # 按名称排序
        self.programs.sort(key=lambda x: x["name"].lower())
    
    def get_program_size(self, install_location):
        """获取程序安装大小"""
        if not install_location or not os.path.isdir(install_location):
            return 0
        
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(install_location):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total_size += os.path.getsize(fp)
                except:
                    continue
        return total_size
    
    def format_size(self, size):
        """格式化文件大小"""
        if size == 0:
            return "N/A"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def search_programs(self, query):
        """搜索程序"""
        query = query.lower()
        results = []
        for program in self.programs:
            if (query in program["name"].lower() or 
                query in program["publisher"].lower()):
                results.append(program)
        return results
    
    def get_program_by_name(self, name):
        """根据名称获取程序"""
        for program in self.programs:
            if program["name"] == name:
                return program
        return None
    
    def uninstall_program(self, program):
        """卸载程序"""
        if not program["uninstall_string"]:
            return False, "No uninstall command found for this program!"
        
        try:
            # 运行卸载命令
            if program["uninstall_string"].lower().endswith(".msi"):
                # MSI 包
                cmd = f'msiexec /x "{program["uninstall_string"]}" /quiet'
            else:
                # 普通卸载程序
                cmd = program["uninstall_string"]
            
            subprocess.Popen(cmd, shell=True)
            return True, f"Uninstalling {program['name']}..."
        except Exception as e:
            return False, f"Failed to start uninstaller: {str(e)}"
    
    def force_remove_program(self, program):
        """强制删除程序"""
        errors = []
        
        # 删除安装目录
        if program["install_location"] and os.path.isdir(program["install_location"]):
            try:
                shutil.rmtree(program["install_location"])
            except Exception as e:
                errors.append(f"Failed to delete installation folder: {str(e)}")
        
        # 删除注册表项
        try:
            hive, reg_key = program["hive"], program["reg_key"]
            # 提取子键路径
            key_parts = reg_key.split("\\")
            parent_path = "\\".join(key_parts[:-1])
            subkey_name = key_parts[-1]
            
            with winreg.OpenKey(hive, parent_path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.DeleteKey(key, subkey_name)
        except Exception as e:
            errors.append(f"Failed to delete registry key: {str(e)}")
        
        if errors:
            return False, "; ".join(errors)
        else:
            return True, f"{program['name']} has been force removed!"
    
    def clean_residues(self, program):
        """清理程序残留"""
        residues = []
        
        # 检查安装目录
        if program["install_location"] and os.path.isdir(program["install_location"]):
            residues.append(program["install_location"])
        
        # 检查常见残留位置
        common_locations = [
            os.path.join(os.environ.get("APPDATA", ""), program["name"]),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), program["name"]),
            os.path.join(os.environ.get("PROGRAMDATA", ""), program["name"]),
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", program["name"]),
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Roaming", program["name"])
        ]
        
        for loc in common_locations:
            if os.path.exists(loc):
                residues.append(loc)
        
        if not residues:
            return True, "No residual files found for this program."
        
        # 删除残留文件
        errors = []
        deleted = []
        for residue in residues:
            try:
                if os.path.isdir(residue):
                    shutil.rmtree(residue)
                else:
                    os.remove(residue)
                deleted.append(residue)
            except Exception as e:
                errors.append(f"Failed to delete {residue}: {str(e)}")
        
        if errors:
            return False, "; ".join(errors)
        else:
            return True, f"Deleted residues: {', '.join(deleted)}"
    
    def generate_markdown_table(self, programs, title="系统已安装程序列表"):
        """生成Markdown表格格式的程序列表"""
        if not programs:
            return f"# {title}\n\n暂无程序信息。"
        
        # 表格头部
        markdown = f"# {title}\n\n"
        markdown += "| 程序名称 | 发布商 | 版本 | 大小 | 安装日期 | 盘符 | 安装位置 |\n"
        markdown += "|----------|--------|------|------|----------|------|----------|\n"
        
        # 表格内容
        for program in programs:
            name = program.get("name", "未知").replace("|", "\\|")  # 转义管道符
            publisher = program.get("publisher", "未知").replace("|", "\\|")
            version = program.get("version", "未知").replace("|", "\\|")
            size = self.format_size(program.get("size", 0)).replace("|", "\\|")
            install_date = program.get("install_date", "未知")
            drive_letter = program.get("drive_letter", "未知")
            install_location = program.get("install_location", "未知").replace("|", "\\|")
            
            # 限制单元格内容长度，避免表格过宽
            if len(name) > 30:
                name = name[:27] + "..."
            if len(publisher) > 20:
                publisher = publisher[:17] + "..."
            if len(version) > 15:
                version = version[:12] + "..."
            if len(install_location) > 40:
                install_location = install_location[:37] + "..."
            
            markdown += f"| {name} | {publisher} | {version} | {size} | {install_date} | {drive_letter} | {install_location} |\n"
        
        # 添加统计信息
        markdown += f"\n\n**统计信息：**\n"
        markdown += f"- 总程序数量：{len(programs)}\n"
        
        # 按盘符统计
        drive_stats = {}
        for program in programs:
            drive = program.get("drive_letter", "未知")
            drive_stats[drive] = drive_stats.get(drive, 0) + 1
        
        markdown += f"- 按盘符分布：\n"
        for drive, count in sorted(drive_stats.items()):
            markdown += f"  - {drive}: {count} 个程序\n"
        
        return markdown
    
    def generate_enhanced_markdown_report(self, programs, filename="system_programs_report", include_stats=True):
        """生成增强版Markdown报告并保存到文件"""
        if not programs:
            return False, "没有程序信息可生成报告"
        
        try:
            # 生成报告内容
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            markdown = f"# 系统已安装程序详细报告\n\n"
            markdown += f"**生成时间：** {current_time}\n\n"
            markdown += f"**报告说明：** 本报告包含系统中所有已安装程序的详细信息\n\n"
            
            # 基本统计信息
            if include_stats:
                markdown += "## 📊 统计概览\n\n"
                markdown += f"- **总程序数量：** {len(programs)}\n"
                
                # 按盘符统计
                drive_stats = {}
                for program in programs:
                    drive = program.get("drive_letter", "未知")
                    drive_stats[drive] = drive_stats.get(drive, 0) + 1
                
                markdown += "- **按盘符分布：**\n"
                for drive, count in sorted(drive_stats.items()):
                    percentage = (count / len(programs)) * 100
                    markdown += f"  - {drive}: {count} 个程序 ({percentage:.1f}%)\n"
                
                # 按发布商统计（前10名）
                publisher_stats = {}
                for program in programs:
                    publisher = program.get("publisher", "未知")
                    if publisher and publisher != "未知":
                        publisher_stats[publisher] = publisher_stats.get(publisher, 0) + 1
                
                top_publishers = sorted(publisher_stats.items(), key=lambda x: x[1], reverse=True)[:10]
                if top_publishers:
                    markdown += "- **主要软件发布商（前10名）：**\n"
                    for publisher, count in top_publishers:
                        markdown += f"  - {publisher}: {count} 个程序\n"
                
                markdown += "\n"
            
            # 程序列表表格
            markdown += "## 📋 程序详细列表\n\n"
            markdown += "| 序号 | 程序名称 | 发布商 | 版本 | 大小 | 安装日期 | 盘符 | 安装位置 |\n"
            markdown += "|------|----------|--------|------|------|----------|------|----------|\n"
            
            # 表格内容
            for i, program in enumerate(programs, 1):
                name = program.get("name", "未知").replace("|", "\\|")  # 转义管道符
                publisher = program.get("publisher", "未知").replace("|", "\\|")
                version = program.get("version", "未知").replace("|", "\\|")
                size = self.format_size(program.get("size", 0)).replace("|", "\\|")
                install_date = program.get("install_date", "未知")
                drive_letter = program.get("drive_letter", "未知")
                install_location = program.get("install_location", "未知").replace("|", "\\|")
                
                # 限制单元格内容长度，避免表格过宽
                if len(name) > 35:
                    name = name[:32] + "..."
                if len(publisher) > 25:
                    publisher = publisher[:22] + "..."
                if len(version) > 20:
                    version = version[:17] + "..."
                if len(install_location) > 50:
                    install_location = install_location[:47] + "..."
                
                markdown += f"| {i} | {name} | {publisher} | {version} | {size} | {install_date} | {drive_letter} | {install_location} |\n"
            
            # 添加页脚信息
            markdown += "\n\n---\n\n"
            markdown += "**报告生成工具：** undoom-uninstaller-mcp\n\n"
            markdown += "**注意事项：**\n"
            markdown += "- 本报告仅显示通过Windows注册表检测到的已安装程序\n"
            markdown += "- 某些便携式软件或手动安装的程序可能不会出现在此列表中\n"
            markdown += "- 程序大小信息可能不完全准确，仅供参考\n"
            
            # 保存到文件
            output_path = os.path.join(os.getcwd(), f"{filename}.md")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            return True, f"报告已成功生成并保存到: {output_path}"
            
        except Exception as e:
            return False, f"生成报告失败: {str(e)}"

# 创建卸载器实例
uninstaller = UninstallerMCP()

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """列出可用的工具"""
    return [
        Tool(
            name="list_programs",
            description="列出所有已安装的程序",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "搜索关键词（可选）"
                    }
                }
            }
        ),
        Tool(
            name="get_program_details",
            description="获取指定程序的详细信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "program_name": {
                        "type": "string",
                        "description": "程序名称"
                    }
                },
                "required": ["program_name"]
            }
        ),
        Tool(
            name="uninstall_program",
            description="卸载指定程序",
            inputSchema={
                "type": "object",
                "properties": {
                    "program_name": {
                        "type": "string",
                        "description": "要卸载的程序名称"
                    }
                },
                "required": ["program_name"]
            }
        ),
        Tool(
            name="force_remove_program",
            description="强制删除程序（删除文件和注册表项）",
            inputSchema={
                "type": "object",
                "properties": {
                    "program_name": {
                        "type": "string",
                        "description": "要强制删除的程序名称"
                    }
                },
                "required": ["program_name"]
            }
        ),
        Tool(
            name="clean_residues",
            description="清理程序残留文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "program_name": {
                        "type": "string",
                        "description": "要清理残留的程序名称"
                    }
                },
                "required": ["program_name"]
            }
        ),
        Tool(
            name="refresh_programs",
            description="刷新程序列表",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="show_all_programs_detailed",
            description="显示所有程序的详细信息，包括名称、安装时间和盘符",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "限制返回的程序数量，默认为100",
                        "default": 100
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "排序字段：name（名称）、install_date（安装时间）、drive_letter（盘符）",
                        "enum": ["name", "install_date", "drive_letter"],
                        "default": "name"
                    }
                }
            }
        ),
        Tool(
            name="generate_markdown_report",
            description="生成系统程序信息的Markdown报告文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "输出文件名（不包含扩展名），默认为'system_programs_report'",
                        "default": "system_programs_report"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "限制返回的程序数量，默认为200",
                        "default": 200
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "排序字段：name（名称）、install_date（安装时间）、drive_letter（盘符）",
                        "enum": ["name", "install_date", "drive_letter"],
                        "default": "name"
                    },
                    "include_stats": {
                        "type": "boolean",
                        "description": "是否包含详细统计信息，默认为true",
                        "default": true
                    }
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """处理工具调用"""
    if arguments is None:
        arguments = {}
    
    if name == "list_programs":
        search_query = arguments.get("search", "")
        if search_query:
            programs = uninstaller.search_programs(search_query)
            title = f"搜索结果 - '{search_query}'"
        else:
            programs = uninstaller.programs
            title = "系统已安装程序列表"
        
        # 限制返回数量
        programs = programs[:50]
        
        # 生成Markdown表格
        markdown_table = uninstaller.generate_markdown_table(programs, title)
        
        return [types.TextContent(
            type="text",
            text=markdown_table
        )]
    
    elif name == "get_program_details":
        program_name = arguments.get("program_name")
        if not program_name:
            return [types.TextContent(type="text", text="错误：请提供程序名称")]
        
        program = uninstaller.get_program_by_name(program_name)
        if not program:
            return [types.TextContent(type="text", text=f"错误：未找到程序 '{program_name}'")]
        
        details = {
            "name": program["name"],
            "publisher": program["publisher"],
            "version": program["version"],
            "size": uninstaller.format_size(program["size"]),
            "install_location": program["install_location"],
            "install_date": program["install_date"],
            "drive_letter": program["drive_letter"],
            "uninstall_string": program["uninstall_string"],
            "reg_key": program["reg_key"]
        }
        
        return [types.TextContent(
            type="text",
            text=f"程序详细信息:\n" + json.dumps(details, ensure_ascii=False, indent=2)
        )]
    
    elif name == "uninstall_program":
        program_name = arguments.get("program_name")
        if not program_name:
            return [types.TextContent(type="text", text="错误：请提供程序名称")]
        
        program = uninstaller.get_program_by_name(program_name)
        if not program:
            return [types.TextContent(type="text", text=f"错误：未找到程序 '{program_name}'")]
        
        success, message = uninstaller.uninstall_program(program)
        return [types.TextContent(type="text", text=message)]
    
    elif name == "force_remove_program":
        program_name = arguments.get("program_name")
        if not program_name:
            return [types.TextContent(type="text", text="错误：请提供程序名称")]
        
        program = uninstaller.get_program_by_name(program_name)
        if not program:
            return [types.TextContent(type="text", text=f"错误：未找到程序 '{program_name}'")]
        
        success, message = uninstaller.force_remove_program(program)
        return [types.TextContent(type="text", text=message)]
    
    elif name == "clean_residues":
        program_name = arguments.get("program_name")
        if not program_name:
            return [types.TextContent(type="text", text="错误：请提供程序名称")]
        
        program = uninstaller.get_program_by_name(program_name)
        if not program:
            return [types.TextContent(type="text", text=f"错误：未找到程序 '{program_name}'")]
        
        success, message = uninstaller.clean_residues(program)
        return [types.TextContent(type="text", text=message)]
    
    elif name == "show_all_programs_detailed":
        limit = arguments.get("limit", 100) if arguments else 100
        sort_by = arguments.get("sort_by", "name") if arguments else "name"
        
        programs = uninstaller.programs.copy()
        
        # 排序
        if sort_by == "name":
            programs.sort(key=lambda x: x["name"].lower())
        elif sort_by == "install_date":
            programs.sort(key=lambda x: x["install_date"] or "0000-00-00")
        elif sort_by == "drive_letter":
            programs.sort(key=lambda x: x["drive_letter"])
        
        # 限制数量
        programs = programs[:limit]
        
        # 生成标题
        sort_names = {
            "name": "程序名称",
            "install_date": "安装日期", 
            "drive_letter": "盘符"
        }
        title = f"系统程序详细信息（按{sort_names.get(sort_by, sort_by)}排序）"
        
        # 生成Markdown表格
        markdown_table = uninstaller.generate_markdown_table(programs, title)
        
        return [types.TextContent(
            type="text",
            text=markdown_table
        )]
    
    elif name == "refresh_programs":
        uninstaller.load_installed_programs()
        return [types.TextContent(
            type="text",
            text=f"程序列表已刷新，共加载 {len(uninstaller.programs)} 个程序"
        )]
    
    elif name == "generate_markdown_report":
        filename = arguments.get("filename", "system_programs_report")
        limit = arguments.get("limit", 200)
        sort_by = arguments.get("sort_by", "name")
        include_stats = arguments.get("include_stats", True)
        
        # 获取程序列表
        programs = uninstaller.programs.copy()
        
        # 排序
        if sort_by == "install_date":
            programs.sort(key=lambda x: x.get("install_date", ""))
        elif sort_by == "drive_letter":
            programs.sort(key=lambda x: x.get("drive_letter", ""))
        else:  # 默认按名称排序
            programs.sort(key=lambda x: x.get("name", "").lower())
        
        # 限制数量
        programs = programs[:limit]
        
        # 生成报告
        success, message = uninstaller.generate_enhanced_markdown_report(programs, filename, include_stats)
        return [types.TextContent(type="text", text=message)]
    
    else:
        return [types.TextContent(type="text", text=f"错误：未知工具 '{name}'")]

async def main():
    # Run the server using stdin/stdout streams
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="undoom-uninstaller-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

def cli_main():
    """CLI entry point for the MCP server"""
    asyncio.run(main())

if __name__ == "__main__":
    cli_main()
