from slithyt import rhyme

def test_get_phonetic_breakdown():
    """Tests that we can get a list of phonemes for a word."""
    # Test a word that should be in the dictionary
    phonemes = rhyme.get_phonetic_breakdown("legacy")
    assert phonemes == ['L', 'EH1', 'G', 'AH0', 'S', 'IY0']
    
    # Test a word that should not be in the dictionary
    assert rhyme.get_phonetic_breakdown("brillig") is None

def test_get_rhyme_signature():
    """Tests that we can correctly extract the rhyming part of a word."""
    # Test a word where the last stressed vowel is in the middle
    phonemes = ['JH', 'EH2', 'N', 'ER0', 'EY1', 'SH', 'AH0', 'N'] # generation
    signature = rhyme.get_rhyme_signature(phonemes)
    assert signature == ['EY1', 'SH', 'AH0', 'N']

    # Test a word where the last stressed vowel is at the beginning
    phonemes = ['S', 'IH1', 'N', 'ER0', 'JH', 'IY0'] # synergy
    signature = rhyme.get_rhyme_signature(phonemes)
    assert signature == ['IH1', 'N', 'ER0', 'JH', 'IY0']

    # Test a word with no stressed vowels (should be rare, but possible)
    # The pronouncing library often returns pronunciations without stress for some words.
    phonemes = ['AH', 'B', 'AW', 'T'] # a pronunciation of "about"
    signature = rhyme.get_rhyme_signature(phonemes)
    assert signature is None