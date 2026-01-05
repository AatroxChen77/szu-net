# cli.py
import time
import sys
from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.table import Table
from rich import print as rprint

# 引入原来的主程序逻辑
from main import run_daemon
from app.config import settings

console = Console()

def print_banner():
    """打印炫酷的横幅"""
    # 使用反斜杠转义，防止被认为是转义字符
    banner_text = """
   _____ ______  _   _    _   _ ______ _______ 
  / ____|___  / | | | |  | \ | |  ____|__   __|
 | (___    / /  | | | |  |  \| | |__     | |   
  \___ \  / /   | | | |  | . ` |  __|    | |   
  ____) |/ /__  | |_| |  | |\  | |____   | |   
 |_____//_____|  \___/   |_| \_|______|  |_|   
                                               
    [bold cyan]SZU Network Guardian[/bold cyan] | [yellow]Dual-Zone Edition v3.0[/yellow]
    """
    
    # 创建一个包含信息的表格
    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="right")
    
    # 获取当前配置信息
    zone_color = "magenta" if settings.NETWORK_ZONE == 'dorm' else "blue"
    
    grid.add_row(
        "[bold green]✅ System Online[/bold green]",
        f"[dim]Mode:[/dim] [{zone_color}]{settings.NETWORK_ZONE.upper()}[/{zone_color}]"
    )
    grid.add_row(
        "[bold green]✅ Config Loaded[/bold green]",
        f"[dim]User:[/dim] [cyan]{settings.SRUN_USERNAME}[/cyan]"
    )

    # 关键修改：使用 Group 将 Banner 和 Grid 组合在一起作为内容
    # 而不是把 grid 放在 subtitle 里
    content_group = Group(
        banner_text,
        "\n",  # 加个换行，拉开一点距离
        grid
    )

    # 用面板包裹起来
    panel = Panel(
        content_group,
        title="[bold blue]⚡ SYSTEM DASHBOARD ⚡[/bold blue]",
        border_style="blue",
        # subtitle 现在可以留空，或者放一句简单的 Slogan
        subtitle="[dim]Industrial Grade Auto-Login Daemon[/dim]",
        subtitle_align="right"
    )
    rprint(panel)

def start_up_animation():
    """模拟启动加载动画"""
    with Progress(
        SpinnerColumn("dots", style="bold magenta"),
        TextColumn("[progress.description]{task.description}"),
        transient=True, # 完成后消失
    ) as progress:
        task1 = progress.add_task("[cyan]Initializing core modules...", total=3)
        time.sleep(0.5); progress.advance(task1)
        time.sleep(0.5); progress.advance(task1)
        time.sleep(0.5); progress.advance(task1)
        
        task2 = progress.add_task("[green]Verifying network environment...", total=3)
        time.sleep(0.3); progress.advance(task2)
        time.sleep(0.3); progress.advance(task2)
        time.sleep(0.3); progress.advance(task2)

def main():
    console.clear() # 清屏
    print_banner()
    start_up_animation()
    
    rprint("\n[bold yellow]>>> Starting Daemon Loop... (Press Ctrl+C to stop)[/bold yellow]")
    rprint("[dim]--------------------------------------------------------[/dim]")
    
    # 这里开始运行原来的死循环
    try:
        run_daemon(force_loop=True)
    except KeyboardInterrupt:
        rprint("\n[bold red]![/bold red] [red]Daemon stopped by user.[/red] 👋")
        sys.exit(0)

if __name__ == "__main__":
    main()