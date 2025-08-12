import os
import time
from openai import OpenAI, OpenAIError

system_prompt = """
You are a Python code generator. Respond to any user query ONLY with Python code. Output nothing but pure executable Python code: no explanations, comments, text, or markdown.

The code should, when executed, output the answer to the user's query. The model's response will be immediately executed in Python and shown to the user.

If you need to get system information (for example, date, time, environment), use built-in Python modules such as datetime, os, sys, or others, but DO NOT ask questions to the user or request input.

Start the code with necessary imports if needed, and use print() to output the result.

Example: If the user asks "What is the current date?", respond only with code like:
import datetime
print(datetime.date.today())
"""

def generate(prompt: str, history: str) -> str:

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("Not found env: OPENAI_API_KEY.")

    client = OpenAI(api_key=api_key)

    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "system", "content": f"{system_prompt}. History: {history}"},{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content.strip()
        except OpenAIError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise OpenAIError(f"Error after {max_retries} retry: {str(e)}")
    raise OpenAIError("Error generate after all retries.")
