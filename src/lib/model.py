from google import genai
from google.genai.types import GenerateContentConfig, Part, Content, Tool


def ask_model(api_key: str,
              user_prompt: str,
              history: list[Content] | None = None,
              tools: list[Tool] | None = None,
              model: str = "gemini-2.5-flash-preview-04-17"
              ) -> str:
    """
    Args:
        user_prompt (str): User's prompt
        model (str): model name

    Returns:
        response.text (str): Gen AI's answer
    """
    history.append(Content(role="user", parts=[Part(text=user_prompt)]))
    # Client
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model, 
                                              contents=history,
                                              config=GenerateContentConfig(
                                                tools=tools,
                                                response_modalities=["TEXT"],
                                                )
                                            )
    history.append(Content(role="model", parts=[Part(text=response.text)]))
    return f"\n\n---\n{user_prompt}\n---\n\n{response.text}\n---\nFrom: {model}\n---"