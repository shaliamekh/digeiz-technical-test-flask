from dataclasses import dataclass


@dataclass
class Mall:
    name: str
    id: int | None = None
