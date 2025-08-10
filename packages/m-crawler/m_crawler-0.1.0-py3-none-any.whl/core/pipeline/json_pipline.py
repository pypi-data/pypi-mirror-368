import json
from typing import Any
from core.pipeline.abstracy_pipeline import AbstractPipeline


class JsonPipeline(AbstractPipeline):

    def process_item(self, item: Any) -> Any:
        json_item = json.dumps(item, ensure_ascii=False)
        print(json_item)
