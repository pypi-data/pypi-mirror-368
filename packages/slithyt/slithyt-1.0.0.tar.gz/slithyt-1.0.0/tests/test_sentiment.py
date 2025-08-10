from slithyt import sentiment

def test_sentiment_inversion():
    """
    Tests that inverting prefixes and suffixes correctly invert sentiment.
    """
    assert sentiment.analyze_word_sentiment("unhelpful") < 0.4
    assert sentiment.analyze_word_sentiment("impossible") < 0.4
    assert sentiment.analyze_word_sentiment("fearless") > 0.6
    assert sentiment.analyze_word_sentiment("hopeless") < 0.4

def test_recursive_affixes():
    """
    Tests that the algorithm can handle multiple prefixes and suffixes.
    """
    # "happy" is positive. "unhappy" is negative.
    # "disunhappy" should be positive again (double negative prefix).
    assert sentiment.analyze_word_sentiment("happy") > 0.7
    assert sentiment.analyze_word_sentiment("unhappy") < 0.3
    assert sentiment.analyze_word_sentiment("disunhappy") > 0.7

    # "fear" is negative. "fearless" is positive.
    # "fearlessless" should be negative again (double negative suffix).
    assert sentiment.analyze_word_sentiment("fearlessless") < 0.4

def test_morphemes_with_neutral_stem():
    """
    Tests that a morpheme's sentiment dominates if the stem is neutral.
    """
    # "bene" is positive, "zyx" is neutral. Result should be positive.
    assert sentiment.analyze_word_sentiment("benezyx") > 0.6
    # "mal" is negative, "zyx" is neutral. Result should be negative.
    assert sentiment.analyze_word_sentiment("malzyx") < 0.4
    # "zyx" is neutral, "less" is an inverting suffix. Result should be negative.
    assert sentiment.analyze_word_sentiment("zyxless") < 0.4

def test_positional_morphemes():
    """
    Tests that prefixes, suffixes, and infixes are scored correctly.
    """
    assert sentiment.analyze_word_sentiment("benefactor") > 0.65
    assert sentiment.analyze_word_sentiment("malrupt") < 0.2
    assert sentiment.analyze_word_sentiment("proactive") > 0.6
    assert sentiment.analyze_word_sentiment("euamor") > 0.8

def test_whole_word_lookup():
    """
    Tests that the validator finds whole words in the VADER lexicon first.
    """
    assert sentiment.analyze_word_sentiment("disaster") < 0.2
    assert sentiment.analyze_word_sentiment("love") > 0.8