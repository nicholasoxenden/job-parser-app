import csv
import json
import re
from pathlib import Path
from datetime import datetime
from glob import glob


class Row:
    """Class designed to represent data parsed from days_data json files"""

    def __init__(self) -> None:
        self._shift_id = None
        self._email = None
        self._reaction_emote = None
        self._reaction_user = None
        self._bot_msg_ts = None
        self._reply_text = None
        self._reply_user = None
        self._reply_ts = None

    def __str__(self) -> str:
        return f"[{self._shift_id}, {self._email}, {self._reaction_emote}, {self._reaction_user},  {self._bot_msg_ts}, {self._reply_text}, {self._reply_user}, {self._reply_ts}]"

    def to_list(self):
        """Method writes class attributes to list

        Returns
        -------
        list
            list of class attributes
        """
        return [
            self._shift_id,
            self._email,
            self._reaction_emote,
            self._reaction_user,
            self._bot_msg_ts,
            self._reply_text,
            self._reply_user,
            self._reply_ts,
        ]

    def to_dict(self):
        """Method writes class attributes to dictionary

        Depends on self.headers() and self.to_list()

        Returns
        -------
        dict
            dictionary of class attributes
        """
        return {k: v for k, v in zip(self.headers(), self.to_list())}

    @staticmethod
    def headers():
        return [
            "shift_id",
            "email",
            "reaction_emote",
            "reaction_user",
            "bot_msg_ts",
            "reply_text",
            "reply_user",
            "reply_ts",
        ]

    @property
    def shift_id(self):
        return self._shift_id

    @shift_id.setter
    def shift_id(self, value):
        self._shift_id = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value: str | None):
        self._email = value

    @property
    def reaction_emote(self):
        return self._reaction_emote

    @reaction_emote.setter
    def reaction_emote(self, value: str):
        self._reaction_emote = value

    @property
    def reaction_user(self):
        return self._reaction_user

    @reaction_user.setter
    def reaction_user(self, value: list):
        if len(value) > 1:
            self._reaction_user = ";".join(value)
        elif len(value) == 1:
            self._reaction_user = value[0]
        else:
            self._reaction_user = None

    @property
    def bot_msg_ts(self):
        return self._bot_msg_ts

    @bot_msg_ts.setter
    def bot_msg_ts(self, value: float):
        self._bot_msg_ts = datetime.fromtimestamp(float(value)).isoformat(" ")

    @property
    def reply_text(self):
        return self._reply_text

    @reply_text.setter
    def reply_text(self, value: str):
        self._reply_text = value

    @property
    def reply_user(self):
        return self._reply_user

    @reply_user.setter
    def reply_user(self, value: str):
        self._reply_user = value

    @property
    def reply_ts(self):
        return self._reply_ts

    @reply_ts.setter
    def reply_ts(self, value: float):
        self._reply_ts = datetime.fromtimestamp(float(value)).isoformat(" ")


class FilePath:
    def __init__(self, path: str) -> None:
        self.path = Path(path)

    def csv_stem(self) -> str:
        return self.path.stem + ".csv"


def load_json(filepath):
    with open(filepath, "r") as f:
        return json.load(f)


def re_email(msg: dict) -> str | None:
    """Function written to parse emails from dictionary input

    Parameters
    ----------
    msg : dict
        input ductionary

    Returns
    -------
    str | None
        returns email if found, None otherwise
    """
    email = re.findall(r":(\S+@+\S+)(?=\|)", msg["text"])
    if len(email) > 0:
        return email[0]
    else:
        return None


def re_shift_id(msg: dict) -> int | None:
    """Function written to parse emails from dictionary input

    Would be good to test.

    Parameters
    ----------
    msg : dict
        input dictionary

    Returns
    -------
    str | None
        returns shift id if found, None otherwise
    """
    re_match = re.findall(r"\<(.*?)\>", msg["text"])
    if len(re_match) > 0:
        url = re_match[0]
        if "/" not in url:
            return None
        else:
            id = url.split("/")[-1]
            try:
                id = int(id)
            except TypeError:
                id = None
            return id
    else:
        return None


def parse_json(filepath):
    # load conversations
    conversations = load_json(filepath)

    # loop through conversations
    data: list[Row] = []
    for conversation in conversations:
        row = Row()

        # search for email, reaction in first item
        if len(conversation) > 0:
            first = conversation[0]
            reaction_list: list = first.get("reactions")

            row.email = re_email(first)
            row.shift_id = re_shift_id(first)

            if reaction_list and len(reaction_list) > 0:
                reaction = reaction_list[0]
                row.reaction_emote = reaction.get("name")
                row.reaction_user = reaction.get("users")
                row.bot_msg_ts = first.get("ts")

        # search for reply text, if any
        if len(conversation) > 1:
            reply = conversation[1]
            row.reply_text = reply.get("text")
            row.reply_user = reply.get("user")
            row.reply_ts = reply.get("ts")

        data.append(row)
    return data


def write_to_csv(rows: list[Row], filepath: str):
    """Function writes list of Row objects to csv file

    Parameters
    ----------
    rows : list[Row]
        list holding row data
    filepath : str
        outpath for csv file
    """
    with open(filepath, "w") as f:
        writer = csv.DictWriter(f, fieldnames=Row.headers())
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_dict())
    print("File written to {}".format(filepath))


if __name__ == "__main__":
    base_dir_path = ""
    files = glob(base_dir_path + "/*.json")

    for file in files:
        in_path = FilePath(file)
        data = parse_json(in_path.path)
        write_to_csv(data, "../out/{}".format(in_path.csv_stem()))
