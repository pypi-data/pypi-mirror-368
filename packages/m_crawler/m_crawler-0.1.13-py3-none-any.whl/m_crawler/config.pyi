from _typeshed import Incomplete

class PlayWeightConfig:
    executable_path: str
    channel: str
    args: Incomplete
    timeout: int
    env: dict[str, str | float | bool] | None
    headless: bool
    downloads_path: str
    slow_mo: int
    def __init__(self) -> None: ...
