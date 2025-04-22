# backend/config.py
import torch

# Model settings
MODEL_NAME = "distilbert-base-multilingual-cased"
MODEL_PATH = "/home/ahmed/projects/Forex-Crypto-chatbot/backend/models/forex_distilbert"  # Absolute path
MAX_LENGTH = 128  # Maximum token length for input queries

# Device configuration
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# FAQ response settings
FAQ_CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence to classify as FAQ