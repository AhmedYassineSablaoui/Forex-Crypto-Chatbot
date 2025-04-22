# backend/predict.py
import torch
import os
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from config import MODEL_NAME, MODEL_PATH, MAX_LENGTH, DEVICE

# Verify the directory exists
if not os.path.isdir(MODEL_PATH):
    print(f"Error: Directory {MODEL_PATH} does not exist.")
    print(f"Current working directory: {os.getcwd()}")
    print("Falling back to default model (untrained).")
    tokenizer = DistilBertTokenizer.from_pretrained(MODEL_NAME)
    model = DistilBertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
else:
    # Load the tokenizer and model from the saved directory
    try:
        tokenizer = DistilBertTokenizer.from_pretrained(MODEL_PATH)
        model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
        print(f"Loaded trained model and tokenizer from {MODEL_PATH}")
    except Exception as e:
        print(f"Error loading model from {MODEL_PATH}: {e}")
        print("Falling back to default model (untrained).")
        tokenizer = DistilBertTokenizer.from_pretrained(MODEL_NAME)
        model = DistilBertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

model.eval()
model.to(DEVICE)

def predict_query(query):
    """
    Classify a user query as FAQ or Non-FAQ using the DistilBERT model.
    
    Args:
        query (str): The user query to classify.
    
    Returns:
        tuple: (label, confidence) where label is "FAQ" or "Non-FAQ" and confidence is a float.
    """
    # Tokenize the input query
    inputs = tokenizer(
        query,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=MAX_LENGTH
    )
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    # Make prediction
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0][predicted_class].item()

    # Map the predicted class to a label
    label = "FAQ" if predicted_class == 1 else "Non-FAQ"
    return label, confidence

# Test the prediction function
if __name__ == "__main__":
    test_queries = [
        "What is the difference between Bitcoin and Ethereum?",
        "What is the capital of France?"
    ]
    for query in test_queries:
        label, confidence = predict_query(query)
        print(f"Query: {query}")
        print(f"Predicted: {label} (Confidence: {confidence:.4f})\n")