from dataclasses import dataclass, field


@dataclass
class Character:
    name: str = "name"
    voice_id: str = "voice_id"
    gender: str = "m"

    def __post_init__(self) -> None:
        if self.gender not in ("m", "f"):
            raise ValueError("gender must be 'm' or 'f'")


@dataclass
class Group:
    name: str | None = None
    folder: str | None = None
    characters: list[Character] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.characters)
