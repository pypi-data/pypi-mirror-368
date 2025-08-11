import enum

class EventType(enum.Enum):
    page_closed = "page_closed"
    page_loaded = "page_loaded"

    @classmethod
    def from_str(cls, event_name: str):
        for event in cls:
            if event.value == event_name:
                return event
        raise ValueError(f"Event {event_name} is not defined.")
