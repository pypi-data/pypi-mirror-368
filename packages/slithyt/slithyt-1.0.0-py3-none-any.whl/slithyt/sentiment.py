from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize the analyzer for its word lexicon.
_analyzer = SentimentIntensityAnalyzer()

# --- Structured Morpheme Lexicons ---

_INVERTING_PREFIXES = {"un", "in", "im", "il", "ir", "non", "dis", "mis", "dys", "anti"}
_INVERTING_SUFFIXES = {"less"}

_PREFIXES = {
    "mal": -4.0, "mis": -3.0, "dis": -2.0, "un": -1.0, "in": -1.0, "im": -1.0,
    "non": -1.0, "de": -1.0, "anti": -2.0, "contra": -2.0, "ob": -2.0,
    "pseudo": -2.0, "cata": -2.0, "dys": -2.2, "caco": -2.3,
    "bene": 3.0, "eu": 4.0, "pro": 2.0, "pre": 1.0, "con": 2.0, "com": 2.0,
    "sym": 2.0, "syn": 2.0,
}

_SUFFIXES = {
    "less": -2.0, "cide": -4.0, "ful": 1.5, "able": 1.0, "ible": 1.0,
}

_INFIXES = {
    "mort": -3.0, "nec": -3.0, "necr": -3.0, "path": -3.0, "tox": -4.0,
    "pess": -3.0, "mor": -3.0, "vill": -3.0, "crim": -3.0, "rupt": -2.0,
    "fail": -3.0, "terr": -2.0, "horr": -4.0, "vuln": -2.0, "hostil": -3.0,
    "vex": -2.0, "trib": -2.0, "fall": -2.0, "err": -1.9,
    "am": 3.0, "amic": 3.0, "phil": 3.0, "pac": 4.0, "grat": 4.0,
    "felic": 4.0, "beat": 4.0, "sanct": 3.0, "salv": 3.0, "ver": 3.0,
    "honor": 3.0, "dign": 3.0, "fortun": 2.0, "optim": 4.0, "lucr": 2.0,
    "prosper": 4.0, "brill": 3.0, "clar": 2.0, "lumin": 3.0, "vital": 3.0,
    "viv": 3.0, "gen": 2.0, "cresc": 2.0, "cret": 2.0, "magn": 3.0,
    "grand": 3.0, "nobl": 3.0, "excell": 4.0, "laud": 4.0, "glor": 3.0,
    "merit": 3.0, "secure": 3.0, "firm": 2.0, "resolut": 2.0, "joy": 4.0,
    "happ": 4.0, "hope": 3.0, "vit": 2.0, "equi": 1.5, "amor": 2.8,
    "bon": 2.5, "luc": 1.8, "lum": 1.8, "cred": 1.7,
}

_WORD_LEXICON = _analyzer.lexicon

_SORTED_PREFIXES = sorted(_PREFIXES.keys(), key=len, reverse=True)
_SORTED_SUFFIXES = sorted(_SUFFIXES.keys(), key=len, reverse=True)

def _normalize_score(score: float) -> float:
    """Normalizes a VADER score to a 0.0-1.0 scale."""
    return (score + 4) / 8

def analyze_word_sentiment(word: str) -> float:
    """
    Analyzes word sentiment using a recursive, positional, multi-pass algorithm.
    """
    word_lower = word.lower()
    
    if not word_lower:
        return 0.5

    if word_lower in _WORD_LEXICON:
        return _normalize_score(_WORD_LEXICON[word_lower])

    for p in _SORTED_PREFIXES:
        if len(p) >= 2 and word_lower.startswith(p):
            prefix_score = _PREFIXES[p]
            stem = word_lower[len(p):]
            
            if len(stem) < 4:
                return _normalize_score(prefix_score)

            stem_sentiment = analyze_word_sentiment(stem)
            
            # If the stem is neutral, the prefix's sentiment dominates.
            if stem_sentiment == 0.5:
                return _normalize_score(prefix_score)
            
            if p in _INVERTING_PREFIXES:
                return 1.0 - stem_sentiment
            
            avg_raw_score = (prefix_score + (stem_sentiment * 8 - 4)) / 2
            return _normalize_score(avg_raw_score)

    for s in _SORTED_SUFFIXES:
        if len(s) >= 2 and word_lower.endswith(s):
            suffix_score = _SUFFIXES[s]
            stem = word_lower[:-len(s)]

            if len(stem) < 4:
                return _normalize_score(suffix_score)
            
            stem_sentiment = analyze_word_sentiment(stem)

            if stem_sentiment == 0.5:
                return _normalize_score(suffix_score)
            
            if s in _INVERTING_SUFFIXES:
                return 1.0 - stem_sentiment

            avg_raw_score = (suffix_score + (stem_sentiment * 8 - 4)) / 2
            return _normalize_score(avg_raw_score)

    found_scores = []
    i = 0
    while i < len(word_lower):
        best_match = ""
        for j in range(len(word_lower), i, -1):
            substring = word_lower[i:j]
            if len(substring) >= 3 and substring in _INFIXES:
                best_match = substring
                break
        
        if best_match:
            found_scores.append(_INFIXES[best_match])
            i += len(best_match)
        else:
            i += 1

    if not found_scores:
        return 0.5

    avg_score = sum(found_scores) / len(found_scores)
    return _normalize_score(avg_score)