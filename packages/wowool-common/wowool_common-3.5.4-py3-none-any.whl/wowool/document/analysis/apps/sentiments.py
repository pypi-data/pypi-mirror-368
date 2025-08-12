"""
Sentiment API Wrapper classes
"""

# {"positive": positive, "negative": negative, "sentiments": sentiments},

from dataclasses import dataclass, field


@dataclass
class Sentiment:
    """Represents a sentiment-bearing expression found in text.

    Contains information about a specific sentiment expression including its
    polarity, location, and linguistic components that contribute to the sentiment.

    Attributes:
        polarity (str): The sentiment polarity (e.g., 'positive', 'negative', 'neutral').
        text (str): The actual text content of the sentiment expression.
        begin_offset (int): Starting character position of the sentiment expression.
        end_offset (int): Ending character position of the sentiment expression.
        object (str|None): The object of the sentiment, if identified. Defaults to None.
        adjective (str|None): Sentiment-bearing adjective, if present. Defaults to None.
        expression (str|None): The sentiment expression phrase, if identified. Defaults to None.
        comp (str|None): Comparative element in the sentiment, if present. Defaults to None.
        verb (str|None): Sentiment-bearing verb, if identified. Defaults to None.
    """

    polarity: str
    text: str
    begin_offset: int
    end_offset: int
    object: str | None = None
    adjective: str | None = None
    expression: str | None = None
    comp: str | None = None
    verb: str | None = None


@dataclass
class SentimentResults:
    """Complete sentiment analysis results for a document.

    Contains overall sentiment scores and detailed information about individual
    sentiment expressions found throughout the document.

    Attributes:
        positive (float): Overall positive sentiment score for the document (0.0 to 1.0).
        negative (float): Overall negative sentiment score for the document (0.0 to 1.0).
        locations (list[Sentiment]): List of individual sentiment expressions found
            in the document with their locations and linguistic details. Defaults to empty list.
    """

    positive: float
    negative: float
    locations: list[Sentiment] = field(default_factory=list)


def convert_sentiments(jo_sentiments: dict) -> SentimentResults:

    sentiments = SentimentResults(
        positive=jo_sentiments.get("positive", 0.0),
        negative=jo_sentiments.get("negative", 0.0),
    )

    for s in jo_sentiments["locations"]:
        sentiment = Sentiment(
            polarity=s["polarity"],
            text=s["text"],
            begin_offset=s["begin_offset"],
            end_offset=s["end_offset"],
            object=s.get("object"),
            adjective=s.get("adjective"),
            expression=s.get("expression"),
            comp=s.get("comp"),
            verb=s.get("verb"),
        )
        sentiments.locations.append(sentiment)
    return sentiments
