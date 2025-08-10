from slithyt import pronounce

def test_pronounceability_scorer():
    """Tests the pronounceability scoring logic."""
    
    # 1. Good, pronounceable words should score high
    # These have good vowel/consonant alternation.
    assert pronounce.score_pronounceability("veridian") > 0.9
    assert pronounce.score_pronounceability("solara") > 0.9
    assert pronounce.score_pronounceability("kalani") > 0.9

    # 2. Words with long consonant clusters should be penalized
    # "rhythmsk" has a 4-consonant cluster.
    assert pronounce.score_pronounceability("rhythmsk") < 0.5
    # "schtroumpf" ("smurf" in German) has a 5-consonant cluster.
    assert pronounce.score_pronounceability("schtroumpf") < 0.7 

    # 3. Words with long vowel clusters should be penalized
    # "aeioua" has a 6-vowel cluster.
    assert pronounce.score_pronounceability("aeioua") < 0.5
    # "eunoia" has a 5-vowel cluster.
    assert pronounce.score_pronounceability("eunoia") < 0.7

    # 4. Words with bad vowel/consonant ratios should be penalized
    # "strength" has a low vowel ratio (1/8 = 12.5%).
    assert pronounce.score_pronounceability("strength") < 0.8 
    # "aeia" has a high vowel ratio (4/4 = 100%).
    assert pronounce.score_pronounceability("aeia") < 0.8 

    # 5. Edge cases should not cause errors
    assert pronounce.score_pronounceability("") == 0.0
    assert pronounce.score_pronounceability("a") < 0.8 # Bad ratio
    assert pronounce.score_pronounceability("b") == 0.7 # Bad ratio