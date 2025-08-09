"""报告生成模块"""

import os
from typing import List, Dict
from datetime import datetime

from .program_manager import ProgramInfo
from .utils import format_size, escape_markdown, truncate_text


class ReportGenerator:
    """报告生成器"""
    
    @staticmethod
    def generate_markdown_table(programs: List[ProgramInfo], title: str = "系统已安装程序列表") -> str:
        """生成Markdown表格格式的程序列表"""
        if not programs:
            return f"# {title}\n\n暂无程序信息。"
        
        # 表格头部
        markdown = f"# {title}\n\n"
        markdown += "| 程序名称 | 发布商 | 版本 | 大小 | 安装日期 | 盘符 | 安装位置 |\n"
        markdown += "|----------|--------|------|------|----------|------|----------|\n"
        
        # 表格内容
        for program in programs:
            name = escape_markdown(truncate_text(program.name, 30))
            publisher = escape_markdown(truncate_text(program.publisher, 20))
            version = escape_markdown(truncate_text(program.version, 15))
            size = escape_markdown(format_size(program.size))
            install_date = program.install_date
            drive_letter = program.drive_letter
            install_location = escape_markdown(truncate_text(program.install_location, 40))
            
            markdown += f"| {name} | {publisher} | {version} | {size} | {install_date} | {drive_letter} | {install_location} |\n"
        
        # 添加统计信息
        markdown += f"\n\n**统计信息：**\n"
        markdown += f"- 总程序数量：{len(programs)}\n"
        
        # 按盘符统计
        drive_stats = {}
        for program in programs:
            drive = program.drive_letter
            drive_stats[drive] = drive_stats.get(drive, 0) + 1
        
        markdown += f"- 按盘符分布：\n"
        for drive, count in sorted(drive_stats.items()):
            markdown += f"  - {drive}: {count} 个程序\n"
        
        return markdown
    
    @staticmethod
    def generate_enhanced_markdown_report(
        programs: List[ProgramInfo], 
        filename: str = "system_programs_report", 
        include_stats: bool = True
    ) -> tuple[bool, str]:
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
                markdown += ReportGenerator._generate_statistics_section(programs)
            
            # 程序列表表格
            markdown += "## 📋 程序详细列表\n\n"
            markdown += "| 序号 | 程序名称 | 发布商 | 版本 | 大小 | 安装日期 | 盘符 | 安装位置 |\n"
            markdown += "|------|----------|--------|------|------|----------|------|----------|\n"
            
            # 表格内容
            for i, program in enumerate(programs, 1):
                name = escape_markdown(truncate_text(program.name, 35))
                publisher = escape_markdown(truncate_text(program.publisher, 25))
                version = escape_markdown(truncate_text(program.version, 20))
                size = escape_markdown(format_size(program.size))
                install_date = program.install_date
                drive_letter = program.drive_letter
                install_location = escape_markdown(truncate_text(program.install_location, 50))
                
                markdown += f"| {i} | {name} | {publisher} | {version} | {size} | {install_date} | {drive_letter} | {install_location} |\n"
            
            # 添加页脚信息
            markdown += ReportGenerator._generate_footer_section()
            
            # 保存到文件
            output_path = os.path.join(os.getcwd(), f"{filename}.md")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            return True, f"报告已成功生成并保存到: {output_path}"
            
        except Exception as e:
            return False, f"生成报告失败: {str(e)}"
    
    @staticmethod
    def _generate_statistics_section(programs: List[ProgramInfo]) -> str:
        """生成统计信息部分"""
        markdown = "## 📊 统计概览\n\n"
        markdown += f"- **总程序数量：** {len(programs)}\n"
        
        # 按盘符统计
        drive_stats = {}
        for program in programs:
            drive = program.drive_letter
            drive_stats[drive] = drive_stats.get(drive, 0) + 1
        
        markdown += "- **按盘符分布：**\n"
        for drive, count in sorted(drive_stats.items()):
            percentage = (count / len(programs)) * 100
            markdown += f"  - {drive}: {count} 个程序 ({percentage:.1f}%)\n"
        
        # 按发布商统计（前10名）
        publisher_stats = {}
        for program in programs:
            publisher = program.publisher
            if publisher and publisher != "未知":
                publisher_stats[publisher] = publisher_stats.get(publisher, 0) + 1
        
        top_publishers = sorted(publisher_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        if top_publishers:
            markdown += "- **主要软件发布商（前10名）：**\n"
            for publisher, count in top_publishers:
                markdown += f"  - {publisher}: {count} 个程序\n"
        
        markdown += "\n"
        return markdown
    
    @staticmethod
    def _generate_footer_section() -> str:
        """生成页脚部分"""
        markdown = "\n\n---\n\n"
        markdown += "**报告生成工具：** undoom-uninstaller-mcp\n\n"
        markdown += "**注意事项：**\n"
        markdown += "- 本报告仅显示通过Windows注册表检测到的已安装程序\n"
        markdown += "- 某些便携式软件或手动安装的程序可能不会出现在此列表中\n"
        markdown += "- 程序大小信息可能不完全准确，仅供参考\n"
        return markdown