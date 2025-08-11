import os
from typing_extensions import Literal
import openai
from pydantic import BaseModel
from typing import TypeVar


class VibesumResponse(BaseModel):
    result: int


class VibesumRequest(BaseModel):
    a: int
    b: int
    operation: Literal["add"] = "add"


def vibesum(a: int, b: int) -> int:
    return structured_output(
        content=VibesumRequest(a=a, b=b).model_dump_json(),
        response_format=VibesumResponse,
    ).result


T = TypeVar("T", bound=BaseModel)


def structured_output(
    content: str,
    response_format: T,
    model: str = "gpt-4o-mini",
) -> T:
    api_key = os.environ["OPENAI_API_KEY"]
    client = openai.OpenAI(api_key=api_key)

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": content,
                    },
                ],
            }
        ],
        response_format=response_format,
    )
    response_model = response.choices[0].message.parsed
    return response_model