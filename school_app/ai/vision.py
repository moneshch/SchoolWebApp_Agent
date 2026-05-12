import base64

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage


vision_model = ChatOllama(
    model="qwen2.5vl:7b",
    temperature=0
)


def analyze_image(image_path, prompt):

    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(
            f.read()
        ).decode("utf-8")

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url":
                f"data:image/png;base64,{image_base64}"
            }
        ]
    )

    response = vision_model.invoke([message])

    return response.content