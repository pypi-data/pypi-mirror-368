# src/slithyt/rhyme.py

import pronouncing
import pickle
import random
import pathlib
from . import build

def get_phonetic_breakdown(word: str) -> list[str] | None:
    """Gets the phonetic breakdown for a word."""
    pronunciations = pronouncing.phones_for_word(word)
    if not pronunciations:
        return None
    return pronunciations[0].split()

def get_rhyme_signature(phonemes: list[str]) -> list[str] | None:
    """Extracts the rhyming part of a word from its list of phonemes."""
    last_stressed_vowel_index = -1
    for i, p in enumerate(phonemes):
        if p[-1] in ('1', '2'):
            last_stressed_vowel_index = i
    if last_stressed_vowel_index == -1:
        return None
    return phonemes[last_stressed_vowel_index:]

def load_phonetic_model(model_path: str) -> dict:
    """Loads a pre-computed phonetic model, building it if it doesn't exist."""
    model_path = pathlib.Path(model_path)
    if model_path.exists():
        with open(model_path, "rb") as f:
            return pickle.load(f)
    else:
        print("First-time setup: Building phonetic model. This may take a moment...")
        module_path = pathlib.Path(__file__).parent
        default_dict_path = module_path / 'data' / 'cmu.txt.gz'
        
        model = build.build_phonetic_model(str(default_dict_path))
        
        model_path.parent.mkdir(parents=True, exist_ok=True)
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        print(f"Phonetic model saved to {model_path}")
        return model

def load_transcription_model(model_path: str) -> dict:
    """Loads a pre-computed transcription model, building it if it doesn't exist."""
    model_path = pathlib.Path(model_path)
    if model_path.exists():
        with open(model_path, "rb") as f:
            return pickle.load(f)
    else:
        print("First-time setup: Building transcription model. This may take a moment...")
        module_path = pathlib.Path(__file__).parent
        default_dict_path = module_path / 'data' / 'cmu.txt.gz'
        
        model = build.build_transcription_model(str(default_dict_path))
        
        model_path.parent.mkdir(parents=True, exist_ok=True)
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        print(f"Transcription model saved to {model_path}")
        return model

def generate_phonetic_word(model: dict, rhyme_signature: list[str], n: int = 3) -> list[str] | None:
    """Generates a new sequence of phonemes that ends with the given rhyme signature."""
    if not model: return None
    prefix_len = n - 1
    current_prefix = tuple(["^"] * prefix_len)
    generated_phonemes = []
    for _ in range(10):
        if current_prefix not in model: return None
        next_phoneme = random.choice(model[current_prefix])
        if next_phoneme == "$": break
        generated_phonemes.append(next_phoneme)
        current_prefix = tuple(list(current_prefix[1:]) + [next_phoneme])
    return generated_phonemes + rhyme_signature

def transcribe_word(transcription_model: dict, phonemes: list[str]) -> str:
    """Transcribes a sequence of phonemes into a plausible word spelling."""
    word = []
    for p in phonemes:
        base_phoneme = p.rstrip('012')
        if base_phoneme in transcription_model and transcription_model[base_phoneme]:
            word.append(random.choice(transcription_model[base_phoneme]))
        else:
            word.append('?')
    return "".join(word)