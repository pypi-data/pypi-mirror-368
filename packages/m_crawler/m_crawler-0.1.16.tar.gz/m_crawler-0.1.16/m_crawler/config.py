from typing import Dict, Optional, Union


class PlayWeightConfig:
    __slots__ = (
        "executable_path",
        "channel",
        "args",
        "timeout",
        "env",
        "headless",
        "downloads_path",
        "slow_mo",
    )

    def __init__(self) -> None:
        # 浏览器启动路径
        self.executable_path = r"/opt/google/chrome/google-chrome"
        # chromium, chrome, chrome-beta, chrome-dev...
        self.channel = "chromium"
        # 浏览器启动参数
        self.args = [
            "--disable-blink-features=AutomationControlled",
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        ]
        # 浏览器启动超时时间，单位 ms
        self.timeout = 10000
        # 环境变量
        self.env: Optional[Dict[str, Union[str, float, bool]]] = None
        # headless 模式
        self.headless = True
        # download 下载地址，不指定当触发下载时将现在到临时目录，且在退出时删除
        self.downloads_path = ""
        # 运行速度减慢指定的毫秒数
        self.slow_mo = 0
