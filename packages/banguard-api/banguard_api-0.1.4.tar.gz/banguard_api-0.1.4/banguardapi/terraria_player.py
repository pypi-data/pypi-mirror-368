from dataclasses import dataclass


@dataclass
class TerrariaPlayer:
    id: str
    latest_name: str
    terraria_uuid: str

    def __str__(self):
        return self.latest_name

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_dict(cls, data: dict) -> "TerrariaPlayer":
        return cls(
            id=data.get("id"),
            latest_name=data.get("latest_name"),
            terraria_uuid=data.get("terraria_uuid")
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "latest_name": self.latest_name,
            "terraria_uuid": self.terraria_uuid
        }
