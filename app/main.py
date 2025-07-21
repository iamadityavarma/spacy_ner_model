
# import argparse
# from app.ner_utils import load_model, extract_entities
# from app.spell_corrector import correct_text, load_corpus

# nlp = load_model()

# def main(use_spellcheck=False):
#     load_corpus("custom_corpus.pkl")  # Load once at start

#     with open("test_samples/examples.txt") as f:
#         samples = f.readlines()

#     for i, text in enumerate(samples):
#         text = text.strip()
#         corrected_text = correct_text(text) if use_spellcheck else text
#         ents = extract_entities(corrected_text, nlp)

#         print(f"\nSample #{i+1}")
#         print("Original: ", text)
#         if use_spellcheck:
#             print("Corrected:", corrected_text)
#         print("Entities:", ents)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--spellcheck", action="store_true", help="Run with spellcheck")
#     args = parser.parse_args()

#     main(use_spellcheck=args.spellcheck)

import logging
from flask import Flask, request, render_template_string
from ner import load_model, extract_entities
from spellCorrector import correct_text, load_corpus
import pdb

# Load the SpaCy model and custom corpus once at startup
nlp = load_model()
load_corpus("app/customCorpus.pkl")

# Configure logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log', mode='a'),
    ]
)

# Initialize Flask app
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Handle GET and POST requests for the main page.
    - On GET: Render the input form.
    - On POST: Process the input text, apply spellcheck if selected, extract entities, and render results.
    Returns:
        Rendered HTML page with results (if POST) or input form (if GET)
    """
    if request.method == "POST":
        # Get user input from form
        text = request.form.get("text", "")
        use_spellcheck = request.form.get("spellcheck") == "on"

        # Optionally correct the text
        corrected_text = correct_text(text) if use_spellcheck else text
        # Extract entities from the (corrected) text
        ents = extract_entities(corrected_text, nlp)

        # Render the template with results
        return render_template_string(TEMPLATE, original=text,
                                      corrected=corrected_text if use_spellcheck else None,
                                      entities=ents)

    # Render the input form on GET
    return render_template_string(TEMPLATE)

# HTML template for the web interface
TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>NER Extractor</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f5f7fa;
      margin: 0;
      padding: 40px;
      color: #333;
    }
    h2 {
      color: #2c3e50;
      text-align: center;
    }
    form {
      background: #ffffff;
      max-width: 800px;
      margin: auto;
      padding: 30px;
      border-radius: 12px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    textarea {
      width: 100%;
      padding: 12px;
      font-size: 16px;
      border-radius: 8px;
      border: 1px solid #ccc;
      resize: vertical;
    }
    label {
      font-weight: bold;
    }
    input[type="submit"] {
      background-color: #3498db;
      color: white;
      padding: 12px 20px;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-size: 16px;
      margin-top: 15px;
    }
    input[type="submit"]:hover {
      background-color: #2980b9;
    }
    .results {
      max-width: 800px;
      margin: 30px auto;
      background: #ffffff;
      padding: 25px;
      border-radius: 12px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .entity-list {
      list-style-type: none;
      padding-left: 0;
    }
    .entity-list li {
      padding: 8px;
      margin-bottom: 6px;
      background-color: #ecf0f1;
      border-left: 6px solid #3498db;
      border-radius: 6px;
    }
    .label {
      font-weight: bold;
      color: #2c3e50;
    }
  </style>
</head>
<body>
  <h2>Named Entity Recognition App</h2>
  <form method="post">
    <label for="text">Enter your product text:</label><br>
    <textarea name="text" rows="5" placeholder="Paste product description here...">{{ original or "" }}</textarea><br><br>
    <label><input type="checkbox" name="spellcheck" {% if corrected %}checked{% endif %}> Apply spellcheck</label><br><br>
    <input type="submit" value="Extract Entities">
  </form>

  {% if corrected is not none %}
  <div class="results">
    <h3>Corrected Text:</h3>
    <p>{{ corrected }}</p>
  </div>
  {% endif %}

  {% if entities %}
  <div class="results">
    <h3>Entities:</h3>
    <ul class="entity-list">
    {% for ent in entities %}
      <li><span class="label">{{ ent['label'] }}</span>: {{ ent['text'] }}</li>
    {% endfor %}
    </ul>
  </div>
  {% endif %}
</body>
</html>
"""

if __name__ == "__main__":
    # Run the Flask app in debug mode
    app.run(debug=False)


# from flask import Flask, request, jsonify, render_template_string
# from ner import load_model, extract_entities
# from spellCorrector import correct_text, load_corpus

# if __name__ == "__main__":
#     load_corpus("custom_corpus.pkl")
#     sentence = "azekc trim baord is beautifull and eldorado stonne is certfied"
#     corrected = correct_text(sentence)
#     print("Corrected:", corrected)

