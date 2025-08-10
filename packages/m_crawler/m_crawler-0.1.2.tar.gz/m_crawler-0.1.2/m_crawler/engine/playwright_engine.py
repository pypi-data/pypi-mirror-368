from typing import Optional
from playwright.sync_api import sync_playwright
from playwright.sync_api import BrowserContext, Playwright, Browser
from config import PlayWeightConfig
from loguru import logger
from m_crawler.engine.abstract_engine import AbstractEngine
from m_crawler.engine.abstract_request import AbstractRequest
from m_crawler.engine.abstract_response import AbstractResponse
from m_crawler.engine.request import PlayWeightRequest
from m_crawler.engine.response import BaseResponse


class PlayWeightEngine(AbstractEngine):
    __slots__ = ("__playwright", "browser", "browser_context", "settings")
    """
    下载引擎
    """

    def __init__(self, settings: PlayWeightConfig) -> None:
        self.settings = settings
        self.__playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None

        self.browser_context: Optional[BrowserContext] = None

    def __init_context(self) -> None:
        self.__playwright = sync_playwright().start()
        self.browser = self.__playwright.chromium.launch(
            executable_path=self.settings.executable_path,
            channel=self.settings.channel,
            args=self.settings.args,
            timeout=self.settings.timeout,
            env=self.settings.env,
            headless=self.settings.headless,
            downloads_path=self.settings.downloads_path,
            slow_mo=self.settings.slow_mo,
        )
        self.browser_context = self.browser.new_context()

    def download(self, request: AbstractRequest) -> AbstractResponse:
        """
        playweight 核心逻辑
        """
        # 确保传入的是 PlayWeightRequest 类型
        if not isinstance(request, PlayWeightRequest):
            raise TypeError("request must be an instance of PlayWeightRequest")
        self.__init_context()
        if not self.browser_context:
            raise ValueError("browser_context is not initialized")
        try:
            new_page = self.browser_context.new_page()
            new_page.goto(request.url)
            for action in request.actions:
                action(new_page)
            return BaseResponse(request, new_page.content(), True)
        except Exception as e:
            logger.error(f"URL:{request.url} failed, error:{e}")
            return BaseResponse(request, None, False)

    def after_download_hook(self, result: AbstractResponse) -> AbstractResponse:
        self.__browser_close()
        return result

    def __browser_close(self):
        if self.browser_context:
            self.browser_context.close()
        if self.browser:
            self.browser.close()
