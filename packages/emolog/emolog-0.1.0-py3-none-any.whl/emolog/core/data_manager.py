"""
Data management for emotion logs
"""

import csv
import json
import os
import tarfile
import uuid
import zoneinfo
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

console = Console()

# Korean timezone
KST = zoneinfo.ZoneInfo("Asia/Seoul")


class DataManager:
    """Manages emotion log data storage and retrieval"""

    def __init__(self):
        self.base_dir = Path.home() / ".emolog"
        self.entries_dir = self.base_dir / "entries"
        self.config_file = self.base_dir / "config.json"
        self.templates_file = self.base_dir / "templates.json"
        self.exports_dir = self.base_dir / "exports"

        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [self.base_dir, self.entries_dir, self.exports_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _parse_timestamp_to_kst(self, timestamp_str: str) -> datetime:
        """Parse timestamp string and convert to KST"""
        if timestamp_str.endswith("Z"):
            return datetime.fromisoformat(
                timestamp_str.replace("Z", "+00:00")
            ).astimezone(KST)
        elif "+" in timestamp_str:
            return datetime.fromisoformat(timestamp_str).astimezone(KST)
        else:
            # Assume it's already in KST
            timestamp = datetime.fromisoformat(timestamp_str)
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=KST)
            return timestamp

    def save_entry(self, entry: Dict[str, Any]) -> str:
        """Save an emotion log entry"""
        # Add timestamp and ID if not present
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now(KST).isoformat()
        if "id" not in entry:
            entry["id"] = str(uuid.uuid4())

        # Determine file path based on date (use KST)
        if "timestamp" in entry and entry["timestamp"]:
            # Parse timestamp considering it might be UTC or KST
            timestamp_str = entry["timestamp"]
            if timestamp_str.endswith("Z"):
                timestamp = datetime.fromisoformat(
                    timestamp_str.replace("Z", "+00:00")
                ).astimezone(KST)
            elif "+" in timestamp_str or timestamp_str.endswith("+09:00"):
                timestamp = datetime.fromisoformat(timestamp_str).astimezone(KST)
            else:
                # Assume it's already in KST
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=KST)
        else:
            timestamp = datetime.now(KST)

        year = timestamp.year
        month = timestamp.month
        day = timestamp.day

        file_path = (
            self.entries_dir
            / str(year)
            / f"{month:02d}"
            / f"{year}{month:02d}{day:02d}.jsonl"
        )
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Append to JSONL file
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return entry["id"]

    def load_entries(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        context: Optional[str] = None,
        emotion: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Load emotion log entries with optional filters"""
        entries = []

        # If no date range specified, load all entries
        if start_date is None:
            start_date = datetime(2020, 1, 1, tzinfo=KST)
        if end_date is None:
            end_date = datetime.now(KST)

        # Iterate through potential date directories
        current_date = start_date.replace(day=1)  # Start from beginning of month
        while current_date <= end_date:
            year_dir = self.entries_dir / str(current_date.year)
            month_dir = year_dir / f"{current_date.month:02d}"

            if month_dir.exists():
                for jsonl_file in month_dir.glob("*.jsonl"):
                    try:
                        with open(jsonl_file, "r", encoding="utf-8") as f:
                            for line in f:
                                if line.strip():
                                    entry = json.loads(line.strip())

                                    # Parse timestamp and convert to KST
                                    timestamp_str = entry["timestamp"]
                                    if timestamp_str.endswith("Z"):
                                        entry_time = datetime.fromisoformat(
                                            timestamp_str.replace("Z", "+00:00")
                                        ).astimezone(KST)
                                    elif "+" in timestamp_str:
                                        entry_time = datetime.fromisoformat(
                                            timestamp_str
                                        ).astimezone(KST)
                                    else:
                                        # Assume it's already in KST
                                        entry_time = datetime.fromisoformat(
                                            timestamp_str
                                        )
                                        if entry_time.tzinfo is None:
                                            entry_time = entry_time.replace(tzinfo=KST)

                                    # Apply date filter
                                    if start_date <= entry_time <= end_date:
                                        # Apply other filters
                                        if context and entry.get("context") != context:
                                            continue
                                        if emotion and entry.get("emotion") != emotion:
                                            continue

                                        entries.append(entry)
                    except (json.JSONDecodeError, KeyError) as e:
                        console.print(
                            f"[yellow]Warning: Could not parse entry in {jsonl_file}: {e}[/yellow]"
                        )

            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        # Sort by timestamp
        entries.sort(key=lambda x: x["timestamp"])
        return entries

    def get_recent_entries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent entries"""
        all_entries = self.load_entries()
        return all_entries[-limit:] if len(all_entries) > limit else all_entries

    def get_today_entries(self) -> List[Dict[str, Any]]:
        """Get today's entries"""
        today = datetime.now(KST)
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = today.replace(hour=23, minute=59, second=59, microsecond=999999)

        return self.load_entries(start_of_day, end_of_day)

    def export_data(
        self, format_type: str, period: str = "all", output_path: Optional[str] = None
    ):
        """Export emotion data to CSV or JSON"""
        # Determine date range based on period
        now = datetime.now(KST)
        if period == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == "week":
            start_date = now.replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=7)
            end_date = now
        elif period == "month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        else:  # 'all'
            start_date = None
            end_date = None

        entries = self.load_entries(start_date, end_date)

        if not entries:
            console.print("[yellow]내보낼 데이터가 없습니다.[/yellow]")
            return

        # Generate filename if not provided
        if output_path is None:
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            output_path = (
                self.exports_dir / f"emolog_{period}_{timestamp}.{format_type}"
            )
        else:
            output_path = Path(output_path)

        if format_type == "csv":
            self._export_csv(entries, output_path)
        elif format_type == "json":
            self._export_json(entries, output_path)

        console.print(f"[green]데이터를 내보냈습니다: {output_path}[/green]")

    def _export_csv(self, entries: List[Dict[str, Any]], output_path: Path):
        """Export entries to CSV format"""
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            if not entries:
                return

            fieldnames = [
                "timestamp",
                "situation",
                "emotion",
                "intensity",
                "body_reaction",
                "thought",
                "context",
                "tags",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for entry in entries:
                # Convert tags list to string
                csv_entry = entry.copy()
                if "tags" in csv_entry and isinstance(csv_entry["tags"], list):
                    csv_entry["tags"] = ",".join(csv_entry["tags"])
                writer.writerow(csv_entry)

    def _export_json(self, entries: List[Dict[str, Any]], output_path: Path):
        """Export entries to JSON format"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)

    def create_backup(self):
        """Create a compressed backup of all emotion data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.base_dir / f"backup_{timestamp}.tar.gz"

        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(self.entries_dir, arcname="entries")
            if self.config_file.exists():
                tar.add(self.config_file, arcname="config.json")
            if self.templates_file.exists():
                tar.add(self.templates_file, arcname="templates.json")

        console.print(f"[green]백업이 생성되었습니다: {backup_path}[/green]")
        return backup_path

    def reset_data(self, period: str = "all", skip_confirm: bool = False):
        """Reset emotion data for specified period"""

        # Count entries to be deleted
        if period == "all":
            entries_to_delete = self.load_entries()
            description = "모든 감정 기록"
        else:
            now = datetime.now(KST)
            if period == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now
                description = "오늘의 감정 기록"
            elif period == "week":
                start_date = now - timedelta(days=7)
                end_date = now
                description = "이번 주 감정 기록"
            elif period == "month":
                start_date = now.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                end_date = now
                description = "이번 달 감정 기록"
            else:
                console.print(f"[red]알 수 없는 기간: {period}[/red]")
                return

            entries_to_delete = self.load_entries(start_date, end_date)

        if not entries_to_delete:
            console.print(f"[yellow]{description}가 없습니다.[/yellow]")
            return

        console.print(
            f"\n[bold red]⚠️ 주의: {description} {len(entries_to_delete)}개를 삭제합니다![/bold red]"
        )

        if not skip_confirm:
            if period == "all":
                console.print(
                    "[red]이 작업은 되돌릴 수 없습니다. 백업을 먼저 생성하는 것을 권장합니다.[/red]"
                )
                create_backup = Confirm.ask(
                    "삭제 전에 백업을 생성하시겠습니까?", default=True
                )
                if create_backup:
                    self.create_backup()

            confirmed = Confirm.ask(
                f"정말로 {description}를 삭제하시겠습니까?", default=False
            )
            if not confirmed:
                console.print("[yellow]취소되었습니다.[/yellow]")
                return

        # Perform deletion
        if period == "all":
            self._reset_all_data()
        else:
            self._delete_period_data(entries_to_delete)

        console.print(
            f"[green]✅ {description} {len(entries_to_delete)}개가 삭제되었습니다.[/green]"
        )

    def _reset_all_data(self):
        """Reset all emotion data (complete reset)"""
        import shutil

        # Remove all entries
        if self.entries_dir.exists():
            shutil.rmtree(self.entries_dir)
            self.entries_dir.mkdir(parents=True, exist_ok=True)

        # Reset config (optional)
        if self.config_file.exists():
            self.config_file.unlink()

        # Reset templates (optional)
        if self.templates_file.exists():
            self.templates_file.unlink()

    def _delete_period_data(self, entries_to_delete: List[Dict[str, Any]]):
        """Delete specific entries by recreating files without them"""
        import shutil
        import tempfile

        # Group entries by file
        entries_by_file = defaultdict(list)
        for entry in entries_to_delete:
            timestamp = datetime.fromisoformat(
                entry["timestamp"].replace("Z", "+00:00")
            )
            year = timestamp.year
            month = timestamp.month
            day = timestamp.day
            file_path = (
                self.entries_dir
                / str(year)
                / f"{month:02d}"
                / f"{year}{month:02d}{day:02d}.jsonl"
            )
            entries_by_file[file_path].append(entry["id"])

        # Process each file
        for file_path, entry_ids_to_delete in entries_by_file.items():
            if not file_path.exists():
                continue

            # Read all entries from file
            remaining_entries = []
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line.strip())
                            if entry.get("id") not in entry_ids_to_delete:
                                remaining_entries.append(entry)
                        except json.JSONDecodeError:
                            # Keep malformed entries
                            remaining_entries.append({"raw_line": line.strip()})

            # Rewrite file with remaining entries
            if remaining_entries:
                with open(file_path, "w", encoding="utf-8") as f:
                    for entry in remaining_entries:
                        if "raw_line" in entry:
                            f.write(entry["raw_line"] + "\n")
                        else:
                            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            else:
                # Remove empty file
                file_path.unlink()

                # Remove empty directories
                try:
                    file_path.parent.rmdir()  # Remove month dir if empty
                    file_path.parent.parent.rmdir()  # Remove year dir if empty
                except OSError:
                    pass  # Directory not empty, that's fine

    def selective_delete(self, period: str = "week"):
        """Interactively select and delete specific emotion entries"""

        # Get entries for the specified period
        entries = self._get_period_entries(period)

        if not entries:
            console.print(f"[yellow]{period} 기간에 기록된 감정이 없습니다.[/yellow]")
            return

        console.print(f"\n[bold blue]📋 {period.upper()} 기간의 감정 기록[/bold blue]")
        console.print("━" * 50)

        # Show entries in a table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("번호", justify="center", style="cyan")
        table.add_column("날짜/시간", style="dim")
        table.add_column("상황", style="white")
        table.add_column("감정", style="yellow")
        table.add_column("강도", justify="center")
        table.add_column("컨텍스트", style="blue")

        for i, entry in enumerate(entries, 1):
            timestamp = datetime.fromisoformat(
                entry["timestamp"].replace("Z", "+00:00")
            )
            date_str = timestamp.strftime("%m/%d %H:%M")
            situation = entry.get("situation", "")[:30] + (
                "..." if len(entry.get("situation", "")) > 30 else ""
            )
            emotion = entry.get("emotion", "")
            intensity = str(entry.get("intensity", ""))
            context = entry.get("context", "")

            table.add_row(str(i), date_str, situation, emotion, intensity, context)

        console.print(table)

        # Interactive selection
        console.print(
            f"\n[bold yellow]삭제할 항목을 선택하세요 (1-{len(entries)}, 여러 개는 쉼표로 구분):[/bold yellow]"
        )
        console.print(
            "[dim]예: 1,3,5 또는 'all' (모두 선택) 또는 'cancel' (취소)[/dim]"
        )

        selection = Prompt.ask("선택").strip()

        if selection.lower() == "cancel":
            console.print("[yellow]취소되었습니다.[/yellow]")
            return

        # Parse selection
        selected_indices = []
        if selection.lower() == "all":
            selected_indices = list(range(len(entries)))
        else:
            try:
                for item in selection.split(","):
                    item = item.strip()
                    if item.isdigit():
                        index = int(item) - 1  # Convert to 0-based index
                        if 0 <= index < len(entries):
                            selected_indices.append(index)
                        else:
                            console.print(f"[red]잘못된 번호: {item}[/red]")
                            return
                    else:
                        console.print(f"[red]잘못된 입력: {item}[/red]")
                        return
            except ValueError:
                console.print("[red]잘못된 형식입니다.[/red]")
                return

        if not selected_indices:
            console.print("[yellow]선택된 항목이 없습니다.[/yellow]")
            return

        # Show selected entries for confirmation
        selected_entries = [entries[i] for i in selected_indices]

        console.print(
            f"\n[bold red]⚠️ 선택된 {len(selected_entries)}개 항목을 삭제합니다:[/bold red]"
        )
        for i, entry in enumerate(selected_entries, 1):
            timestamp = datetime.fromisoformat(
                entry["timestamp"].replace("Z", "+00:00")
            )
            date_str = timestamp.strftime("%m/%d %H:%M")
            situation = entry.get("situation", "")[:50]
            emotion = entry.get("emotion", "")
            console.print(f"  {i}. [{date_str}] {situation} - {emotion}")

        # Confirmation
        confirmed = Confirm.ask("정말로 삭제하시겠습니까?", default=False)
        if not confirmed:
            console.print("[yellow]취소되었습니다.[/yellow]")
            return

        # Delete selected entries
        self._delete_period_data(selected_entries)
        console.print(
            f"[green]✅ {len(selected_entries)}개 항목이 삭제되었습니다.[/green]"
        )

    def _get_period_entries(self, period: str):
        """Get entries for a specific period (helper method)"""
        now = datetime.now(KST)

        if period == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == "week":
            start_date = now - timedelta(days=7)
            end_date = now
        elif period == "month":
            start_date = now - timedelta(days=30)
            end_date = now
        elif period == "all":
            start_date = None
            end_date = None
        else:
            # Default to week
            start_date = now - timedelta(days=7)
            end_date = now

        return self.load_entries(start_date, end_date)

    def edit_entry(self, period: str = "week"):
        """Interactively select and edit specific emotion entries"""

        # Get entries for the specified period
        entries = self._get_period_entries(period)

        if not entries:
            console.print(f"[yellow]{period} 기간에 기록된 감정이 없습니다.[/yellow]")
            return

        console.print(f"\n[bold blue]📝 {period.upper()} 기간의 감정 기록[/bold blue]")
        console.print("━" * 50)

        # Show entries in a table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("번호", justify="center", style="cyan")
        table.add_column("날짜/시간", style="dim")
        table.add_column("상황", style="white")
        table.add_column("감정", style="yellow")
        table.add_column("강도", justify="center")
        table.add_column("컨텍스트", style="blue")

        for i, entry in enumerate(entries, 1):
            timestamp = datetime.fromisoformat(
                entry["timestamp"].replace("Z", "+00:00")
            )
            date_str = timestamp.strftime("%m/%d %H:%M")
            situation = entry.get("situation", "")[:30] + (
                "..." if len(entry.get("situation", "")) > 30 else ""
            )
            emotion = entry.get("emotion", "")
            intensity = str(entry.get("intensity", ""))
            context = entry.get("context", "")

            table.add_row(str(i), date_str, situation, emotion, intensity, context)

        console.print(table)

        # Select entry to edit
        console.print(
            f"\n[bold yellow]수정할 항목을 선택하세요 (1-{len(entries)}):[/bold yellow]"
        )

        try:
            choice = IntPrompt.ask("번호", default=1)
            if not (1 <= choice <= len(entries)):
                console.print("[red]잘못된 번호입니다.[/red]")
                return
        except:
            console.print("[red]잘못된 입력입니다.[/red]")
            return

        selected_entry = entries[choice - 1]

        # Show current entry details
        console.print(f"\n[bold cyan]현재 엔트리 내용:[/bold cyan]")
        self._display_entry_details(selected_entry)

        # Interactive editing
        console.print(f"\n[bold yellow]수정할 필드를 선택하세요:[/bold yellow]")
        console.print("1. 상황")
        console.print("2. 감정")
        console.print("3. 강도")
        console.print("4. 몸 반응")
        console.print("5. 생각")
        console.print("6. 컨텍스트")
        console.print("7. 태그")
        console.print("8. 모든 필드 수정")
        console.print("9. 취소")

        field_choice = Prompt.ask(
            "선택", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"], default="9"
        )

        if field_choice == "9":
            console.print("[yellow]취소되었습니다.[/yellow]")
            return

        # Edit the entry
        updated_entry = selected_entry.copy()

        if field_choice == "1" or field_choice == "8":
            updated_entry["situation"] = self._edit_situation(
                selected_entry.get("situation", "")
            )

        if field_choice == "2" or field_choice == "8":
            updated_entry["emotion"] = self._edit_emotion(
                selected_entry.get("emotion", "")
            )

        if field_choice == "3" or field_choice == "8":
            updated_entry["intensity"] = self._edit_intensity(
                selected_entry.get("intensity", 5)
            )

        if field_choice == "4" or field_choice == "8":
            updated_entry["body_reaction"] = self._edit_body_reaction(
                selected_entry.get("body_reaction", "")
            )

        if field_choice == "5" or field_choice == "8":
            updated_entry["thought"] = self._edit_thought(
                selected_entry.get("thought", "")
            )

        if field_choice == "6" or field_choice == "8":
            updated_entry["context"] = self._edit_context(
                selected_entry.get("context", "")
            )

        if field_choice == "7" or field_choice == "8":
            updated_entry["tags"] = self._edit_tags(selected_entry.get("tags", []))

        # Show updated entry and confirm
        console.print(f"\n[bold cyan]수정된 내용:[/bold cyan]")
        self._display_entry_details(updated_entry)

        confirmed = Confirm.ask("변경사항을 저장하시겠습니까?", default=True)
        if confirmed:
            self._update_entry(selected_entry, updated_entry)
            console.print("[green]✅ 엔트리가 수정되었습니다.[/green]")
        else:
            console.print("[yellow]변경사항이 취소되었습니다.[/yellow]")

    def _display_entry_details(self, entry: Dict[str, Any]):
        """Display detailed entry information"""
        timestamp = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
        date_str = timestamp.strftime("%Y년 %m월 %d일 %H:%M")

        content = []
        content.append(f"📅 날짜: {date_str}")
        content.append(f"📝 상황: {entry.get('situation', '')}")
        content.append(
            f"😊 감정: {entry.get('emotion', '')} (강도: {entry.get('intensity', '')}/10)"
        )

        if entry.get("body_reaction"):
            content.append(f"🫀 몸 반응: {entry.get('body_reaction')}")

        if entry.get("thought"):
            content.append(f"💭 생각: {entry.get('thought')}")

        content.append(f"🏷️ 컨텍스트: {entry.get('context', '')}")

        if entry.get("tags"):
            content.append(f"#️⃣ 태그: {', '.join(entry.get('tags', []))}")

        console.print(Panel("\n".join(content), style="blue"))

    def _edit_situation(self, current: str) -> str:
        """Edit situation field"""
        console.print(f"\n[bold cyan]상황 수정[/bold cyan]")
        console.print(f"현재: {current}")
        new_value = Prompt.ask("새로운 상황", default=current).strip()
        return new_value if new_value else current

    def _edit_emotion(self, current: str) -> str:
        """Edit emotion field"""
        console.print(f"\n[bold cyan]감정 수정[/bold cyan]")
        console.print(f"현재: {current}")
        new_value = Prompt.ask("새로운 감정", default=current).strip()
        return new_value if new_value else current

    def _edit_intensity(self, current: int) -> int:
        """Edit intensity field"""
        console.print(f"\n[bold cyan]강도 수정[/bold cyan]")
        console.print(f"현재: {current}/10")
        try:
            new_value = IntPrompt.ask("새로운 강도 (1-10)", default=current)
            return max(1, min(10, new_value))
        except:
            return current

    def _edit_body_reaction(self, current: str) -> str:
        """Edit body reaction field"""
        console.print(f"\n[bold cyan]몸 반응 수정[/bold cyan]")
        console.print(f"현재: {current if current else '없음'}")
        new_value = Prompt.ask("새로운 몸 반응", default=current).strip()
        return new_value

    def _edit_thought(self, current: str) -> str:
        """Edit thought field"""
        console.print(f"\n[bold cyan]생각 수정[/bold cyan]")
        console.print(f"현재: {current if current else '없음'}")
        new_value = Prompt.ask("새로운 생각", default=current).strip()
        return new_value

    def _edit_context(self, current: str) -> str:
        """Edit context field"""
        console.print(f"\n[bold cyan]컨텍스트 수정[/bold cyan]")
        console.print(f"현재: {current}")

        # Load context options
        contexts_file = Path(__file__).parent.parent / "data" / "contexts.json"
        if contexts_file.exists():
            with open(contexts_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                contexts = data.get("contexts", [])

            console.print("옵션:")
            for i, ctx in enumerate(contexts, 1):
                console.print(f"{i}. {ctx['emoji']} {ctx['label']} ({ctx['key']})")

        new_value = Prompt.ask("새로운 컨텍스트", default=current).strip()
        return new_value if new_value else current

    def _edit_tags(self, current: List[str]) -> List[str]:
        """Edit tags field"""
        console.print(f"\n[bold cyan]태그 수정[/bold cyan]")
        current_tags_str = ", ".join(current) if current else ""
        console.print(f"현재: {current_tags_str if current_tags_str else '없음'}")

        new_value = Prompt.ask(
            "새로운 태그 (쉼표로 구분)", default=current_tags_str
        ).strip()
        if new_value:
            tags = [tag.strip() for tag in new_value.split(",") if tag.strip()]
            return tags[:5]  # Limit to 5 tags
        return []

    def _update_entry(
        self, original_entry: Dict[str, Any], updated_entry: Dict[str, Any]
    ):
        """Update an entry in the data files"""
        # Find and update the entry in the appropriate file
        timestamp = datetime.fromisoformat(
            original_entry["timestamp"].replace("Z", "+00:00")
        )
        year = timestamp.year
        month = timestamp.month
        day = timestamp.day
        file_path = (
            self.entries_dir
            / str(year)
            / f"{month:02d}"
            / f"{year}{month:02d}{day:02d}.jsonl"
        )

        if not file_path.exists():
            console.print("[red]원본 파일을 찾을 수 없습니다.[/red]")
            return

        # Read all entries from file
        updated_entries = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        entry = json.loads(line.strip())
                        if entry.get("id") == original_entry.get("id"):
                            # Update this entry
                            updated_entries.append(updated_entry)
                        else:
                            updated_entries.append(entry)
                    except json.JSONDecodeError:
                        # Keep malformed entries as is
                        updated_entries.append({"raw_line": line.strip()})

        # Rewrite file with updated entries
        with open(file_path, "w", encoding="utf-8") as f:
            for entry in updated_entries:
                if "raw_line" in entry:
                    f.write(entry["raw_line"] + "\n")
                else:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
