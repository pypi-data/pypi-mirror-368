from dataclasses import dataclass
from typing import Optional
from .server import Server
from .terraria_player import TerrariaPlayer


@dataclass
class Ban:
    id: int
    player: TerrariaPlayer
    category: str
    server: Optional[Server] = None

    def __str__(self):
        return f"Ban(player={self.player}, server={self.server}, category={self.category})"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_dict(cls, data: dict) -> "Ban":
        if isinstance(data.get("player"), TerrariaPlayer):
            player = data.get("player")
        else:
            player = TerrariaPlayer.from_dict(data.get("player"))

        if isinstance(data.get("server"), Server):
            server = data.get("server")
        else:
            server = Server.from_dict(data.get("server"))

        return cls(
            id=data.get("id"),
            player=player,
            category=data.get("category"),
            server=server,
        )
