import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.web import SlackResponse

from bot import Conversions, Parser, convert_ts

# Parameters to toggle
CHANNEL_NAME = "first-jobs"
DELTA = Conversions.MS_DAY

start_month = 5
start_month_name = "may"
start = datetime(year=2022, month=start_month, day=1).timestamp()
end = datetime(year=2022, month=start_month + 1, day=1).timestamp()


if __name__ == "__main__":
    # load .env
    load_dotenv()

    # start log
    logging.basicConfig(
        format="%(levelname)s:%(asctime)s: %(message)s",
        filename=f"../logs/{start_month_name}_bot.log",
        encoding="utf-8",
        level=logging.CRITICAL,
    )

    # start client and logger
    client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

    # get list of channels
    channels: SlackResponse = client.conversations_list(limit=150)["channels"]  # type: ignore

    # start parser
    p = Parser(CHANNEL_NAME)

    # isolate channel metadata
    channel = p.get_channel_data(channels)

    while start < end:
        try:
            # pull channel data
            p.pull(client, channel, start, DELTA)

        except Exception as e:
            logging.critical(f"failed over {start}, {start + DELTA} ", e)

        else:
            logging.critical(
                f"Pulled from {convert_ts(start)} to {convert_ts(start + DELTA)}"
            )
            start += DELTA
