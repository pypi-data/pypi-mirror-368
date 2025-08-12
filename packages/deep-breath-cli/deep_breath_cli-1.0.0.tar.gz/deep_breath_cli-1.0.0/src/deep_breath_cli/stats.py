import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any


class StatsManager:
    def __init__(self):
        """Initialize the stats manager and load existing stats."""
        self.config_dir = Path.home() / ".config" / "deep-breath-cli"
        self.stats_file = self.config_dir / "stats.json"
        self.data = self._load_stats()

    def _load_stats(self) -> dict[str, Any]:
        """Load stats from JSON file or create default structure."""
        if not self.stats_file.exists():
            print("Stats file not found, creating default stats.")
            self.config_dir.mkdir(parents=True, exist_ok=True)
            default_data = {
                "total_sessions": 0,
                "total_time_seconds": 0,
                "patterns_used": {"4-7-8": 0, "4-4-4-4": 0},
                "sessions": [],
                "streaks": {"current": 0, "longest": 0},
            }
            # Save default data
            with open(self.stats_file, "w") as f:
                json.dump(default_data, f, indent=2)
            return default_data
        else:
            # Load existing stats
            try:
                with open(self.stats_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading stats file: {e}")
                print("Creating fresh stats file.")
                # Recreate the stats file if there's an error
                return self._load_stats()

    def _save_stats(self) -> None:
        """Save current stats to JSON file."""
        try:
            with open(self.stats_file, "w") as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            print(f"Error saving stats file: {e}")

    def add_session(self, pattern: str, cycles: int, duration_seconds: int) -> None:
        """Add a completed breathing session to stats."""
        # Add session data to the sessions list
        session = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "pattern": pattern,
            "cycles": cycles,
            "duration_seconds": duration_seconds,
        }
        self.data["sessions"].append(session)
        # Increment total sessions and time
        self.data["total_sessions"] += 1
        self.data["total_time_seconds"] += duration_seconds
        # Increment pattern usage
        # self.data["patterns_used"][pattern] = self.data["patterns_used"].get(pattern, 0) + 1
        if pattern in self.data["patterns_used"]:
            self.data["patterns_used"][pattern] += 1
        else:
            self.data["patterns_used"][pattern] = 1
        # Update streaks
        current_streak = self._calculate_streak()
        self.data["streaks"]["current"] = current_streak
        if current_streak > self.data["streaks"]["longest"]:
            self.data["streaks"]["longest"] = current_streak
        # Save updated stats
        self._save_stats()

    def get_display_stats(self) -> str:
        """Format stats for display in terminal."""
        if self.data["total_sessions"] == 0:
            return "No breathing sessions recorded yet.\nStart your first session with 'breath start' to begin tracking your progress!"

        # Calculate total time in a user-friendly format
        total_time_seconds = self.data["total_time_seconds"]
        total_time_minutes = total_time_seconds // 60

        if total_time_minutes < 1:
            time_display = f"{total_time_seconds} seconds"
        elif total_time_minutes < 60:
            time_display = f"{total_time_minutes} minutes"
        else:
            hours = total_time_minutes // 60
            minutes = total_time_minutes % 60
            time_display = f"{hours}h {minutes}min"

        # Get the favorite pattern
        if self.data["patterns_used"]:
            favorite_pattern = max(
                self.data["patterns_used"], key=self.data["patterns_used"].get
            )
            favorite_count = self.data["patterns_used"][favorite_pattern]

        return f"""Your Breathing Stats
            Total sessions: {self.data["total_sessions"]}
            Total time: {time_display}
            Favorite pattern: {favorite_pattern} ({favorite_count} sessions)
            Current streak: {self.data["streaks"]["current"]} days"""

    def _calculate_streak(self) -> int:
        """Calculate current streak of consecutive days."""
        if not self.data["sessions"]:
            return 0  # No sessions means no streak

        # Get the unique dates from sessions
        unique_dates = set(session["date"] for session in self.data["sessions"])

        # Convert dates to datetime objects
        date_objects = [datetime.strptime(date, "%Y-%m-%d") for date in unique_dates]

        # Sort dates in descending order
        date_objects.sort(reverse=True)

        # Check if the last session was today
        today = datetime.now().date()
        if date_objects[0].date() != today:
            return 0  # Streak broken if last session is not today

        # Count consecutive days
        streak = 1
        expected_date = today

        for i in range(1, len(date_objects)):
            expected_date -= timedelta(days=1)  # Move to the previous day

            if date_objects[i].date() == expected_date:
                streak += 1  # Increment streak if the date matches
            else:
                break  # Stop counting if a day is missing

        return streak
