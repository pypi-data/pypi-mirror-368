class MaxRetryTimeException(Exception):
    def __init__(self, message: str = "Max retry count reached") -> None:
        super().__init__(message)
