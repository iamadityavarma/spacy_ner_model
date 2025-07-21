
""" This segment is not implemented due to memory constraints in the current laptop but they will be added during future work"""



import pickle
import json
import re
from collections import Counter
import subprocess
from pathlib import Path

def load_corpus(corpus_path):
    """Load corpus from pickle file"""
    with open(corpus_path, 'rb') as f:
        return pickle.load(f)

def extract_domain_resources(products, corpus):
    """Extract domain dictionary and brand names"""
    # Domain vocabulary (case-insensitive)
    vocab = Counter()
    for doc in corpus:
        tokens = re.findall(r'\b\w+\b', doc.lower())
        vocab.update(tokens)
    
    # Get most frequent domain terms
    domain_dict = {word for word, count in vocab.most_common() if count >= 2}
    
    # Extract brand names
    brand_names = set()
    for product in products:
        brand = product['Brand'].strip().lower()
        # Split multi-word brands into individual tokens
        brand_names.update(brand.split())
        # Also add the full brand name as a compound term
        brand_names.add(brand.replace(' ', '_'))
    
    return domain_dict, brand_names

def train_language_model(corpus, output_dir):
    """Train KenLM language model from corpus"""
    # Prepare directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    corpus_txt = Path(output_dir) / 'corpus.txt'
    arpa_file = Path(output_dir) / 'product.arpa'
    binary_file = Path(output_dir) / 'product.klm'
    
    # Write corpus to text file
    with open(corpus_txt, 'w') as f:
        for doc in corpus:
            f.write(doc + '\n')
    
    # Train 3-gram model using KenLM
    subprocess.run([
        'lmplz', 
        '-o', '3',
        '--verbose_header',
        '--text', str(corpus_txt),
        '--arpa', str(arpa_file)
    ], check=True)
    
    # Convert to binary format
    subprocess.run([
        'build_binary',
        str(arpa_file),
        str(binary_file)
    ], check=True)
    
    return binary_file

def save_resources(domain_dict, brand_names, output_dir):
    """Save spelling resources to files"""
    # Save domain dictionary
    with open(Path(output_dir) / 'domain_dict.txt', 'w') as f:
        for word in sorted(domain_dict):
            f.write(f"{word}\n")
    
    # Save brand names
    with open(Path(output_dir) / 'brand_names.txt', 'w') as f:
        for brand in sorted(brand_names):
            f.write(f"{brand}\n")

def main():
    # Configuration
    PRODUCTS_JSON = "products.json"
    CORPUS_PKL = "product_corpus.pkl"
    OUTPUT_DIR = "spelling_resources"
    
    # Load data
    with open(PRODUCTS_JSON, 'r') as f:
        products = json.load(f)
    corpus = load_corpus(CORPUS_PKL)
    
    # Extract resources
    domain_dict, brand_names = extract_domain_resources(products, corpus)
    
    # Train language model
    lm_path = train_language_model(corpus, OUTPUT_DIR)
    
    # Save resources
    save_resources(domain_dict, brand_names, OUTPUT_DIR)
    
    print(f"\nSuccessfully built spelling resources in {OUTPUT_DIR}:")
    print(f"- Domain dictionary: {len(domain_dict)} words")
    print(f"- Brand names: {len(brand_names)} entries")
    print(f"- Language model: {lm_path}")

if __name__ == "__main__":
    main()