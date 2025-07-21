import json
import re
import requests
from typing import List, Dict, Tuple, Any
import pandas as pd
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class SpacyNERDataGenerator:
    def __init__(self, ollama_url: str = "http://localhost:11434/api/generate", openrouter_api_key: str = "sk-or-v1-xxx"): # update api key here
        self.ollama_url = ollama_url
        self.openrouter_api_key = openrouter_api_key
        self.entity_labels = [
            "Brand", "ManufacturerID", "Dimensions",
            "Applicable_Standards", "MainCategory", "SubCategory"
        ]

    def get_entity_mappings(self, product: Dict[str, Any]) -> Dict[str, str]:
        mappings = {label: product.get(label, '') for label in self.entity_labels}
        if isinstance(mappings["Applicable_Standards"], list):
            mappings["Applicable_Standards"] = ", ".join(mappings["Applicable_Standards"])
        return {k: str(v).strip() for k, v in mappings.items() if v}

    def build_prompt(self, product: Dict[str, Any]) -> str:
        fields = []
        for key, val in self.get_entity_mappings(product).items():
            pretty_key = key.replace("_", " ")
            fields.append(f"{pretty_key}: {val}")
        return "\n".join(fields)

    def generate_natural_sentence(self, product: Dict[str, Any]) -> str:
        prompt_text = self.build_prompt(product)
        prompt = f"""
You are a factual product description generator. Only use the data provided.
Do NOT invent or assume missing details. Here's the structured input:
{prompt_text}

Write a natural product description (max 300 characters) using ONLY this data.
Avoid generic marketing phrases. Stay factual and concrete.
"""
        try:
            return self.generate_with_claude(prompt)
        except Exception as e:
            print(f"Claude error: {e}. Falling back to Ollama...")
            return self.generate_with_ollama(prompt, product)

    def generate_with_claude(self, prompt: str) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "anthropic/claude-3-haiku",
            "messages": [
                {"role": "system", "content": "You are a factual product description generator."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 150
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except requests.exceptions.HTTPError as e:
            print("OpenRouter API error:", e)
            print("Response content:", response.text)
            raise

    def generate_with_ollama(self, prompt: str, product: Dict[str, Any]) -> str:
        payload = {
            "model": "phi3",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "max_tokens": 150}
        }
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            print(f"Error with Ollama fallback: {e}")
            return self.create_fallback_sentence(product)

    def create_fallback_sentence(self, product: Dict[str, Any]) -> str:
        parts = []
        if product.get("title"):
            parts.append(product["title"])
        if product.get("Brand"):
            parts.append(f"by {product['Brand']}")
        if product.get("MainCategory"):
            parts.append(f"in {product['MainCategory']} category")
        if product.get("Dimensions"):
            parts.append(f"with dimensions {product['Dimensions']}")
        if product.get("ManufacturerID"):
            parts.append(f"(ID: {product['ManufacturerID']})")
        return " ".join(parts)

    def find_entity_spans(self, text: str, product: Dict[str, Any]) -> List[Tuple[int, int, str]]:
        spans = []
        for entity_type, entity_value in self.get_entity_mappings(product).items():
            entity_value = str(entity_value).strip()
            if not entity_value:
                continue

            strategies = [
                lambda: text.lower().find(entity_value.lower()),
                lambda: re.search(re.escape(entity_value), text, re.IGNORECASE),
                lambda: re.search(r'\b' + r'\s+'.join(map(re.escape, entity_value.split())) + r'\b', text, re.IGNORECASE),
                lambda: next((re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE)
                              for word in entity_value.split() if len(word) > 3), None)
            ]

            found_span = None
            for strategy in strategies:
                try:
                    result = strategy()
                    if isinstance(result, int) and result != -1:
                        found_span = (result, result + len(entity_value), entity_type)
                        break
                    elif hasattr(result, 'start') and hasattr(result, 'end'):
                        found_span = (result.start(), result.end(), entity_type)
                        break
                except (re.error, AttributeError):
                    continue

            if found_span:
                spans.append(found_span)

        return self.remove_overlapping_spans(spans)

    def remove_overlapping_spans(self, spans: List[Tuple[int, int, str]]) -> List[Tuple[int, int, str]]:
        spans.sort(key=lambda x: x[0])
        filtered = []
        for span in spans:
            if not any(not (span[1] <= fs[0] or span[0] >= fs[1]) and (span[1]-span[0] <= fs[1]-fs[0]) for fs in filtered):
                filtered.append(span)
        return filtered

    def write_batch_to_csv(self, data: List[Tuple[str, Dict]], path: str, append: bool = False):
        df = pd.DataFrame([{"article": text, "labels": ann["entities"]} for text, ann in data])
        df.to_csv(path, mode='a' if append else 'w', header=not append, index=False)

    def process_product(self, product: Dict[str, Any]) -> Tuple[str, Dict]:
        sentence = self.generate_natural_sentence(product)
        spans = self.find_entity_spans(sentence, product)
        return sentence, {"entities": spans}

    def create_training_data_parallel(self, json_file_path: str, output_file_path: str, max_workers: int = 10, start: int = 0, end: int = 30000) -> List[Tuple[str, Dict]]:
        print(f"🚀 Starting data generation...")
        print(f"📂 Input file: {json_file_path}")
        print(f"💾 Output file: {output_file_path}")
        
        # Check if input file exists
        if not os.path.exists(json_file_path):
            print(f"Error: Input file {json_file_path} not found!")
            return []
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            products = data["data"]
        
        total_products = min(len(products), end) - start
        print(f"Processing {total_products} products with {max_workers} workers...")
        
        training_data = []
        completed_count = 0
        error_count = 0
        start_time = time.time()
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.process_product, product) for product in products[start:end]]
            
            for i, future in enumerate(as_completed(futures)):
                try:
                    result = future.result()
                    training_data.append(result)
                    completed_count += 1
                    
                    # Progress update every 100 completions
                    if completed_count % 100 == 0 or completed_count <= 10:
                        elapsed = time.time() - start_time
                        rate = completed_count / elapsed if elapsed > 0 else 0
                        eta = (total_products - completed_count) / rate if rate > 0 else 0
                        print(f"Completed: {completed_count}/{total_products} "
                              f"({completed_count/total_products*100:.1f}%) "
                              f"Rate: {rate:.1f}/sec ETA: {eta/60:.1f}min")
                        
                        # Show sample of recent result
                        if len(result[0]) > 0:
                            print(f"   Latest: {result[0][:100]}...")
                            if result[1]['entities']:
                                print(f"   Entities found: {len(result[1]['entities'])}")
                
                except Exception as e:
                    error_count += 1
                    print(f" Error {error_count}: {e}")

        print(f"\n Processing complete!")
        print(f"Successfully processed: {completed_count}")
        print(f"Errors: {error_count}")
        print(f"Total time: {(time.time() - start_time)/60:.1f} minutes")
        
        # Save to CSV
        print(f" Saving to {output_file_path}...")
        self.write_batch_to_csv(training_data, output_file_path)
        print(f"Saved {len(training_data)} training examples")
        
        return training_data

if __name__ == "__main__":
    generator = SpacyNERDataGenerator(openrouter_api_key="sk-or-v1-xxxx") # update api key here
    # For training data (first 30,000)
    training_data = generator.create_training_data_parallel(
        json_file_path="data/becn_data.json",
        output_file_path="output/spacy_training_data.csv",
        max_workers=5,
        start=0,
        end=30000
    )
    # For test data (next 2,000)
    test_data = generator.create_training_data_parallel(
        json_file_path="data/becn_data.json",
        output_file_path="output/spacy_test_data.csv",
        max_workers=5,
        start=30000,
        end=32000
    )