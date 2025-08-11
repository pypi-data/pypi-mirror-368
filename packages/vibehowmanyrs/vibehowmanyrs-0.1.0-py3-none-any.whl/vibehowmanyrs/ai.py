import os
from typing_extensions import Literal
import openai
from pydantic import BaseModel
from typing import TypeVar


class VibehowmanyrsResponse(BaseModel):
    r_count: int


class VibehowmanyrsRequest(BaseModel):
    text: str
    letter: Literal["R"] = "R"
    case_sensitive: bool = False


def vibehowmanyrs(text: str) -> int:
    return structured_output(
        content=VibehowmanyrsRequest(text=text).model_dump_json(),
        response_format=VibehowmanyrsResponse,
    ).r_count


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