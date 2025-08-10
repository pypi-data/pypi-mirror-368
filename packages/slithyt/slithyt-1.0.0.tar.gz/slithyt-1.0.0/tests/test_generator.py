# Tests for the generator module.
import tempfile
import os
from slithyt import generator

def test_train_and_generate():
    """
    Tests that the generator can be trained and can produce a word.
    This test creates a temporary corpus file.
    """
    corpus_content = "slithy\nautonomer\npythonic\n"

    # Create a temporary file to act as the corpus
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as tmp:
        tmp.write(corpus_content)
        corpus_path = tmp.name

    try:
        # Test training
        model, corpus_set = generator.train_from_corpus(corpus_path, n=3)
        assert isinstance(model, dict)
        assert len(model) > 0
        assert isinstance(corpus_set, set)
        assert "pythonic" in corpus_set
        # Check if a known trigram was learned correctly.
        # The key should be the prefix of length n-1.
        # The value should be a list containing the next character.
        assert '^^' in model and 's' in model['^^']
        assert "th" in model
        assert "y" in model["th"]

        # Test generation
        word = generator.generate_word(model, min_len=4, max_len=10, n=3)
        assert isinstance(word, str)
        assert len(word) >= 4
        assert word.islower() # Check that the word is lowercase
        
        # Check that the generated word only contains characters from the corpus
        corpus_chars = set("slithyautonomerpcn")
        word_chars = set(word.lower())
        assert word_chars.issubset(corpus_chars)

    finally:
        # Clean up the temporary file
        os.remove(corpus_path)
