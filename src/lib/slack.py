from slack_sdk import WebClient
from slack_sdk.web.slack_response import SlackResponse


def send_slack_message(text: str,
                       token: str,
                       channel: str
                       ) -> SlackResponse:
    """
    Args:
        text (str): text which you want to send Slack
        token (str): Slack's token
        channel (str): Slack's channel name

    Returns:
        SlackResponse: Response
    """
    client = WebClient(token=token)
    response = client.chat_postMessage(
        channel=channel,
        text=text
    )
    return response