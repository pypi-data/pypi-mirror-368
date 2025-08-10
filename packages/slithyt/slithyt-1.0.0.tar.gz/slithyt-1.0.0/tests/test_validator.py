# Tests for the validator module.
import os
from slithyt import validator

import os
from slithyt import validator

def test_validator_with_sets():
    """
    Tests the validation logic with in-memory sets.
    """
    # Create the sets directly in memory for the test
    dictionary_set = {"common", "ordinary"}
    blocklist_set = {"blocked", "forbidden"}

    # Test a valid word
    assert validator.validate_word("zentoria", dictionary_set=dictionary_set, blocklist_set=blocklist_set) == True

    # Test a word that is a common word
    assert validator.validate_word("common", dictionary_set=dictionary_set, blocklist_set=blocklist_set) == False

    # Test a word that is on the blocklist
    assert validator.validate_word("forbidden", dictionary_set=dictionary_set, blocklist_set=blocklist_set) == False

    # Test regex constraints (these don't need the sets)
    assert validator.validate_word("startgood", matches_regex="^start") == True
    assert validator.validate_word("startbad", matches_regex="^wrong") == False
    assert validator.validate_word("endgood", reject_regex="bad$") == True
    assert validator.validate_word("endbad", reject_regex="bad$") == False

def test_sentiment_validator():
    """Tests the sentiment validation logic."""
    # These words are constructed to have clear sentiment leanings
    # based on morphemes in the VADER lexicon (e.g., 'win', 'love', 'doom', 'bad').
    positive_word = "eulove"
    negative_word = "maldoom"
    neutral_word = "zxyabc" # No morphemes in VADER lexicon
    
    # Test min_sentiment: positive word should pass, negative word should fail.
    assert validator.validate_word(positive_word, min_sentiment=0.75) == True
    assert validator.validate_word(negative_word, min_sentiment=0.75) == False

    # Test max_sentiment: negative word should pass, positive word should fail.
    assert validator.validate_word(negative_word, max_sentiment=0.35) == True
    assert validator.validate_word(positive_word, max_sentiment=0.35) == False

    # Test a neutral word in a neutral range
    assert validator.validate_word(neutral_word, min_sentiment=0.4, max_sentiment=0.6) == True

    # Test a positive word failing a neutral range
    assert validator.validate_word(positive_word, min_sentiment=0.4, max_sentiment=0.6) == False

def test_corpus_rejection():
    """Tests that a word from the corpus rejection set is correctly invalidated."""
    corpus_rejection_set = {"brillig", "slithy", "toves"}

    # A word from the set should be rejected
    assert validator.validate_word("slithy", corpus_rejection_set=corpus_rejection_set) == False
    # A novel word should be accepted
    assert validator.validate_word("gimble", corpus_rejection_set=corpus_rejection_set) == True
