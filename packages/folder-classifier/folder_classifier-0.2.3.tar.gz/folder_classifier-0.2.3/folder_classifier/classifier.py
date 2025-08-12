from typing import Tuple
import torch
from transformers import pipeline
from folder_classifier.dto import Listing


classifier = None


def predict(listing: Listing) -> Tuple[str, float]:
    global classifier
    if classifier is None:
        classifier = pipeline(
            "text-classification",
            model="/mnt/cluster_storage/models/corto-ai/ModernBERT-large-folder-classifier",
            torch_dtype=torch.bfloat16,
            device="cuda"
        )
    text = "\n".join(listing.items)
    prediction = classifier(text)
    predicted_label = prediction[0]["label"]
    confidence = prediction[0]["score"]
    return predicted_label, confidence


