import json
from datetime import datetime
from math import floor

from slack_sdk import WebClient
from slack_sdk.web import SlackResponse


def convert_ts(ts: int | float) -> str:
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%m_%d_%Y")


# basic conversions
class Conversions:
    MS_WEEK = 604800
    MS_DAY = MS_WEEK / 7
    JUNE_1 = 1654063200.0
    JULY_1 = 1656655200.0
    AUGUST_1 = 1659333600.0
    SEPTEMBER_1 = 1662012000.0
    OCTOBER_1 = 1664604000.0
    NOVEMBER_1 = 1667282400.0


class Parser:
    def __init__(self, channel_name) -> None:
        self.channel_name = channel_name

    def pull(self, client, channel: dict, start, delta):
        # get conversation history
        # update limit as required
        result = client.conversations_history(
            channel=channel["id"],  # type: ignore
            oldest=str(start),
            latest=str(start + delta),
            inclusive=True,
            limit=1000,
        )

        if result["has_more"] is True:
            raise Exception("Didn't get it all")

        # parse conversation threads
        threads = self.parse_threads(client, channel, result)

        # clean list of lists
        # holding msg dictionaries
        parsed = self.clean_threads(threads)

        # write parsed messages
        channel_name = channel["name"]
        with open(
            f"../days_data/{channel_name}_{int(start)}_{int(start + delta)}.json", "w"
        ) as f:
            json.dump(parsed, f)

    def get_channel_data(self, channel_list: SlackResponse) -> dict:
        # get first-jobs channel
        first_jobs = dict()
        for channel in channel_list:
            # find the desired channel
            if channel["name"] == self.channel_name:
                # save data in first_jobs
                first_jobs: dict = channel  # type: ignore
        return first_jobs

    def parse_threads(
        self, client: WebClient, channel, message_container, check_reply=False
    ):
        # parse messages
        threads: list[list[dict]] = []
        for m in message_container["messages"]:  # type: ignore
            # get messages
            reply = client.conversations_replies(channel=channel["id"], ts=m["ts"], limit=None)  # type: ignore
            reply_messages: list[dict[str, str]] = reply["messages"]  # type: ignore

            if check_reply:
                # check to see if message has reply
                if len(reply_messages) > 1:
                    # if so, add to replies
                    threads.append(reply_messages)
            # else append all messages
            threads.append(reply_messages)
        return threads

    def clean_threads(self, data: list[list[dict]]) -> list[list[dict]]:
        """Accepts a list of lists of dictionaries
        and returns a condensed list holding data
        corresponding to the local fields variable.

        Parameters
        ----------
        data : list[list[dict]]
            Data yielded from parsing conversation replies

        Returns
        -------
        list[list[dict]]
            Condensed list
        """
        fields = ["type", "subtype", "text", "reactions", "user", "ts"]
        new = []
        for conv in data:
            conv_list = []
            for msg in conv:
                d = {}
                for f in fields:
                    d[f] = msg.get(f)
                conv_list.append(d)
            new.append(conv_list)
        return new

    @staticmethod
    def convert_ts(ts: float) -> datetime:
        """Converts Slack's timestamp"""
        return datetime.fromtimestamp(floor(ts))

    @staticmethod
    def convert_dt(dt: datetime):
        return dt.timestamp()
