class NotFoundError(Exception):
    def __init__(self, detail: str = "Not found"):
        self.detail = detail
