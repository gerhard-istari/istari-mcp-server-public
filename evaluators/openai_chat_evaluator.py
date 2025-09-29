import dotenv
import os

from openai import AsyncOpenAI
from shared.query_status import QueryStatus


dotenv.load_dotenv()

ai_model_var_name = 'OPENAI_MODEL'
if ai_model_var_name in os.environ:
  ai_model = os.getenv(ai_model_var_name)
else:
  ai_model = 'gps-oss-120b'

client = AsyncOpenAI(base_url=os.getenv('OPENAI_URL'),
                     api_key=os.getenv('OPENAI_TOKEN'))


async def evaluate_query(query: str,
                         item: str) -> QueryStatus:
  prompt = (
    f"Given the following data: {item}\n\n"
    f"Is the following query satisfied (yes or no): {query}"
  )
  resp = await client.chat.completions.create(
    model=ai_model,
    messages={"role": "user", "content": prompt},
    max_completion_tokens=32768
  )
  print(json.dumps(resp))
