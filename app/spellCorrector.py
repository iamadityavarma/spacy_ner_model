import os 
import logging
import pickle
import difflib
import re

CUSTOM_CORPUS = None
logger = logging.getLogger(__name__)

def load_corpus(corpus_path: str = "app/customCorpus.pkl") -> bool:
    """
    Load the custom corpus from pickle file.
    
    Args:
        corpus_path: Path to the pickle file containing the corpus
        
    Returns:
        bool: True if corpus loaded successfully, False otherwise
    """
    global CUSTOM_CORPUS
    try:
        with open(corpus_path, "rb") as f:
            CUSTOM_CORPUS = pickle.load(f)
        logger.info(f"Corpus loaded successfully from {corpus_path}")
        return True
    except FileNotFoundError:
        logger.error(f"Corpus file not found: {corpus_path}")
        CUSTOM_CORPUS = set()  # Initialize empty set as fallback
        return False
    except (pickle.UnpicklingError, EOFError) as e:
        logger.error(f"Error unpickling corpus file: {e}")
        CUSTOM_CORPUS = set()
        return False
    except Exception as e:
        logger.error(f"Unexpected error loading corpus: {e}")
        CUSTOM_CORPUS = set()
        return False

def is_mixed_token(word: str) -> bool:
    """
    Check if a word contains both digits and letters.
    
    Args:
        word: The word to check
        
    Returns:
        bool: True if word contains both digits and letters, False otherwise
    """
    try:
        if not word or not isinstance(word, str):
            return False
        return bool(re.search(r'\d', word)) and bool(re.search(r'[a-zA-Z]', word))
    except Exception as e:
        logger.warning(f"Error checking mixed token for '{word}': {e}")
        return False

def is_valid_word(word: str) -> bool:
    """
    Check if a word is valid (exists in corpus or is a mixed token).
    
    Args:
        word: The word to validate
        
    Returns:
        bool: True if word is valid, False otherwise
    """
    try:
        if not word or not isinstance(word, str):
            return False
        
        if CUSTOM_CORPUS is None:
            logger.warning("Corpus not loaded. Loading default corpus.")
            if not load_corpus():
                return is_mixed_token(word)  # Fallback to mixed token check only
        
        return word.lower() in CUSTOM_CORPUS or is_mixed_token(word)
    except Exception as e:
        logger.warning(f"Error validating word '{word}': {e}")
        return False

def suggest_word(word: str, n: int = 1) -> str:
    """
    Suggest a correction for a word using difflib.
    
    Args:
        word: The word to get suggestions for
        n: Number of suggestions to consider (default: 1)
        
    Returns:
        str: The suggested word or original word if no suggestions found
    """
    try:
        if not word or not isinstance(word, str):
            return word
        
        if CUSTOM_CORPUS is None:
            logger.warning("Corpus not loaded. Cannot suggest corrections.")
            return word
        
        if not isinstance(n, int) or n <= 0:
            n = 1
        
        matches = difflib.get_close_matches(word.lower(), CUSTOM_CORPUS, n=n, cutoff=0.6)
        return matches[0] if matches else word
    except Exception as e:
        logger.warning(f"Error suggesting word for '{word}': {e}")
        return word

def correct_text(text: str) -> str:
    """
    Correct text by replacing invalid words with suggestions.
    
    Args:
        text: The text to correct
        
    Returns:
        str: The corrected text
    """
    try:
        if not text or not isinstance(text, str):
            logger.warning("Invalid input text provided")
            return text or ""
        
        if CUSTOM_CORPUS is None:
            logger.warning("Corpus not loaded. Loading default corpus.")
            if not load_corpus():
                logger.error("Failed to load corpus. Returning original text.")
                return text
        
        words = text.split()
        corrected = []
        
        for word in words:
            try:
                if is_valid_word(word):
                    corrected.append(word)
                else:
                    suggested = suggest_word(word)
                    corrected.append(suggested)
                    if suggested != word:
                        logger.debug(f"Corrected '{word}' to '{suggested}'")
            except Exception as e:
                logger.warning(f"Error processing word '{word}': {e}")
                corrected.append(word)  # Keep original word if error occurs
        
        return " ".join(corrected)
    
    except Exception as e:
        logger.error(f"Error correcting text: {e}")
        return text or ""

# import re
# import kenlm
# from spellchecker import SpellChecker

# class DomainSpellCorrector:
#     def __init__(self, resource_dir):
#         # Load domain resources
#         self.domain_dict = self._load_resource(resource_dir / 'domain_dict.txt')
#         self.brand_names = self._load_resource(resource_dir / 'brand_names.txt')
        
#         # Initialize spell checker with domain dictionary
#         self.spell = SpellChecker()
#         self.spell.word_frequency.load_words(self.domain_dict)
        
#         # Load language model
#         self.lm = kenlm.Model(str(resource_dir / 'product.klm'))
    
#     def _load_resource(self, file_path):
#         """Load resource file into set"""
#         with open(file_path, 'r') as f:
#             return {line.strip() for line in f}
    
#     def _is_measurement(self, token):
#         """Check if token is a measurement"""
#         return bool(re.match(r'^(\d+|\d+\.\d+|\d+/\d+)[a-z"\'°]*$', token))
    
#     def _correct_measurement(self, token):
#         """Standardize measurement units"""
#         replacements = {
#             '"': 'inch', "'": 'ft', 'in': 'inch', 'ft': 'ft',
#             'ga': 'gauge', 'g': 'gauge', 'sqft': 'sq_ft', 'sq': 'sq_ft',
#             'lf': 'linear_ft', 'mil': 'mil'
#         }
#         for unit, canonical in replacements.items():
#             if token.endswith(unit):
#                 return token.replace(unit, canonical)
#         return token
    
#     def correct_query(self, query):
#         """Correct spelling errors in query with domain awareness"""
#         tokens = query.split()
#         corrected = []
        
#         for token in tokens:
#             # Handle measurements (7", 28ga, etc.)
#             if self._is_measurement(token):
#                 corrected.append(self._correct_measurement(token))
#                 continue
            
#             # Check brand names first (case-insensitive)
#             token_lower = token.lower()
#             if token_lower in self.brand_names:
#                 corrected.append(token)  # Preserve original casing
#                 continue
            
#             # Check domain dictionary
#             if token_lower in self.domain_dict:
#                 corrected.append(token)
#                 continue
            
#             # Generate spelling candidates
#             candidates = self.spell.candidates(token)
#             if not candidates or token in candidates:
#                 corrected.append(token)
#                 continue
            
#             # Score candidates with language model
#             best_candidate = token
#             best_score = float('-inf')
            
#             for candidate in candidates:
#                 # Create candidate sentence
#                 test_sentence = " ".join(corrected + [candidate] + tokens[len(corrected)+1:])
#                 score = self.lm.score(test_sentence)
                
#                 if score > best_score:
#                     best_score = score
#                     best_candidate = candidate
            
#             corrected.append(best_candidate)
        
#         return " ".join(corrected)

# # Usage example
# if __name__ == "__main__":
#     corrector = DomainSpellCorrector(Path("spelling_resources"))
    
#     test_queries = [
#         "kemprol resin rolr 7in",
#         "gaf ventalation 8-7/8",
#         "28ga flashng charcoal",
#         "pvc trim coil soft maple",
#         "rooling accessories"
#     ]
    
#     for query in test_queries:
#         corrected = corrector.correct_query(query)
#         print(f"Original: {query}")
#         print(f"Corrected: {corrected}\n")

