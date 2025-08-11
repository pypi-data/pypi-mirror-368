import os
from openai import OpenAI
from pydantic import BaseModel
from typing import TypeVar, Type, Callable, Any


class AreYouSureResponse(BaseModel):
    vibe_check: bool

def vibe_check_it(fn: Callable[..., Any], *args, **kwargs) -> bool:
    vibe_output = fn(*args, **kwargs)

    prompt = (
        f"Function call: {fn.__name__}({', '.join(map(str, args))})\n"
        f"Output: {vibe_output}\n"
        "Are you sure this output is correct? Answer with a python bool: True or False"
    )

    return structured_output(
        prompt=prompt,
        response_format=AreYouSureResponse,
        model="gpt-5",
    ).vibe_check

T = TypeVar("T", bound=BaseModel)

def structured_output(
    prompt: str,
    response_format: Type[T],
    model: str = "gpt-5",
) -> T:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.parse(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
            response_format=response_format,
        )
        response_model = response.choices[0].message.parsed
        return response_model
    except Exception as e:
        raise RuntimeError(
            "This must be a user error. "
            "Please check your code. "
            "OpenAI would never let its downstream users down! "
            f"Exception: {e}"
        )

