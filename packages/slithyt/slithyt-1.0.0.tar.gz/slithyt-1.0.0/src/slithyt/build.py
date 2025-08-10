# src/slithyt/build.py

import pickle
import pathlib
from collections import defaultdict
from . import utils
import pronouncing

def build_phonetic_model(corpus_path: str, n: int = 3) -> dict:
    """Builds a phonetic n-gram model from a word corpus."""
    model = defaultdict(list)
    prefix_len = n - 1

    with utils.open_any(corpus_path) as f:
        for i, word in enumerate(f):
            if (i + 1) % 20000 == 0:
                print(f"  ...processed {i+1} words for phonetic model...")
            word = word.strip().lower()
            if not word: continue
            
            phones_list = pronouncing.phones_for_word(word)
            if not phones_list: continue
            
            phonemes = phones_list[0].split()
            padded_phonemes = (["^"] * prefix_len) + phonemes + ["$"]
            
            for i in range(len(padded_phonemes) - prefix_len):
                prefix = tuple(padded_phonemes[i : i + prefix_len])
                next_phoneme = padded_phonemes[i + prefix_len]
                model[prefix].append(next_phoneme)
    
    return dict(model)

def build_transcription_model(corpus_path: str) -> dict:
    """Builds a statistical model for transcribing phonemes to graphemes."""
    model = defaultdict(lambda: defaultdict(int))

    with utils.open_any(corpus_path) as f:
        for i, word in enumerate(f):
            if (i + 1) % 20000 == 0:
                print(f"  ...processed {i+1} words for transcription model...")
            word = word.strip().lower()
            if not word: continue

            phones_list = pronouncing.phones_for_word(word)
            if not phones_list: continue
            
            phonemes = phones_list[0].split()
            
            if len(phonemes) == len(word):
                for i, p in enumerate(phonemes):
                    base_phoneme = p.rstrip('012')
                    letter = word[i]
                    model[base_phoneme][letter] += 1

    final_model = {}
    for phoneme, spellings in model.items():
        sorted_spellings = sorted(spellings.items(), key=lambda item: item[1], reverse=True)
        final_model[phoneme] = [s[0] for s in sorted_spellings[:3]]

    return final_model