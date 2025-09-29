import dotenv
import os

from openai import AsyncOpenAI
from evaluators.query_status import QueryStatus


dotenv.load_dotenv()

gen_cli = AsyncOpenAI(api_key=os.getenv('OPENAI_TOKEN'),
                      base_url=os.getenv('OPENAI_URL'))
assistant_id = os.getenv('OPENAI_ASSISTANT_ID')

async def evaluate_query(query: str,
                         item: str) -> QueryStatus:
  prompt = (
    f"Given the following data: {item}\n\n"
    f"Is the following query satisfied (yes or no): {query}"
  )
  thread_cont = {
    "messages": [
      {"role": "user", "content": prompt}
    ]
  }

  ret_val = QueryStatus.FAIL
  while ret_val == QueryStatus.FAIL:
    try:
      stream = await gen_cli.beta.threads.create_and_run(
        assistant_id=assistant_id,
        thread=thread_cont,
        stream=True,
        max_completion_tokens=8192
      )
    except Exception as excp:
      print(f"Exception: {excp}")
      ret_val = QueryStatus.FAIL
      continue

    ret_val = QueryStatus.MISS
    try:
      async for event in stream:
        if event.event == "thread.message.completed":
          event_cont = event.data.content
          if len(event_cont) == 0:
            print(f"*** Completion event has no content ***")
            ret_val = QueryStatus.FAIL
            break
          elif 'yes' in event_cont[0].text.value.lower():
            ret_val = QueryStatus.MATCH
            break
          else:
            ret_val = QueryStatus.MISS
    except Exception as excp:
      print(f"Failed to retrieve stream event: {excp}")
      ret_val = QueryStatus.FAIL

  return ret_val
