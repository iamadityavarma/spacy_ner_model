# # import nltk
# # nltk.download('words')
# # from nltk.corpus import words
# # import json
# # import re
# # import logging

# # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='corpusCreator.log')

# # # Download NLTK corpus if not already
# # nltk.download('words')
# # nltk_words = set(w.lower() for w in words.words())

# # try:
# #     # Load JSON file
# #     logging.info("Loading JSON file...")
# #     with open("becn_data.json", "r", encoding="utf-8") as f:
# #         json_data = json.load(f)

# #     # Extract the actual data array from the "data" key
# #     data = json_data["data"]
# #     logging.info(f"Successfully loaded {len(data)} items")

# #     # Extract relevant text fields
# #     corpus_text = ""
# #     processed_items = 0

# #     for item in data:
# #         if isinstance(item, dict):  # Safety check
# #             fields = [
# #                 item.get("Brand", ""),
# #                 item.get("ProductTitle", ""),
# #                 item.get("ProductDescription", ""),
# #                 " ".join(item.get("ProductAttributes", [])) if item.get("ProductAttributes") else "",
# #                 item.get("Dimensions", ""),
# #                 item.get("Thickness", "")
# #             ]
# #             corpus_text += " ".join(fields) + " "
# #             processed_items += 1

# #             # Progress indicator for large files
# #             if processed_items % 1000 == 0:
# #                 logging.info(f"Processed {processed_items} items...")

# #     logging.info(f"Processed {processed_items} items total")


# #     logging.info("Removing URLs...")
# #     # Remove HTTP/HTTPS URLs
# #     corpus_text = re.sub(r'https?://[^\s]+', '', corpus_text, flags=re.IGNORECASE)
# #     # Extract words with 3 or more letters
# #     logging.info("Extracting words...")
# #     bcan_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', corpus_text.lower()))

# #     # Find words in BCAN but not in NLTK
# #     logging.info("Finding missing words...")
# #     missing_words = bcan_words - nltk_words

# #     # Save missing words
# #     with open("bcan_missing_words.txt", "w", encoding="utf-8") as f:
# #         for word in sorted(missing_words):
# #             f.write(word + "\n")

# #     logging.info(f"{len(missing_words)} unique BCAN-specific words written to bcan_missing_words.txt")
# #     logging.info(f"Total unique words found: {len(bcan_words)}")

# #     custom_word_set = nltk_words.union(missing_words)

# #     # Optional: Save the combined set to a text file
# #     with open("custom_corpus.txt", "w", encoding="utf-8") as f:
# #         for word in sorted(custom_word_set):
# #             f.write(word + "\n")

# #     logging.info(f"Custom corpus created with {len(custom_word_set)} words.")

# # except FileNotFoundError:
# #     logging.error("Error: becn_data.json file not found")
# # except json.JSONDecodeError as e:
# #     logging.error(f"Error parsing JSON: {e}")
# # except KeyError as e:
# #     logging.error(f"Error: Key {e} not found in JSON structure")
# #     logging.warning("Available keys: %s", list(json_data.keys()) if 'json_data' in locals() else "Cannot determine")
# # except Exception as e:
# #     logging.error(f"Unexpected error: {e}")


# import nltk
# nltk.download('words')
# from nltk.corpus import words
# import json
# import re
# import logging
# import pickle
# import os

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='corpusCreator.log')

# # Path to pickle file
# pickle_path = "customCorpus.pkl"

# # Try loading from pickle first
# if os.path.exists(pickle_path):
#     with open(pickle_path, "rb") as f:
#         custom_word_set = pickle.load(f)
#     logging.info(f"Loaded custom corpus from pickle with {len(custom_word_set)} words.")
# else:
#     # Download NLTK corpus if not already
#     nltk.download('words')
#     nltk_words = set(w.lower() for w in words.words())

#     try:
#         # Load JSON file
#         logging.info("Loading JSON file...")
#         with open("becn_data.json", "r", encoding="utf-8") as f:
#             json_data = json.load(f)

#         # Extract the actual data array from the "data" key
#         data = json_data["data"]
#         logging.info(f"Successfully loaded {len(data)} items")

#         # Extract relevant text fields
#         corpus_text = ""
#         processed_items = 0

#         for item in data:
#             if isinstance(item, dict):  # Safety check
#                 fields = [
#                     item.get("Brand", ""),
#                     item.get("ProductTitle", ""),
#                     item.get("ProductDescription", ""),
#                     " ".join(item.get("ProductAttributes", [])) if item.get("ProductAttributes") else "",
#                     item.get("Dimensions", ""),
#                     item.get("Thickness", "")
#                 ]
#                 corpus_text += " ".join(fields) + " "
#                 processed_items += 1

#                 # Progress indicator for large files
#                 if processed_items % 1000 == 0:
#                     logging.info(f"Processed {processed_items} items...")

#         logging.info(f"Processed {processed_items} items total")

#         # Clean and tokenize
#         logging.info("Removing URLs...")
#         corpus_text = re.sub(r'https?://[^\s]+', '', corpus_text, flags=re.IGNORECASE)

#         logging.info("Extracting words...")
#         bcan_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', corpus_text.lower()))

#         # Find missing words
#         logging.info("Finding missing words...")
#         missing_words = bcan_words - nltk_words

#         # Save missing words
#         with open("bcanMissingWords.txt", "w", encoding="utf-8") as f:
#             for word in sorted(missing_words):
#                 f.write(word + "\n")

