class AnimeException(Exception):
    def __init__(self, message: str, metodo: str, source: str = "AnimeFLV"):
        self.metodo = metodo
        self.source = source
        self.message = message
        super().__init__(
            f"{self.message} - Metodo: {self.metodo} - Sorce: {self.source}"
        )
