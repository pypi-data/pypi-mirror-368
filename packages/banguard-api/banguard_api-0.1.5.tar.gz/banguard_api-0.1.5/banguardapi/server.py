from dataclasses import dataclass

@dataclass
class Server:
    id: str
    name: str

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_dict(cls, data: dict) -> 'Server':
        return cls(id=data["id"], name=data["name"])
