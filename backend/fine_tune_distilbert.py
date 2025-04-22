import pandas as pd
from datasets import Dataset
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
import torch
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


# Step 1: Load the dataset
try:
    df = pd.read_csv("faq_data_cleaned.csv")
    print("Dataset balance:")
    print(df['label'].value_counts())
    dataset = Dataset.from_pandas(df)
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit(1)

# Step 2: Load tokenizer and model
try:
    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-multilingual-cased")
    model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-multilingual-cased", num_labels=2)
except Exception as e:
    print(f"Error loading tokenizer or model: {e}")
    exit(1)

# Move to GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)
print(f"Running on: {device}")

# Step 3: Preprocess the dataset
def preprocess_function(examples):
    return tokenizer(examples["text"], truncation=True, padding='max_length', max_length=64)

try:
    tokenized_dataset = dataset.map(preprocess_function, batched=True)
    tokenized_dataset = tokenized_dataset.rename_column("label", "labels")
    tokenized_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'labels'])
except Exception as e:
    print(f"Error preprocessing dataset: {e}")
    exit(1)

# Step 4: Split into train and test sets (80% train, 20% test)
train_test = tokenized_dataset.train_test_split(test_size=0.2)
train_dataset = train_test['train']
eval_dataset = train_test['test']

# Step 5: Compute class weights for imbalanced dataset
labels = train_dataset['labels'].numpy()
class_weights = len(labels) / (2 * np.bincount(labels))  # Inverse frequency
class_weights = torch.tensor(class_weights, dtype=torch.float).to(device)
print(f"Class weights: {class_weights}")

# Step 6: Custom Trainer to use class weights
class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        loss_fct = torch.nn.CrossEntropyLoss(weight=class_weights)
        loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

# Step 7: Define compute_metrics for evaluation
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

# Step 8: Define training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=10,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

# Step 9: Initialize Trainer
trainer = WeightedTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
)

# Step 10: Train the model
try:
    trainer.train()
except Exception as e:
    print(f"Error during training: {e}")
    exit(1)

# Step 11: Save the fine-tuned model to models/
try:
    model.save_pretrained('./models/forex_distilbert')
    tokenizer.save_pretrained('./models/forex_distilbert')
    print("Model saved to ./models/forex_distilbert")
except Exception as e:
    print(f"Error saving model: {e}")
    exit(1)