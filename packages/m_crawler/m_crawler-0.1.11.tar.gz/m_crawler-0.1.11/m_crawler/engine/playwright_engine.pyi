from _typeshed import Incomplete
from m_crawler.config import PlayWeightConfig as PlayWeightConfig
from m_crawler.engine.abstract_engine import AbstractEngine as AbstractEngine
from m_crawler.engine.abstract_request import AbstractRequest as AbstractRequest
from m_crawler.engine.abstract_response import AbstractResponse as AbstractResponse
from m_crawler.engine.request import PlayWeightRequest as PlayWeightRequest
from m_crawler.engine.response import BaseResponse as BaseResponse
from playwright.sync_api import Browser as Browser, BrowserContext as BrowserContext, Playwright as Playwright

class PlayWeightEngine(AbstractEngine):
    settings: Incomplete
    browser: Browser | None
    browser_context: BrowserContext | None
    def __init__(self, settings: PlayWeightConfig) -> None: ...
    def download(self, request: AbstractRequest) -> AbstractResponse: ...
    def after_download_hook(self, result: AbstractResponse) -> AbstractResponse: ...
