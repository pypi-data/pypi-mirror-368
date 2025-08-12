#!/usr/bin/env python3
"""
Emolog - A terminal-based emotion logging tool for developers
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text

from .core.analyzer import EmotionAnalyzer
from .core.data_manager import DataManager
from .core.emotion_logger import EmotionLogger

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Emolog - Track your emotions from the terminal"""
    if ctx.invoked_subcommand is None:
        # Default action: start emotion logging
        start_emotion_logging()


@main.command()
def log():
    """Log a new emotion entry"""
    start_emotion_logging()


@main.command()
def stats():
    """Show emotion statistics"""
    analyzer = EmotionAnalyzer()
    analyzer.show_stats()


@main.command()
def patterns():
    """Show emotion patterns"""
    analyzer = EmotionAnalyzer()
    analyzer.show_patterns()


@main.command()
def triggers():
    """Show stress triggers analysis"""
    analyzer = EmotionAnalyzer()
    analyzer.show_triggers()


@main.command()
def timeline():
    """Show emotion timeline"""
    analyzer = EmotionAnalyzer()
    analyzer.show_timeline()


@main.command()
@click.option(
    "--format", "export_format", type=click.Choice(["csv", "json"]), default="csv"
)
@click.option(
    "--period", default="all", help="Period to export (all, today, week, month)"
)
@click.option("--output", help="Output file path")
def export(export_format, period, output):
    """Export emotion data"""
    data_manager = DataManager()
    data_manager.export_data(export_format, period, output)


@main.command()
def backup():
    """Create a backup of all emotion data"""
    data_manager = DataManager()
    data_manager.create_backup()


@main.command()
@click.option("--period", help="Reset specific period (today, week, month, or all)")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def reset(period, confirm):
    """Reset emotion data"""
    data_manager = DataManager()

    if not period:
        # Interactive selection
        console.print("\n[bold yellow]🔄 Reset 옵션을 선택해주세요:[/bold yellow]")
        console.print("1. 오늘 데이터만 삭제")
        console.print("2. 이번 주 데이터 삭제")
        console.print("3. 이번 달 데이터 삭제")
        console.print("4. 모든 데이터 삭제 (완전 초기화)")
        console.print("5. 취소")

        choice = Prompt.ask("선택", choices=["1", "2", "3", "4", "5"], default="5")

        if choice == "1":
            period = "today"
        elif choice == "2":
            period = "week"
        elif choice == "3":
            period = "month"
        elif choice == "4":
            period = "all"
        else:
            console.print("[yellow]취소되었습니다.[/yellow]")
            return

    data_manager.reset_data(period, confirm)


@main.command()
@click.option(
    "--period",
    default="week",
    help="Period to show entries from (today, week, month, all)",
)
def delete(period):
    """Selectively delete emotion entries"""
    data_manager = DataManager()
    data_manager.selective_delete(period)


@main.command()
@click.option(
    "--period",
    default="week",
    help="Period to show entries from (today, week, month, all)",
)
def edit(period):
    """Edit existing emotion entries"""
    data_manager = DataManager()
    data_manager.edit_entry(period)


def start_emotion_logging():
    """Start the interactive emotion logging process"""
    console.print(
        Panel(
            "[bold blue]🌟 Emolog[/bold blue]\n" "지금 기분을 기록해보세요",
            style="blue",
        )
    )

    logger = EmotionLogger()
    try:
        logger.start_interactive_logging()
    except KeyboardInterrupt:
        console.print("\n[yellow]기록을 취소했습니다.[/yellow]")
    except Exception as e:
        console.print(f"[red]오류가 발생했습니다: {e}[/red]")


if __name__ == "__main__":
    main()
