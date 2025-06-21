import re
from slack_sdk import WebClient
from slack_sdk.web.slack_response import SlackResponse
from google import genai
from google.genai.types import GenerateContentConfig, Part, Content, Tool, GoogleSearch


class GeminiPredict(object):

    def __init__(self,
                 api_key: str,
                 token: str,
                 channel: str,
                 model: str = "gemini-2.0-flash",
                 ) -> None:
        """
        Args:
            api_key (str): GOOGLE_API_KEY
            token (str): SLACK_API_TOKEN
            channel (str): Channel ID of Slack
            model (str): Gemini model name
        Returns:
            None
        """
        self.api_key = api_key
        self.token = token
        self.channel = channel
        self.model = model
        self.history_list: list[Content] = []
        self.tool_list: list[Tool] = [Tool(google_search = GoogleSearch())]
        self.slack_client = WebClient(token=self.token)

    def send_slack_message(self,
                        text: str,
                        ) -> SlackResponse:
        """
        Args:
            text (str): text which you want to send Slack

        Returns:
            SlackResponse: Response
        """
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":crystal_ball: *Gemini Model Response*"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{text.replace("*   ", "* ").replace("   *", " *")}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Model: `{self.model}`"
                    }
                ]
            }
        ]
        response = self.slack_client.chat_postMessage(
            channel=self.channel,
            text="Geminiモデルの出力結果です",
            blocks=blocks
        )
        return response

    def ask_model(self,
                user_prompt: str,
                temperature: float = 0.2,
                top_k: float = 20,
                top_p: float = 0.6
                ) -> str:
        """
        Args:
            user_prompt (str): User's prompt
        
        Returns:
            response.text: str
        """
        self.history_list.append(Content(role="user", parts=[Part(text=user_prompt)]))

        # Client
        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(model=self.model,
                                                contents=self.history_list,
                                                config=GenerateContentConfig(
                                                    tools=self.tool_list,
                                                    response_modalities=["TEXT"],
                                                    temperature=temperature,
                                                    top_k=top_k,
                                                    top_p=top_p
                                                    )
                                                )
        self.history_list.append(Content(role="model", parts=[Part(text=response.text)]))
        self.message = (
            f"*Prompt:*\n```{user_prompt}```\n\n"
            f"*Response:*\n{response.text}\n\n"
        )
        print(self.message)
        self.send_slack_message(self.message)
        return response.text