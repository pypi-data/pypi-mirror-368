from playwright.sync_api import sync_playwright
from m_crawler.config import PlayWeightConfig
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

    def download(self, request: AbstractRequest) -> AbstractResponse:
        """
        playweight 核心逻辑
        """
        # 确保传入的是 PlayWeightRequest 类型
        if not isinstance(request, PlayWeightRequest):
            raise TypeError("request must be an instance of PlayWeightRequest")
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=self.settings.executable_path,
                channel=self.settings.channel,
                args=self.settings.args,
                timeout=self.settings.timeout,
                env=self.settings.env,
                headless=self.settings.headless,
                downloads_path=self.settings.downloads_path,
                slow_mo=self.settings.slow_mo,
            )
            context = browser.new_context()
            page = context.new_page()
            try:
                page.goto(request.url)
                for action in request.actions:
                    action(page)
                return BaseResponse(request, page.content(), True)
            except Exception as e:
                logger.error(f"URL:{request.url} failed, error:{e}")
                return BaseResponse(request, None, False)
