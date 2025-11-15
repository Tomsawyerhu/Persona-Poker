from typing import List


class Event:
    def __init__(self, player_name: str, event_content: str):
        self.player_name = player_name
        self.event_content = event_content  # 如 "fold", "check", "raise"

    def __repr__(self):
        return f"<Player={self.player_name} Action={self.event_content}'>"


class Memory:
    def __init__(self, events: List[Event] = None):
        self.events = events if events is not None else []

    def add_event(self, event: Event):
        """Add a new event to memory."""
        self.events.append(event)

    def __repr__(self):
        result = ''
        for event in self.events:
            result += str(event) + '\n'
        return result
