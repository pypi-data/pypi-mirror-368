# Contains the n-gram model training and word generation logic.

import random
from collections import defaultdict
from . import utils

def train_from_corpus(corpus_path: str, n: int = 3) -> tuple[dict, set]:
    """
    Reads a corpus file once to train a character-level n-gram model
    and create a set of all words in the corpus for novelty checking.
    
    The model is a dictionary where keys are prefixes of length (n-1)
    and values are lists of characters that can follow that prefix.

    Args:
        corpus_path: Path to the text file to train on (one word per line).
        n: The order of the n-gram model (e.g., 3 for trigrams).

    Returns:
        A tuple containing (model_dict, corpus_word_set).
    """
    model = defaultdict(list)
    corpus_word_set = set()
    
    # Use special characters for start and end of a word
    start_char = "^"
    end_char = "$"
    
    prefix_len = n - 1

    try:
        with utils.open_any(corpus_path) as f:
            for line in f:
                word = line.strip().lower()
                if not word:
                    continue
                corpus_word_set.add(word)
                
                # Pad the word with start/end markers
                padded_word = (start_char * prefix_len) + word + end_char
                
                for i in range(len(padded_word) - prefix_len):
                    prefix = padded_word[i : i + prefix_len]
                    next_char = padded_word[i + prefix_len]
                    model[prefix].append(next_char)
    except FileNotFoundError:
        print(f"ERROR: Corpus file not found at {corpus_path}")
        return {}, set()
        
    return dict(model), corpus_word_set

def generate_word(model: dict, min_len: int = 5, max_len: int = 10, n: int = 3) -> str:
    """
    Generates a single word using the trained n-gram model.

    Args:
        model: The trained n-gram model from train_model().
        min_len: The minimum length of the generated word.
        max_len: The maximum length of the generated word.
        n: The order of the n-gram model used for generation.

    Returns:
        A newly generated word as a string, or an empty string if generation fails.
    """
    if not model:
        return ""

    start_char = "^"
    end_char = "$"
    prefix_len = n - 1

    # Loop until a valid word is generated
    for _ in range(100): # Max attempts to prevent infinite loops
        word_chars = []
        current_prefix = start_char * prefix_len
        
        for _ in range(max_len):
            if current_prefix not in model:
                # This prefix was not seen during training, dead end.
                break 

            next_char = random.choice(model[current_prefix])

            if next_char == end_char:
                break
            
            word_chars.append(next_char)
            current_prefix = current_prefix[1:] + next_char
        
        final_word = "".join(word_chars)
        if min_len <= len(final_word) <= max_len:
            return final_word

    return "" # Return empty if we couldn't generate a valid word
