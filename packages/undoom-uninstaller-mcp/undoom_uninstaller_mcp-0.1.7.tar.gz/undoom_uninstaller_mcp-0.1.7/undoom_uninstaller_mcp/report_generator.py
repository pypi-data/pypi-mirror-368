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
        """生成美化的Markdown格式程序列表"""
        if not programs:
            return f"# 📋 {title}\n\n> 暂无程序信息。"
        
        # 美化的标题和概览
        markdown = f"# 📋 {title}\n\n"
        markdown += f"> 🔍 **发现 {len(programs)} 个已安装程序**\n\n"
        
        # 快速统计概览
        drive_stats = {}
        publisher_stats = {}
        total_size = 0
        
        for program in programs:
            drive = program.drive_letter
            drive_stats[drive] = drive_stats.get(drive, 0) + 1
            
            if program.publisher and program.publisher != "未知":
                publisher_stats[program.publisher] = publisher_stats.get(program.publisher, 0) + 1
            
            if program.size > 0:
                total_size += program.size
        
        # 统计信息卡片
        markdown += "## 📊 快速概览\n\n"
        markdown += "| 📈 统计项目 | 📊 数值 | 💾 详情 |\n"
        markdown += "|------------|--------|--------|\n"
        markdown += f"| **总程序数** | `{len(programs)}` | 系统中检测到的程序总数 |\n"
        markdown += f"| **总占用空间** | `{format_size(total_size)}` | 已计算程序的总大小 |\n"
        markdown += f"| **主要盘符** | `{max(drive_stats.items(), key=lambda x: x[1])[0] if drive_stats else '未知'} ({max(drive_stats.values()) if drive_stats else 0}个)` | 程序最多的安装盘符 |\n"
        
        top_publisher = max(publisher_stats.items(), key=lambda x: x[1]) if publisher_stats else ("未知", 0)
        markdown += f"| **主要发布商** | `{top_publisher[0][:20]}` | {top_publisher[1]}个程序 |\n\n"
        
        # 盘符分布可视化
        if drive_stats:
            markdown += "### 💿 盘符分布\n\n"
            for drive, count in sorted(drive_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(programs)) * 100
                bar_length = int(percentage / 5)  # 每5%一个方块
                bar = "█" * bar_length + "░" * (20 - bar_length)
                markdown += f"**{drive}** `{count:3d}个` {bar} `{percentage:5.1f}%`\n\n"
        
        # 程序详细列表
        markdown += "## 📦 程序详细列表\n\n"
        
        # 按类别分组显示
        categories = {
            "🛠️ 开发工具": [],
            "🌐 浏览器与网络": [],
            "🎮 游戏娱乐": [],
            "🔧 系统组件": [],
            "📱 移动开发": [],
            "☁️ 云服务工具": [],
            "📊 其他应用": []
        }
        
        for program in programs:
            name_lower = program.name.lower()
            publisher_lower = program.publisher.lower()
            
            if any(keyword in name_lower for keyword in ['studio', 'ide', 'clion', 'intellij', 'git', 'jdk', 'java', 'cursor', 'codebuddy']):
                categories["🛠️ 开发工具"].append(program)
            elif any(keyword in name_lower for keyword in ['chrome', 'browser', 'firefox', 'edge']):
                categories["🌐 浏览器与网络"].append(program)
            elif any(keyword in name_lower for keyword in ['game', 'steam', 'epic', 'dead cells']):
                categories["🎮 游戏娱乐"].append(program)
            elif any(keyword in publisher_lower for keyword in ['microsoft', 'intel']) and 'visual studio' not in name_lower:
                categories["🔧 系统组件"].append(program)
            elif any(keyword in name_lower for keyword in ['android', 'maui', 'deveco', 'huawei']):
                categories["📱 移动开发"].append(program)
            elif any(keyword in name_lower for keyword in ['ai', 'copilot', 'figma', 'apifox', 'apipost']):
                categories["☁️ 云服务工具"].append(program)
            else:
                categories["📊 其他应用"].append(program)
        
        # 显示各类别
        for category, progs in categories.items():
            if progs:
                markdown += f"### {category} ({len(progs)}个)\n\n"
                markdown += "| 🏷️ 程序名称 | 🏢 发布商 | 📋 版本 | 💾 大小 | 📅 安装日期 | 💿 盘符 |\n"
                markdown += "|------------|---------|-------|-------|----------|------|\n"
                
                for program in progs:
                    name = escape_markdown(truncate_text(program.name, 25))
                    publisher = escape_markdown(truncate_text(program.publisher, 18))
                    version = escape_markdown(truncate_text(program.version, 12))
                    size = escape_markdown(format_size(program.size))
                    install_date = program.install_date if program.install_date != "未知" else "❓"
                    drive_letter = program.drive_letter
                    
                    # 添加状态图标
                    size_icon = "💾" if program.size > 100*1024*1024 else "📦" if program.size > 0 else "❓"
                    
                    markdown += f"| **{name}** | {publisher} | `{version}` | {size_icon} {size} | {install_date} | **{drive_letter}** |\n"
                
                markdown += "\n"
        
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