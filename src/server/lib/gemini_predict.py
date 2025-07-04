from slack_sdk import WebClient
from slack_sdk.web.slack_response import SlackResponse
from google import genai
from google.genai.types import GenerateContentConfig, Part, Content, Tool, GoogleSearch, ThinkingConfig


class GeminiPredict(object):

    def __init__(self,
                 api_key: str,
                 token: str | None = None,
                 channel: str | None = None,
                 ) -> None:
        """
        Args:
            api_key (str): GOOGLE_API_KEY
            token (str | None): SLACK_API_TOKEN
            channel (str | None): Channel ID of Slack
        Returns:
            None
        """
        self.api_key = api_key
        self.token = token
        self.channel = channel
        self.history_list: list[Content] = []
        self.tool_list: list[Tool] = [Tool(google_search=GoogleSearch())]
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
                    "text": f"{text}"
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
                  model: str = "gemini-2.5-flash",
                  temperature: float | None = None,
                  top_k: float | None = None,
                  top_p: float | None = None
                  ) -> str:
        """
        Args:
            user_prompt (str): user prompt
            model (str): model name
            temperature (float): Temperature
            top_k (float): Top K
            top_p (float): Top P

        Returns:
            response.text: str
        """
        # ToDo: Token数から履歴を削除する機能が必要
        self.history_list.append(
            Content(role="user", parts=[Part(text=user_prompt)]))
        self.model = model
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.thinking_config = ThinkingConfig(
            thinking_budget=-1) if "2.5" in self.model else None
        # Client
        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(model=self.model,
                                                  contents=self.history_list,
                                                  config=GenerateContentConfig(
                                                      tools=self.tool_list,
                                                      response_modalities=[
                                                          "TEXT"],
                                                      thinking_config=self.thinking_config,
                                                      temperature=self.temperature,
                                                      top_k=self.top_k,
                                                      top_p=self.top_p
                                                  )
                                                  )
        self.history_list.append(
            Content(role="model", parts=[Part(text=response.text)]))
        self.message = (
            f"*:innocent:Prompt:*\n```{user_prompt.split("ただし、以下のフォーマットとします。")[0]}```\n\n"
            f"*:hugging_face:Response:*\n{response.text}\n\n"
        )
        if self.token and self.channel:
            self.send_slack_message(self.message)
        return response.text
