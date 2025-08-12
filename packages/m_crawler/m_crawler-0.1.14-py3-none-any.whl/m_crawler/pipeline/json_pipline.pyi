from m_crawler.pipeline.abstracy_pipeline import AbstractPipeline as AbstractPipeline
from typing import Any

class JsonPipeline(AbstractPipeline):
    def process_item(self, item: Any) -> Any: ...
