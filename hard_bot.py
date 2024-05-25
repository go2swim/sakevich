from bot import Bot


class HardBot(Bot):
    def __init__(self, name: str, server_addr: tuple[str, int]):
        super().__init__(name, server_addr)

    def play(self) -> None:
        print()
        print('Hard bot start play')
        print()