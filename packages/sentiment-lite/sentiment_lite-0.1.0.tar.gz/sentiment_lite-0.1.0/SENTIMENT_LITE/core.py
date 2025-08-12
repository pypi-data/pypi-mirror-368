#sentiment analysis logic
positive_words = [
    "good", "great", "excellent", "amazing", "happy", "love", "fantastic", "positive", "wonderful", "best"
]

negative_words = [
    "bad", "terrible", "awful", "horrible", "sad", "hate", "poor", "worst", "negative", "angry"
]

neutral_words = [
    "okay", "fine", "average", "medium", "neutral", "so-so", "fair", "ordinary", "standard", "passable"
]


def analyze_sentiment(text):
    """
    Analyze sentiment of the given text based on word matching.

    Returns:
        dict: {
            'score': int,
            'label': 'positive' | 'negative' | 'neutral'
        }
    """
    text = text.lower().split()
    pos_count = sum(word in positive_words for word in text)
    neg_count = sum(word in negative_words for word in text)
    neu_count = sum(word in neutral_words for word in text)

    if pos_count > neg_count and pos_count > neu_count:
        return {"score": pos_count - neg_count, "label": "positive"}
    elif neg_count > pos_count and neg_count > neu_count:
        return {"score": neg_count - pos_count, "label": "negative"}
    else:
        return {"score": 0, "label": "neutral"}
