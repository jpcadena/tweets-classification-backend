"""
A module for cleaning in the app.utils.ml utils.text preprocessing package.
"""
import logging
import re
import string

logger: logging.Logger = logging.getLogger(__name__)


def remove_emoji(text: str) -> str:
    """
    Remove emojis from a text
    :param text: The text to remove emojis from
    :type text: str
    :return: The input text with emojis removed.
    :rtype: str
    """
    emoji_pattern: re.Pattern[str] = re.compile(
        "[" + "\U0001f600-\U0001f64f"  # emoticons
        + "\U0001f300-\U0001f5ff"  # symbols & pictographs
        + "\U0001f680-\U0001f6ff"  # transport & map symbols
        + "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        + "\U0001f900-\U0001f9ff"  # Unicode 9.0 emojis
        + "\U0001f980-\U0001f9ff"  # Unicode 10.0 emojis
        + "\U0001fa80-\U0001faff"  # Unicode 11.0 emojis
        + "\U0001fbc0-\U0001fbc9"  # Unicode 12.0 emojis
        + "\U0001fcc0-\U0001fcc9"  # Unicode 13.0 emojis
        + "\U0001fcd0-\U0001fcd9"  # Unicode 14.0 emojis
        + "\U0001fdd0-\U0001fdd9"  # Unicode 15.0 emojis
          "]+", flags=re.UNICODE)
    return emoji_pattern.sub("", text)


def twitter_text_cleaning(text: str) -> str:
    """
    Clean a text message that might have @mentions, "#" symbol or URLs
    :param text: The text message to clean
    :type text: str
    :return: The cleaned text message without @mentions, "#" and URLs
    :rtype: str
    """
    text = text.lower()
    text = re.sub(r"@[A-Za-z0-9]+", "", text)
    text = re.sub(r"@[A-Za-zA-Z0-9]+", "", text)
    text = re.sub(r"@[A-Za-z0-9_]+", "", text)
    text = re.sub(r"@[A-Za-z]+", "", text)
    text = re.sub(r"@[-)]+", "", text)
    text = re.sub(r"#", "", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"https?\/\/\S+", "", text)
    text = re.sub(r"http?\/\/\S+", "", text)
    text = re.sub(r"https?\/\/.*[\r\n]*", "", text)
    text = re.sub(r"^https?\/\/.*[\r\n]*", "", text)
    text = re.sub(r"^https?:\/\/.*[\r\n]*", "", text)
    return text


def remove_punc(message) -> str:
    """
    Remove punctuation from the given message.
    :param message: Text message that might have punctuations
    :type message: str
    :return: Message without punctuations
    :rtype: str
    """
    return "".join(
        [char for char in message if char not in string.punctuation])
