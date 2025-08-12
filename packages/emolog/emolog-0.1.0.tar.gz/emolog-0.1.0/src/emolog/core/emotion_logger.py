"""
Interactive emotion logging system
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

from .data_manager import DataManager

console = Console()


class EmotionLogger:
    """Handles interactive emotion logging"""

    def __init__(self):
        self.data_manager = DataManager()
        self.data_dir = Path(__file__).parent.parent / "data"

        # Load predefined data
        self.emotions = self._load_emotions()
        self.contexts = self._load_contexts()
        self.body_reactions = self._load_body_reactions()

    def _load_emotions(self) -> Dict[str, List[str]]:
        """Load emotion categories from JSON file"""
        emotions_file = self.data_dir / "emotions.json"
        if emotions_file.exists():
            with open(emotions_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"positive": [], "negative": [], "neutral": []}

    def _load_contexts(self) -> List[Dict[str, str]]:
        """Load context options from JSON file"""
        contexts_file = self.data_dir / "contexts.json"
        if contexts_file.exists():
            with open(contexts_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("contexts", [])
        return []

    def _load_body_reactions(self) -> List[str]:
        """Load body reaction options from JSON file"""
        reactions_file = self.data_dir / "body_reactions.json"
        if reactions_file.exists():
            with open(reactions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("reactions", [])
        return []

    def start_interactive_logging(self):
        """Start the interactive emotion logging process"""
        console.print()

        # Step 1: Situation (Required)
        situation = self._get_situation()
        if not situation:
            console.print("[yellow]상황을 입력하지 않으면 기록할 수 없습니다.[/yellow]")
            return

        # Step 2: Emotion (Required)
        emotion = self._get_emotion()
        if not emotion:
            console.print("[yellow]감정을 입력하지 않으면 기록할 수 없습니다.[/yellow]")
            return

        # Step 3: Intensity (Optional, default 5)
        intensity = self._get_intensity()

        # Step 4: Body reaction (Optional)
        body_reaction = self._get_body_reaction()

        # Step 5: Thought (Optional)
        thought = self._get_thought()

        # Step 6: Context (Required)
        context = self._get_context()
        if not context:
            console.print(
                "[yellow]컨텍스트를 선택하지 않으면 기록할 수 없습니다.[/yellow]"
            )
            return

        # Step 7: Tags (Optional)
        tags = self._get_tags()

        # Create entry
        entry = {
            "situation": situation,
            "emotion": emotion,
            "intensity": intensity,
            "body_reaction": body_reaction,
            "thought": thought,
            "context": context,
            "tags": tags,
        }

        # Show summary and confirm
        if self._confirm_entry(entry):
            entry_id = self.data_manager.save_entry(entry)
            console.print(
                f"[green]✅ 기록이 저장되었습니다! (ID: {entry_id[:8]})[/green]"
            )
        else:
            console.print("[yellow]기록을 취소했습니다.[/yellow]")

    def _get_situation(self) -> str:
        """Get situation description from user"""
        console.print("\n[bold cyan]📝 상황을 간단히 적어주세요:[/bold cyan]")
        console.print(
            "[dim]예: '회의에서 디자인 변경 요구 받음', '코드리뷰 받음'[/dim]"
        )

        situation = Prompt.ask("상황", default="").strip()
        return situation

    def _get_emotion(self) -> str:
        """Get emotion from user with suggestions"""
        console.print("\n[bold cyan]😊 어떤 감정이었나요?[/bold cyan]")

        # Show emotion categories
        table = Table(show_header=True, header_style="bold")
        table.add_column("긍정", style="green")
        table.add_column("부정", style="red")
        table.add_column("중성", style="blue")

        max_rows = max(
            len(self.emotions["positive"]),
            len(self.emotions["negative"]),
            len(self.emotions["neutral"]),
        )

        for i in range(max_rows):
            positive = (
                self.emotions["positive"][i]
                if i < len(self.emotions["positive"])
                else ""
            )
            negative = (
                self.emotions["negative"][i]
                if i < len(self.emotions["negative"])
                else ""
            )
            neutral = (
                self.emotions["neutral"][i] if i < len(self.emotions["neutral"]) else ""
            )
            table.add_row(positive, negative, neutral)

        console.print(table)
        console.print("[dim]위 목록에서 선택하거나 직접 입력하세요[/dim]")

        emotion = Prompt.ask("감정", default="").strip()
        return emotion

    def _get_intensity(self) -> int:
        """Get emotion intensity from user"""
        console.print("\n[bold cyan]🌡️ 강도는? (1-10)[/bold cyan]")
        console.print("[dim]1: 거의 안 느낌 ~ 10: 매우 강함[/dim]")

        try:
            intensity = IntPrompt.ask("강도", default=5)
            return max(1, min(10, intensity))  # Clamp between 1-10
        except:
            return 5

    def _get_body_reaction(self) -> str:
        """Get body reaction from user"""
        console.print("\n[bold cyan]🫀 몸의 반응이 있었다면?[/bold cyan]")

        # Show common reactions
        console.print("[dim]일반적인 반응들:[/dim]")
        for i, reaction in enumerate(self.body_reactions, 1):
            console.print(f"[dim]{i:2d}. {reaction}[/dim]")

        console.print(
            "[dim]위 목록에서 선택하거나 직접 입력하세요 (Enter로 건너뛰기)[/dim]"
        )

        body_reaction = Prompt.ask("몸 반응", default="").strip()

        # Check if user entered a number
        if body_reaction.isdigit():
            index = int(body_reaction) - 1
            if 0 <= index < len(self.body_reactions):
                body_reaction = self.body_reactions[index]

        return body_reaction

    def _get_thought(self) -> str:
        """Get thought from user"""
        console.print("\n[bold cyan]💭 그때 든 생각은?[/bold cyan]")
        console.print(
            "[dim]예: '망했다', '어떻게 해결하지', '잘될거야' (Enter로 건너뛰기)[/dim]"
        )

        thought = Prompt.ask("생각", default="").strip()
        return thought

    def _get_context(self) -> str:
        """Get context from user"""
        console.print("\n[bold cyan]🏷️ 컨텍스트를 선택해주세요:[/bold cyan]")

        for i, ctx in enumerate(self.contexts, 1):
            console.print(
                f"[dim]{i}. {ctx['emoji']} {ctx['label']} ({ctx['key']})[/dim]"
            )

        while True:
            choice = Prompt.ask("번호를 선택하거나 직접 입력", default="").strip()

            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(self.contexts):
                    return self.contexts[index]["key"]
            elif choice:
                # Direct input
                return choice.lower()

            console.print(
                "[red]올바른 번호를 선택하거나 컨텍스트를 입력해주세요.[/red]"
            )

    def _get_tags(self) -> List[str]:
        """Get tags from user"""
        console.print(
            "\n[bold cyan]#️⃣ 태그 (쉼표로 구분, Enter로 건너뛰기):[/bold cyan]"
        )
        console.print("[dim]예: '회의,디자인,일정'[/dim]")

        tags_input = Prompt.ask("태그", default="").strip()
        if tags_input:
            tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
            return tags[:5]  # Limit to 5 tags
        return []

    def _confirm_entry(self, entry: Dict[str, Any]) -> bool:
        """Show entry summary and get confirmation"""
        console.print("\n[bold cyan]📋 입력한 내용을 확인해주세요:[/bold cyan]")

        panel_content = []
        panel_content.append(f"📝 상황: {entry['situation']}")
        panel_content.append(
            f"😊 감정: {entry['emotion']} (강도: {entry['intensity']}/10)"
        )

        if entry["body_reaction"]:
            panel_content.append(f"🫀 몸 반응: {entry['body_reaction']}")

        if entry["thought"]:
            panel_content.append(f"💭 생각: {entry['thought']}")

        panel_content.append(f"🏷️ 컨텍스트: {entry['context']}")

        if entry["tags"]:
            panel_content.append(f"#️⃣ 태그: {', '.join(entry['tags'])}")

        console.print(Panel("\n".join(panel_content), title="입력 내용", style="blue"))

        return Prompt.ask("저장하시겠습니까?", choices=["y", "n"], default="y") == "y"
