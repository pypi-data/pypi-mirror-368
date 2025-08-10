# slithyt/pronounce.py

def score_pronounceability(word: str) -> float:
    """
    Calculates a pronounceability score for a word based on heuristics.
    The score is between 0.0 (less pronounceable) and 1.0 (more pronounceable).

    Args:
        word: The word to score.

    Returns:
        A float representing the pronounceability score.
    """
    if not word:
        return 0.0

    word_lower = word.lower()
    vowels = "aeiou"
    
    # Heuristic 1: Penalize long consonant clusters
    max_consonant_cluster = 0
    current_consonant_cluster = 0
    for char in word_lower:
        if char not in vowels:
            current_consonant_cluster += 1
        else:
            max_consonant_cluster = max(max_consonant_cluster, current_consonant_cluster)
            current_consonant_cluster = 0
    max_consonant_cluster = max(max_consonant_cluster, current_consonant_cluster)
    
    # A cluster of more than 3 consonants is difficult.
    consonant_penalty = max(0, max_consonant_cluster - 3) * 0.3

    # Heuristic 2: Penalize long vowel clusters
    max_vowel_cluster = 0
    current_vowel_cluster = 0
    for char in word_lower:
        if char in vowels:
            current_vowel_cluster += 1
        else:
            max_vowel_cluster = max(max_vowel_cluster, current_vowel_cluster)
            current_vowel_cluster = 0
    max_vowel_cluster = max(max_vowel_cluster, current_vowel_cluster)

    # A cluster of more than 2 vowels is uncommon.
    vowel_penalty = max(0, max_vowel_cluster - 2) * 0.4

    # Heuristic 3: Ideal vowel-to-consonant ratio (35%-65% vowels)
    num_vowels = sum(1 for char in word_lower if char in vowels)
    vowel_ratio = num_vowels / len(word_lower) if len(word_lower) > 0 else 0
    
    ratio_penalty = 0
    if not (0.35 <= vowel_ratio <= 0.65):
        ratio_penalty = 0.3

    # Calculate final score
    total_penalty = consonant_penalty + vowel_penalty + ratio_penalty
    score = max(0.0, 1.0 - total_penalty)
    
    return score