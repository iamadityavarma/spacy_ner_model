# Named Entity Recognition (NER) Project

This project provides a pipeline for training and evaluating a custom spaCy NER model, including spell correction and a Flask web app for entity extraction.

## Training and Evaluation Data Preparation

The script `training/train_pipeline.py` can be used to convert your annotated CSV data into spaCy's DocBin format for training, development, and evaluation.

### Usage

```sh
python training/train_pipeline.py \
  --csv output/spacy_training_data.csv \
  --train training/train.spacy \
  --dev training/dev.spacy \
  --eval_csv output/spacy_test_data.csv \
  --eval_out training/test.spacy
```

- `--csv`: Path to your main training CSV file (default: `output/spacy_training_data.csv`)
- `--train`: Output path for the training DocBin file (default: `training/train.spacy`)
- `--dev`: Output path for the dev DocBin file (default: `training/dev.spacy`)
- `--eval_csv`: (Optional) Path to your evaluation/test CSV file (default: `output/spacy_test_data.csv`)
- `--eval_out`: (Optional) Output path for the evaluation DocBin file (default: `training/test.spacy`)

If you provide `--eval_csv` and `--eval_out`, the script will also process your evaluation dataset and save it in spaCy DocBin format.

### Example

To generate all three files (train, dev, eval):

```sh
python training/train_pipeline.py --csv output/spacy_training_data.csv --train training/train.spacy --dev training/dev.spacy --eval_csv output/spacy_test_data.csv --eval_out training/test.spacy
```

## Project Structure
- `app/` - Flask web app, NER logic, spell correction
- `training/` - Data processing and training pipeline
- `models/` - Trained spaCy model files
- `data/` - Product data and sample JSONs
- `requirements.txt` - Python dependencies
- `dockerfile` - Docker setup for deployment

## Notes
- Make sure your CSVs have the correct format: columns `article` (text) and `labels` (list of entity spans).
- For large files/models, consider using Git LFS or storing them outside your main repository.

---
Feel free to expand this README with more details about the web app, spell correction, or deployment as needed!
