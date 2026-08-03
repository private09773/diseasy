"""
diseasy/presence.py (v0.1.1a)

Bot presence/activity — Playing, Watching, Listening, and Custom
status. Wire set_presence() into your gateway's PRESENCE_UPDATE
payload builder (sent as part of IDENTIFY or a later gateway op 3).
"""

ACTIVITY_TYPES = {
    "playing": 0,
    "streaming": 1,
    "listening": 2,
    "watching": 3,
    "custom": 4,
    "competing": 5,
}


class Activity:
    def __init__(self, type: str, name: str, state: str = None):
        if type not in ACTIVITY_TYPES:
            raise ValueError(f"Unknown activity type: {type}")
        self.type = type
        self.name = name
        self.state = state  # used for custom status text

    def to_payload(self):
        payload = {
            "name": self.name,
            "type": ACTIVITY_TYPES[self.type],
        }
        if self.type == "custom" and self.state:
            payload["state"] = self.state
        return payload


def playing(name):
    return Activity("playing", name)


def watching(name):
    return Activity("watching", name)


def listening(name):
    return Activity("listening", name)


def custom_status(text, emoji=None):
    """
    Custom status — the kind users set themselves, e.g. 'Building Diseasy'.
    emoji is optional and expected as a unicode emoji string for now;
    custom guild emoji support can be layered in later.
    """
    activity = Activity("custom", text, state=text)
    if emoji:
        activity.emoji = emoji
    return activity


def build_presence_payload(activity: Activity, status: str = "online"):
    """
    status: 'online', 'idle', 'dnd', or 'invisible'
    Returns the payload shape Discord expects on the gateway.
    """
    return {
        "since": None,
        "activities": [activity.to_payload()] if activity else [],
        "status": status,
        "afk": False,
    }