#         logging.info(f"{len(missing_words)} unique BCAN-specific words written to bcan_missing_words.txt")
#         logging.info(f"Total unique words found: {len(bcan_words)}")

#         # Merge into final corpus
#         custom_word_set = nltk_words.union(missing_words)

#         with open("customCorpus.txt", "w", encoding="utf-8") as f:
#             for word in sorted(custom_word_set):
#                 f.write(word + "\n")

#         logging.info(f"Custom corpus created with {len(custom_word_set)} words.")

#         # Save as pickle
#         with open(pickle_path, "wb") as f:
#             pickle.dump(custom_word_set, f)

#         logging.info(f"Custom corpus saved to {pickle_path}")

#     except FileNotFoundError:
#         logging.error("Error: becn_data.json file not found")
#     except json.JSONDecodeError as e:
#         logging.error(f"Error parsing JSON: {e}")
#     except KeyError as e:
#         logging.error(f"Error: Key {e} not found in JSON structure")
#         logging.warning("Available keys: %s", list(json_data.keys()) if 'json_data' in locals() else "Cannot determine")
#     except Exception as e:
#         logging.error(f"Unexpected error: {e}")


import json
import pickle
import re
from collections import defaultdict

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='logs/corpusCreator.log')

def load_data(file_path):
    """Load JSON product data"""
    logging.info(f"Loading data from {file_path}")
    try:
        with open(file_path, 'r') as f:
            json_data = json.load(f)
            data = json_data["data"]
        logging.info(f"Successfully loaded data with {len(data)} items")
        return data
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in {file_path}: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error loading {file_path}: {e}")
        raise

def clean_text(text):
    """Clean and normalize text"""
    # Convert to string if not already
    if text is None:
        return ""
    text = str(text)
    if not text or text == "NA":
        return ""
    
    original_length = len(text)
    
    # Remove special characters except allowed set
    text = re.sub(r'[^\w\s.,;:/+\-\'"()]', '', text)
    
    # Standardize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    cleaned_length = len(text)
    if original_length != cleaned_length:
        logging.debug(f"Cleaned text: {original_length} -> {cleaned_length} characters")
    
    return text

def create_corpus(products):
    """Build corpus from product data"""
    logging.info(f"Starting corpus creation for {len(products)} products")
    corpus = []
    field_counter = defaultdict(int)
    processed_count = 0
    
    for i, product in enumerate(products):
        # Collect all text fields
        text_parts = []
        
        # Core fields
        for field in ['Brand', 'ProductTitle', 'ProductDescription']:
            if field in product:
                cleaned = clean_text(product[field])
                if cleaned:
                    text_parts.append(cleaned)
                    field_counter[field] += 1
        
        # Attributes
        if 'ProductAttributes' in product and product['ProductAttributes']:
            attrs = [clean_text(a) for a in product['ProductAttributes']]
            text_parts.append("Attributes: " + ", ".join(attrs))
            field_counter['ProductAttributes'] += 1
        
        # Specifications
        spec_fields = [
            'Length', 'Dimensions', 'Thickness', 'Area', 
            'Pieces per Bundle', 'Weight', 'Width'
        ]
        for field in spec_fields:
            if field in product and product[field]:
                spec = clean_text(product[field])
                if spec:
                    text_parts.append(f"{field}: {spec}")
                    field_counter[field] += 1
        
        # Combine all parts
        if text_parts:
            corpus.append(". ".join(text_parts))
            processed_count += 1
        
        # Progress logging every 1000 products
        if (i + 1) % 1000 == 0:
            logging.info(f"Processed {i + 1}/{len(products)} products ({processed_count} with valid text)")
    
    logging.info(f"Corpus creation completed. {processed_count}/{len(products)} products processed successfully")
    
    # Log field usage statistics
    logging.info("Field usage statistics:")
    for field, count in sorted(field_counter.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(products)) * 100
        logging.info(f"  {field}: {count}/{len(products)} products ({percentage:.1f}%)")
    
    # Also print to console for immediate feedback
    print("\nField usage statistics:")
    for field, count in sorted(field_counter.items(), key=lambda x: x[1], reverse=True):
        print(f"{field}: {count}/{len(products)} products")
    
    return corpus

def save_corpus(corpus, output_file):
    """Save corpus as pickle file"""
    logging.info(f"Saving corpus to {output_file}")
    try:
        with open(output_file, 'wb') as f:
            pickle.dump(corpus, f)
        logging.info(f"Successfully saved corpus with {len(corpus)} documents to {output_file}")
        print(f"\nCorpus saved to {output_file} with {len(corpus)} documents")
    except Exception as e:
        logging.error(f"Error saving corpus to {output_file}: {e}")
        raise

if __name__ == "__main__":
    # Configuration
    INPUT_FILE = "data/becn_data.json" 
    OUTPUT_FILE = "product_corpus.pkl"
    
    logging.info("=" * 50)
    logging.info("Starting Corpus Creator")
    logging.info("=" * 50)
    
    try:
        # Process data
        logging.info(f"Input file: {INPUT_FILE}")
        logging.info(f"Output file: {OUTPUT_FILE}")
        
        products = load_data(INPUT_FILE)
        corpus = create_corpus(products)
        save_corpus(corpus, OUTPUT_FILE)
        
        logging.info("=" * 50)
        logging.info("Corpus Creator completed successfully")
        logging.info("=" * 50)
        
    except Exception as e:
        logging.error(f"Corpus Creator failed: {e}")
        logging.error("=" * 50)
        raise