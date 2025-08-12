"""
Emotion data analysis and insights
"""

import zoneinfo
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.table import Table
from rich.text import Text

from .data_manager import DataManager

# Korean timezone
KST = zoneinfo.ZoneInfo("Asia/Seoul")

console = Console()


class EmotionAnalyzer:
    """Analyzes emotion log data and provides insights"""

    def __init__(self):
        self.data_manager = DataManager()

    def show_stats(self, period: str = "week"):
        """Show basic emotion statistics"""
        # Get data for the specified period
        entries = self._get_period_entries(period)

        if not entries:
            console.print(f"[yellow]{period} 기간에 기록된 감정이 없습니다.[/yellow]")
            return

        console.print(f"\n[bold blue]📊 {period.upper()} 감정 분포[/bold blue]")
        console.print("━" * 30)

        # Emotion distribution
        emotions = [entry["emotion"] for entry in entries if entry.get("emotion")]
        emotion_counts = Counter(emotions)
        total_count = len(entries)

        # Create emotion distribution table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("감정", style="cyan")
        table.add_column("횟수", justify="right")
        table.add_column("비율", justify="right")
        table.add_column("시각화", style="blue")

        for emotion, count in emotion_counts.most_common():
            percentage = (count / total_count) * 100
            bar = "█" * int(percentage / 3)  # Scale down for display
            table.add_row(
                emotion, str(count), f"{percentage:.1f}%", f"{bar} {percentage:.1f}%"
            )

        console.print(table)

        # Average intensity
        intensities = [
            entry.get("intensity", 5) for entry in entries if entry.get("intensity")
        ]
        if intensities:
            avg_intensity = sum(intensities) / len(intensities)
            console.print(f"\n📈 평균 강도: {avg_intensity:.1f}/10")

        # Context distribution
        contexts = [entry["context"] for entry in entries if entry.get("context")]
        context_counts = Counter(contexts)
        console.print(f"\n🏷️ 주요 컨텍스트:")
        for context, count in context_counts.most_common(3):
            percentage = (count / total_count) * 100
            console.print(f"   {context}: {count}회 ({percentage:.1f}%)")

        console.print(f"\n📅 총 기록: {total_count}개")

    def show_patterns(self):
        """Show emotion patterns and trends"""
        entries = self.data_manager.load_entries()

        if len(entries) < 5:
            console.print(
                "[yellow]패턴 분석을 위해서는 최소 5개 이상의 기록이 필요합니다.[/yellow]"
            )
            return

        console.print("\n[bold blue]🔍 발견된 패턴들[/bold blue]")
        console.print("━" * 30)

        patterns = []

        # Day of week patterns
        patterns.extend(self._analyze_day_patterns(entries))

        # Time of day patterns
        patterns.extend(self._analyze_time_patterns(entries))

        # Tag-emotion patterns
        patterns.extend(self._analyze_tag_patterns(entries))

        # Context-emotion patterns
        patterns.extend(self._analyze_context_patterns(entries))

        if patterns:
            for pattern in patterns:
                console.print(f"• {pattern}")
        else:
            console.print("[dim]아직 명확한 패턴이 발견되지 않았습니다.[/dim]")

    def show_triggers(self):
        """Show stress triggers and negative emotion analysis"""
        entries = self.data_manager.load_entries()

        # Define negative emotions
        negative_emotions = [
            "스트레스",
            "불안",
            "좌절",
            "화남",
            "긴장",
            "피로",
            "걱정",
            "슬픔",
            "짜증",
            "실망",
            "우울",
            "두려움",
        ]

        # Filter negative emotion entries
        negative_entries = [
            entry
            for entry in entries
            if entry.get("emotion", "").lower()
            in [e.lower() for e in negative_emotions]
        ]

        if not negative_entries:
            console.print("[green]부정적인 감정 기록이 없습니다! 🎉[/green]")
            return

        console.print("\n[bold red]🎯 스트레스 유발 요인 분석[/bold red]")
        console.print("━" * 35)

        # Analyze situations that trigger negative emotions
        situations = [
            entry["situation"] for entry in negative_entries if entry.get("situation")
        ]
        situation_analysis = self._analyze_triggers(situations, negative_entries)

        # Create triggers table
        table = Table(show_header=True, header_style="bold red")
        table.add_column("순위", justify="center")
        table.add_column("트리거", style="red")
        table.add_column("발생 횟수", justify="right")
        table.add_column("평균 강도", justify="right")

        for i, (trigger, count, avg_intensity) in enumerate(situation_analysis[:5], 1):
            table.add_row(str(i), trigger, f"{count}회", f"{avg_intensity:.1f}/10")

        console.print(table)

        # Most stressful tags
        tags_analysis = self._analyze_tag_triggers(negative_entries)
        if tags_analysis:
            console.print(f"\n[bold red]🏷️ 주요 스트레스 태그:[/bold red]")
            for tag, count, avg_intensity in tags_analysis[:3]:
                console.print(f"   {tag}: {count}회 (평균 강도 {avg_intensity:.1f})")

    def show_timeline(self, period: str = "today"):
        """Show emotion timeline"""
        entries = self._get_period_entries(period)

        if not entries:
            console.print(f"[yellow]{period} 기간에 기록된 감정이 없습니다.[/yellow]")
            return

        console.print(f"\n[bold blue]📈 {period.upper()} 감정 타임라인[/bold blue]")
        console.print("━" * 30)

        for entry in entries:
            # Parse timestamp and convert to KST
            timestamp_str = entry["timestamp"]
            if timestamp_str.endswith("Z"):
                timestamp = datetime.fromisoformat(
                    timestamp_str.replace("Z", "+00:00")
                ).astimezone(KST)
            elif "+" in timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str).astimezone(KST)
            else:
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=KST)

            time_str = timestamp.strftime("%H:%M")
            emotion = entry.get("emotion", "?")
            intensity = entry.get("intensity", 5)
            situation = entry.get("situation", "")[:30] + (
                "..." if len(entry.get("situation", "")) > 30 else ""
            )

            # Create visual bar based on intensity
            bar = "█" * intensity
            bar_color = self._get_emotion_color(emotion)

            console.print(
                f"{time_str}  {emotion}({intensity}) [{bar_color}]{bar}[/{bar_color}]  {situation}"
            )

    def _get_period_entries(self, period: str) -> List[Dict[str, Any]]:
        """Get entries for a specific period"""
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
        else:
            # Default to week
            start_date = now - timedelta(days=7)
            end_date = now

        return self.data_manager.load_entries(start_date, end_date)

    def _analyze_day_patterns(self, entries: List[Dict[str, Any]]) -> List[str]:
        """Analyze patterns by day of week"""
        patterns = []
        day_emotions = defaultdict(list)

        for entry in entries:
            # Parse timestamp and convert to KST
            timestamp_str = entry["timestamp"]
            if timestamp_str.endswith("Z"):
                timestamp = datetime.fromisoformat(
                    timestamp_str.replace("Z", "+00:00")
                ).astimezone(KST)
            elif "+" in timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str).astimezone(KST)
            else:
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=KST)

            day_name = timestamp.strftime("%A")
            emotion = entry.get("emotion", "")
            intensity = entry.get("intensity", 5)

            day_emotions[day_name].append((emotion, intensity))

        # Find patterns
        for day, emotions in day_emotions.items():
            if len(emotions) >= 3:  # Need sufficient data
                negative_emotions = ["스트레스", "불안", "좌절", "화남", "긴장"]
                negative_count = sum(
                    1 for emotion, _ in emotions if emotion in negative_emotions
                )

                if negative_count / len(emotions) > 0.6:  # 60% negative
                    patterns.append(
                        f"{day}에 부정적인 감정이 집중되는 경향 ({negative_count}/{len(emotions)})"
                    )

        return patterns

    def _analyze_time_patterns(self, entries: List[Dict[str, Any]]) -> List[str]:
        """Analyze patterns by time of day"""
        patterns = []
        time_emotions = defaultdict(list)

        for entry in entries:
            # Parse timestamp and convert to KST
            timestamp_str = entry["timestamp"]
            if timestamp_str.endswith("Z"):
                timestamp = datetime.fromisoformat(
                    timestamp_str.replace("Z", "+00:00")
                ).astimezone(KST)
            elif "+" in timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str).astimezone(KST)
            else:
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=KST)

            hour = timestamp.hour
            emotion = entry.get("emotion", "")
            intensity = entry.get("intensity", 5)

            time_slot = self._get_time_slot(hour)
            time_emotions[time_slot].append((emotion, intensity))

        # Find high-stress time periods
        for time_slot, emotions in time_emotions.items():
            if len(emotions) >= 3:
                avg_intensity = sum(intensity for _, intensity in emotions) / len(
                    emotions
                )
                if avg_intensity > 6.5:
                    patterns.append(
                        f"{time_slot} 시간대에 감정 강도가 높은 편 (평균 {avg_intensity:.1f})"
                    )

        return patterns

    def _analyze_tag_patterns(self, entries: List[Dict[str, Any]]) -> List[str]:
        """Analyze emotion patterns by tags"""
        patterns = []
        tag_emotions = defaultdict(list)

        for entry in entries:
            tags = entry.get("tags", [])
            emotion = entry.get("emotion", "")
            intensity = entry.get("intensity", 5)

            for tag in tags:
                tag_emotions[tag].append((emotion, intensity))

        # Find problematic tags
        for tag, emotions in tag_emotions.items():
            if len(emotions) >= 3:
                avg_intensity = sum(intensity for _, intensity in emotions) / len(
                    emotions
                )
                if avg_intensity > 7:
                    patterns.append(
                        f"'{tag}' 태그가 있을 때 감정 강도가 높음 (평균 {avg_intensity:.1f})"
                    )

        return patterns

    def _analyze_context_patterns(self, entries: List[Dict[str, Any]]) -> List[str]:
        """Analyze emotion patterns by context"""
        patterns = []
        context_emotions = defaultdict(list)

        for entry in entries:
            context = entry.get("context", "")
            emotion = entry.get("emotion", "")
            intensity = entry.get("intensity", 5)

            context_emotions[context].append((emotion, intensity))

        # Find context-specific patterns
        for context, emotions in context_emotions.items():
            if len(emotions) >= 5:
                negative_emotions = ["스트레스", "불안", "좌절", "화남", "긴장"]
                negative_count = sum(
                    1 for emotion, _ in emotions if emotion in negative_emotions
                )

                if negative_count / len(emotions) > 0.7:
                    patterns.append(
                        f"'{context}' 컨텍스트에서 부정적 감정이 빈번함 ({negative_count}/{len(emotions)})"
                    )

        return patterns

    def _analyze_triggers(
        self, situations: List[str], entries: List[Dict[str, Any]]
    ) -> List[Tuple[str, int, float]]:
        """Analyze situation triggers"""
        # Simple keyword-based analysis
        keywords = defaultdict(list)

        for i, situation in enumerate(situations):
            # Extract keywords (simple approach)
            words = situation.split()
            for word in words:
                if len(word) > 1:  # Skip single characters
                    keywords[word].append(entries[i].get("intensity", 5))

        # Calculate trigger strength
        triggers = []
        for keyword, intensities in keywords.items():
            if len(intensities) >= 2:  # Need multiple occurrences
                count = len(intensities)
                avg_intensity = sum(intensities) / count
                triggers.append((keyword, count, avg_intensity))

        # Sort by combination of frequency and intensity
        triggers.sort(key=lambda x: x[1] * x[2], reverse=True)
        return triggers

    def _analyze_tag_triggers(
        self, entries: List[Dict[str, Any]]
    ) -> List[Tuple[str, int, float]]:
        """Analyze tag-based triggers"""
        tag_data = defaultdict(list)

        for entry in entries:
            tags = entry.get("tags", [])
            intensity = entry.get("intensity", 5)

            for tag in tags:
                tag_data[tag].append(intensity)

        triggers = []
        for tag, intensities in tag_data.items():
            if len(intensities) >= 2:
                count = len(intensities)
                avg_intensity = sum(intensities) / count
                triggers.append((tag, count, avg_intensity))

        triggers.sort(key=lambda x: x[1] * x[2], reverse=True)
        return triggers

    def _get_time_slot(self, hour: int) -> str:
        """Convert hour to time slot description"""
        if 6 <= hour < 12:
            return "오전"
        elif 12 <= hour < 18:
            return "오후"
        elif 18 <= hour < 22:
            return "저녁"
        else:
            return "밤"

    def _get_emotion_color(self, emotion: str) -> str:
        """Get color for emotion visualization"""
        positive_emotions = [
            "기쁨",
            "만족",
            "자신감",
            "안도",
            "설렘",
            "평온",
            "행복",
            "감사",
        ]
        negative_emotions = [
            "스트레스",
            "불안",
            "좌절",
            "화남",
            "긴장",
            "피로",
            "걱정",
            "슬픔",
        ]

        if emotion in positive_emotions:
            return "green"
        elif emotion in negative_emotions:
            return "red"
        else:
            return "blue"
