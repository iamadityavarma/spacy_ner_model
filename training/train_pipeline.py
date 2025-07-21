import pandas as pd
import ast
from sklearn.model_selection import train_test_split
import spacy
from spacy.tokens import DocBin
import logging
import argparse
import os

def setup_logging(log_path='logs/trainPipeline.log'):
    """Configure logging to file and console."""
    os.makedirs(os.path.dirname(log_path) or '.', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_path,
        filemode='w'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def convert_to_docbin(dataframe, nlp, filename):
    """Convert a DataFrame to spaCy DocBin and save to disk."""
    logging.info(f"Converting {len(dataframe)} records to DocBin and saving to {filename}...")
    doc_bin = DocBin()
    for i, (text, annotations) in enumerate(zip(dataframe['article'], dataframe['labels'])):
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annotations:
            span = doc.char_span(start, end, label=label)
            if span is not None:
                ents.append(span)
        doc.ents = ents
        doc_bin.add(doc)
        if (i+1) % 100 == 0:
            logging.info(f"Processed {i+1} documents...")
    doc_bin.to_disk(filename)
    logging.info(f"Saved DocBin to {filename}.")

def main(csv_path, train_path, dev_path, test_size=0.2, random_state=42):
    """Main pipeline for converting CSV NER data to spaCy DocBin format."""
    setup_logging()
    logging.info(f"Loading CSV file: {csv_path}")
    df = pd.read_csv(csv_path)
    logging.info(f"Loaded {len(df)} rows from CSV.")

    logging.info("Converting stringified label lists to actual lists...")
    df['labels'] = df['labels'].apply(ast.literal_eval)
    logging.info("Label conversion complete.")

    logging.info("Splitting data into train and test sets...")
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=random_state)
    logging.info(f"Train size: {len(train_df)}; Test size: {len(test_df)}")

    print(f"Train size: {len(train_df)}")
    print(f"Test size: {len(test_df)}")

    nlp = spacy.blank("en")
    convert_to_docbin(train_df, nlp, train_path)
    convert_to_docbin(test_df, nlp, dev_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert NER CSV data to spaCy DocBin format.")
    parser.add_argument('--csv', type=str, default='output/spacy_training_data.csv', help='Path to input CSV file')
    parser.add_argument('--train', type=str, default='training/train.spacy', help='Path to output train DocBin file')
    parser.add_argument('--dev', type=str, default='training/dev.spacy', help='Path to output dev DocBin file')
    parser.add_argument('--test_size', type=float, default=0.2, help='Test set size fraction')
    parser.add_argument('--random_state', type=int, default=42, help='Random state for splitting')
    parser.add_argument('--eval_csv', type=str, default="output/spacy_test_data.csv", help='(Optional) Path to evaluation CSV file')
    parser.add_argument('--eval_out', type=str, default="training/test.spacy", help='(Optional) Path to output eval DocBin file')
    args = parser.parse_args()

    main(args.csv, args.train, args.dev, args.test_size, args.random_state)

    # Optional: Convert evaluation data if provided
    if args.eval_csv and args.eval_out:
        logging.info(f"Loading evaluation CSV file: {args.eval_csv}")
        eval_df = pd.read_csv(args.eval_csv)
        logging.info(f"Loaded {len(eval_df)} rows from evaluation CSV.")
        logging.info("Converting stringified label lists to actual lists for evaluation data...")
        eval_df['labels'] = eval_df['labels'].apply(ast.literal_eval)
        logging.info("Label conversion complete for evaluation data.")
        nlp = spacy.blank("en")
        convert_to_docbin(eval_df, nlp, args.eval_out)
        logging.info(f"Evaluation data saved to {args.eval_out}.")