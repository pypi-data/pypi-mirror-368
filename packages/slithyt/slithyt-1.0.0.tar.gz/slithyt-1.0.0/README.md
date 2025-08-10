# SlithyT

A tool for generating novel, plausible, and pronounceable words based on linguistic corpuses.

The name is a reference to the "slithy toves" in Lewis Carroll's poem "Jabberwocky".

(Code was written substantially by AI, although I did a fair amount of reviewing, criticizing, revising
and debugging.)

## Installation

```bash
pip install .
```

## Usage

Generate a word that looks/sounds like it fits with other words in a given
corpus. Similarity is determined partly by ngram analysis and partly by
pronunciation.

You can make your own corpus, or use pregenerated ones (in the data folder
of the package):

* Astronomy names (stars, galaxies, planets)
* Transliterated Greek, Latin, Hebrew, Egyptian names
* Harry Potter or Star Wars names
* Drug names
* Latin words from biology taxonomy (genus, species)

You can also use the whole dictionary as your corpus, in which case you will
get words with no particular flavor to them. A good corpus has at least a
couple hundred words in it.

By default, generated words are *novel*, meaning they won't appear in the
corpus you reference. You can also add a blocklist to avoid generating curse
words, words that violate trademarks or spam filters, etc.

All corpora and dictionary/block list files used by this tool are text
files having a single word per line, and can optionally be gzipped.
Sentiment analysis, pronounceability, and rhyming are moderately English-
centric, though the tolerate romance and germanic languages a bit as well.
However, they could be made to reflect the sensibilities of other language
communities by running build_phonetic_model.py and build_transcription_model.py
in the package's scripts folder. These generate cached patterns in 
~/.slithyt/data.

```bash
# Generate 10 realistic words that sound like they belong in corpus. Make
# the words have a length of at least 5 characters.
slithyt generate --corpus path/to/your/corpus.txt

# Generate words that have a positive connotation due to sound symbolism
# (see https://en.wikipedia.org/wiki/Sound_symbolism), that have use n=4
# for ngram analysis. (The --ngram-size argument is a tradeoff. Default is 3.
# Bigger values make the resonance with the corpus stronger, but also make it
# harder to be creative; it may be impossible to generate words if you go too
# high. Smaller values give the algorithm more freedom in both size and
# character sequence, but the output might sound less like the corpus.)
slithyt generate --corpus path/to/corpus.txt --min-sentiment 0.8 --ngram-size 4

# Generate words that are at between 4 and 8 characters long, and that are at
# least moderately pronounceable. (Pronounceability depends partly on the
# speaker's judgment; slithyt uses a simple algorithm to predict scores from
# 0 (hardest) to 1 (easiest), but the corpus may affect how reasonable 0.5 is.
# Typically, the variety of generated word lengths matches the variety of
# word lengths in the corpus. These values constrain output but may make
# generation impossible, if nothing in the corpus is as small or as large as
# what was requested.)
slithyt generate --corpus path/to/corpus.txt --min-length 4 --max-length 8 --min-pronounceability 0.5

# Generate 5 words that rhyme with synergy
slithyt generate --count 5 --rhymes-with synergy

# Report the rhyming analysis for synergy. (Only known words are usable
# as a rhyming template; passing made-up words here will do nothing
# useful.)
slithyt rhyme synergy

# Check to see whether a particular made-up word would pass certain tests.
slithyt validate synerjee
```
