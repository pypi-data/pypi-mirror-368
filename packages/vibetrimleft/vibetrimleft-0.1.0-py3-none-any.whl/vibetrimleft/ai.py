import os
from typing_extensions import Literal
import openai
from pydantic import BaseModel
from typing import TypeVar


class VibetrimleftResponse(BaseModel):
    trimmed_text: str


class VibetrimleftRequest(BaseModel):
    text: str
    operation: Literal["lstrip"] = "lstrip"


def vibetrimleft(text: str) -> str:
    return structured_output(
        content=VibetrimleftRequest(text=text).model_dump_json(),
        response_format=VibetrimleftResponse,
    ).trimmed_text


T = TypeVar("T", bound=BaseModel)


def structured_output(
    content: str,
    response_format: T,
    model: str = "gpt-4o-mini",
) -> T:
    api_key = os.environ["OPENAI_API_KEY"]
    client = openai.OpenAI(api_key=api_key)

    response = client.beta.chat.completiclearons.parse(
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