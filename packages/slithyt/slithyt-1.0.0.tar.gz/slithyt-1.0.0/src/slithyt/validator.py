import re
from typing import Set
from . import sentiment
from . import pronounce
from . import utils

def load_word_set(file_path: str) -> Set[str]:
    """
    Loads a word list from a plain text or gzipped file into a set
    for efficient lookup.
    """
    if not file_path:
        return set()
    try:
        with utils.open_any(file_path) as f:
            return {line.strip().lower() for line in f if line.strip()}
    except FileNotFoundError:
        print(f"WARNING: File not found at {file_path}. Skipping this check.")
        return set()

def validate_word(
    word: str,
    matches_regex: str = None,
    reject_regex: str = None,
    dictionary_set: set[str] = None,
    blocklist_set: set[str] = None,
    corpus_rejection_set: set[str] = None,
    min_sentiment: float = None,
    max_sentiment: float = None,
    min_pronounceability: float = None
) -> bool:
    """
    Validates a word against a set of constraints.
    """
    if not word:
        return False
    word_lower = word.lower()
    if matches_regex and not re.search(matches_regex, word, re.IGNORECASE):
        return False
    if reject_regex and re.search(reject_regex, word, re.IGNORECASE):
        return False
    if dictionary_set and word_lower in dictionary_set:
        return False
    if blocklist_set and word_lower in blocklist_set:
        return False
    if corpus_rejection_set and word_lower in corpus_rejection_set:
        return False
    if min_sentiment is not None or max_sentiment is not None:
        score = sentiment.analyze_word_sentiment(word)
        if min_sentiment is not None and score < min_sentiment:
            return False
        if max_sentiment is not None and score > max_sentiment:
            return False
    if min_pronounceability is not None:
        score = pronounce.score_pronounceability(word)
        if score < min_pronounceability:
            return False
    return True