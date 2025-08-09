"""MCP服务器主模块 - 重构版本"""

import asyncio
import json
from typing import List

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Tool, TextContent
import mcp.types as types

from .program_manager import ProgramManager, ProgramInfo
from .report_generator import ReportGenerator
from .config import DEFAULT_CONFIG
from .utils import format_size

# 创建服务器实例
server = Server("undoom-uninstaller-mcp")

# 创建程序管理器实例
program_manager = ProgramManager()
report_generator = ReportGenerator()


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
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
                        "default": True
                    }
                }
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> List[types.TextContent]:
    """处理工具调用"""
    if arguments is None:
        arguments = {}
    
    try:
        if name == "list_programs":
            return await _handle_list_programs(arguments)
        elif name == "get_program_details":
            return await _handle_get_program_details(arguments)
        elif name == "uninstall_program":
            return await _handle_uninstall_program(arguments)
        elif name == "force_remove_program":
            return await _handle_force_remove_program(arguments)
        elif name == "clean_residues":
            return await _handle_clean_residues(arguments)
        elif name == "refresh_programs":
            return await _handle_refresh_programs(arguments)
        elif name == "show_all_programs_detailed":
            return await _handle_show_all_programs_detailed(arguments)
        elif name == "generate_markdown_report":
            return await _handle_generate_markdown_report(arguments)
        else:
            return [types.TextContent(type="text", text=f"错误：未知工具 '{name}'")]
    
    except Exception as e:
        return [types.TextContent(type="text", text=f"工具执行错误: {str(e)}")]


async def _handle_list_programs(arguments: dict) -> List[types.TextContent]:
    """处理列出程序请求"""
    search_query = arguments.get("search", "")
    
    if search_query:
        programs = program_manager.search_programs(search_query)
        title = f"搜索结果 - '{search_query}'"
    else:
        programs = program_manager.programs
        title = "系统已安装程序列表"
    
    # 限制返回数量
    programs = programs[:50]
    
    # 生成Markdown表格
    markdown_table = report_generator.generate_markdown_table(programs, title)
    
    return [types.TextContent(type="text", text=markdown_table)]


async def _handle_get_program_details(arguments: dict) -> List[types.TextContent]:
    """处理获取程序详情请求"""
    program_name = arguments.get("program_name")
    if not program_name:
        return [types.TextContent(type="text", text="错误：请提供程序名称")]
    
    program = program_manager.get_program_by_name(program_name)
    if not program:
        return [types.TextContent(type="text", text=f"错误：未找到程序 '{program_name}'")]
    
    details = {
        "name": program.name,
        "publisher": program.publisher,
        "version": program.version,
        "size": format_size(program.size),
        "install_location": program.install_location,
        "install_date": program.install_date,
        "drive_letter": program.drive_letter,
        "uninstall_string": program.uninstall_string,
        "reg_key": program.reg_key
    }
    
    return [types.TextContent(
        type="text",
        text=f"程序详细信息:\n" + json.dumps(details, ensure_ascii=False, indent=2)
    )]


async def _handle_uninstall_program(arguments: dict) -> List[types.TextContent]:
    """处理卸载程序请求"""
    program_name = arguments.get("program_name")
    if not program_name:
        return [types.TextContent(type="text", text="错误：请提供程序名称")]
    
    program = program_manager.get_program_by_name(program_name)
    if not program:
        return [types.TextContent(type="text", text=f"错误：未找到程序 '{program_name}'")]
    
    success, message = program_manager.uninstall_program(program)
    return [types.TextContent(type="text", text=message)]


async def _handle_force_remove_program(arguments: dict) -> List[types.TextContent]:
    """处理强制删除程序请求"""
    program_name = arguments.get("program_name")
    if not program_name:
        return [types.TextContent(type="text", text="错误：请提供程序名称")]
    
    program = program_manager.get_program_by_name(program_name)
    if not program:
        return [types.TextContent(type="text", text=f"错误：未找到程序 '{program_name}'")]
    
    success, message = program_manager.force_remove_program(program)
    return [types.TextContent(type="text", text=message)]


async def _handle_clean_residues(arguments: dict) -> List[types.TextContent]:
    """处理清理残留请求"""
    program_name = arguments.get("program_name")
    if not program_name:
        return [types.TextContent(type="text", text="错误：请提供程序名称")]
    
    program = program_manager.get_program_by_name(program_name)
    if not program:
        return [types.TextContent(type="text", text=f"错误：未找到程序 '{program_name}'")]
    
    success, message = program_manager.clean_residues(program)
    return [types.TextContent(type="text", text=message)]


async def _handle_refresh_programs(arguments: dict) -> List[types.TextContent]:
    """处理刷新程序列表请求"""
    program_manager.load_installed_programs()
    return [types.TextContent(
        type="text",
        text=f"程序列表已刷新，共加载 {len(program_manager.programs)} 个程序"
    )]


async def _handle_show_all_programs_detailed(arguments: dict) -> List[types.TextContent]:
    """处理显示详细程序列表请求"""
    limit = arguments.get("limit", DEFAULT_CONFIG["max_programs_display"])
    sort_by = arguments.get("sort_by", DEFAULT_CONFIG["default_sort_by"])
    
    programs = program_manager.programs.copy()
    
    # 排序
    if sort_by == "name":
        programs.sort(key=lambda x: x.name.lower())
    elif sort_by == "install_date":
        programs.sort(key=lambda x: x.install_date or "0000-00-00")
    elif sort_by == "drive_letter":
        programs.sort(key=lambda x: x.drive_letter)
    
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
    markdown_table = report_generator.generate_markdown_table(programs, title)
    
    return [types.TextContent(type="text", text=markdown_table)]


async def _handle_generate_markdown_report(arguments: dict) -> List[types.TextContent]:
    """处理生成Markdown报告请求"""
    filename = arguments.get("filename", DEFAULT_CONFIG["report_filename"])
    limit = arguments.get("limit", 200)
    sort_by = arguments.get("sort_by", DEFAULT_CONFIG["default_sort_by"])
    include_stats = arguments.get("include_stats", DEFAULT_CONFIG["include_stats"])
    
    # 获取程序列表
    programs = program_manager.programs.copy()
    
    # 排序
    if sort_by == "install_date":
        programs.sort(key=lambda x: x.install_date or "")
    elif sort_by == "drive_letter":
        programs.sort(key=lambda x: x.drive_letter or "")
    else:  # 默认按名称排序
        programs.sort(key=lambda x: x.name.lower())
    
    # 限制数量
    programs = programs[:limit]
    
    # 生成报告
    success, message = report_generator.generate_enhanced_markdown_report(programs, filename, include_stats)
    return [types.TextContent(type="text", text=message)]


async def main():
    """主函数 - 运行MCP服务器"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="undoom-uninstaller-mcp",
                server_version="0.1.3",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def cli_main():
    """CLI入口点"""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()