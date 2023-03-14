
class InvalidConfiguration(RuntimeError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NoConfigFound(RuntimeError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)