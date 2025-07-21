import logging
import spacy

logger = logging.getLogger(__name__)

# Load SpaCy English model from the specified directory

def load_model():
    """
    Load the trained SpaCy model from the 'models' directory.
    
    Returns:
        nlp: The loaded SpaCy language model
    Raises:
        Exception: If the model cannot be loaded
    """
    try:
        nlp = spacy.load("models")  # Load the model from the 'models' directory
        logger.info("SpaCy model loaded successfully")
        return nlp
    except Exception as e:
        logger.error(f"Error loading SpaCy model: {e}")
        raise

def extract_entities(text: str, nlp):
    """
    Extract named entities from the input text using the provided SpaCy model.
    
    Args:
        text (str): The input text to analyze
        nlp: The loaded SpaCy language model
    
    Returns:
        List[dict]: A list of dictionaries, each containing the entity text and label
    """
    try:
        doc = nlp(text)  # Process the text with the SpaCy model
        # Return a list of entities with their text and label
        return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        return []