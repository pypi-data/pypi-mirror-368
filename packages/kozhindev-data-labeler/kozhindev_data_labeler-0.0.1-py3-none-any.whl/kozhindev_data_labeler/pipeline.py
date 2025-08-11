import json
from typing import Any

import pandas as pd

from kozhindev_data_labeler.llm import LLMClient

class Pipeline:
    def __init__(
        self,
        data: dict,
        prompt: str,
        model_client: LLMClient
    ) -> None:
        self.data = data
        self.prompt = prompt
        self.model = model_client
        self.result: dict[str, Any] = None

    def _result_to_dict(self) -> None:
        try:
            self.result = json.loads(self.result)
        except json.decoder.JSONDecodeError as ex:
            print(f'Произошла ошибка при декодировании JSON: {ex}')

    def run(self) -> None:
        self.result = self.model.predict(f'{self.prompt}\n{self.data}')
        self._result_to_dict()

    def to_csv(self, filename: str) -> None:
        if not self.result:
            raise ValueError('Нет данных для сохранения')
        if not filename.endswith('.csv'):
            raise ValueError("Ожидался файл с расширением '.csv'")
        df = pd.DataFrame(self.result)
        df.to_csv(filename, index=False)
