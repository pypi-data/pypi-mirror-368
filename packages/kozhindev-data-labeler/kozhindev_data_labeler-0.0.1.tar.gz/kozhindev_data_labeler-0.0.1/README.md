# Usage example
```python
from pydantic import BaseModel

from kozhindev_data_labeler import LLMClient
from kozhindev_data_labeler import Pipeline


class LLMPredict(BaseModel):
    reviews: list[str]
    target: list[int]

llm_client = LLMClient(
    model='gpt-4o-mini',
    api_key='API_KEY',
    response_format=LLMPredict
)

reviews = [
    'Сегодня отличная погода, настроение супер!',
    'SOME TEXT 123312!312OKF;SEKF;',
    'PostgreSQL- свободная объектно-реляционная базами данных',
    "Congratulations! You've won a $1,000 Walmart gift card to http://bit.ly/123456 tp claim now."
]

pipeline = Pipeline(
    data={'reviews': reviews},
    prompt='Сделай классификацию сообщений на негативные и позитивные (0 - позитивный, 1 - негативный)',
    model_client=llm_client
)

pipeline.run()
pipeline.to_csv('result.csv')
```