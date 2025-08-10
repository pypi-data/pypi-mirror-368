"""Module for training error detection models."""

import os
import pickle
from typing import Any, Dict, List, Optional

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import (AdamW, RobertaTokenizer, T5Tokenizer,
                          get_linear_schedule_with_warmup)

from .models import CodeBERTClassifier, T5Generator


class CodeDataset(Dataset):
    """Custom dataset for code."""
    def __init__(self, tokenizer, data, max_length):
        self.tokenizer = tokenizer
        self.data = data
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        code = item['code']
        inputs = self.tokenizer.encode_plus(
            code,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            return_attention_mask=True,
            return_tensors='pt',
            truncation=True
        )
        return {
            'input_ids': inputs['input_ids'].flatten(),
            'attention_mask': inputs['attention_mask'].flatten(),
            'labels': torch.tensor(item['label'], dtype=torch.long)
        }


class ModelTrainer:
    """Class for training code error detection models."""

    def __init__(self, model_type: str = 'codebert', output_path: Optional[str] = None):
        self.model_type = model_type
        self.output_path = output_path
        self.model = None
        self.tokenizer = None

        if self.model_type == 'codebert':
            self.model = CodeBERTClassifier()
            self.tokenizer = RobertaTokenizer.from_pretrained('microsoft/codebert-base')
        elif self.model_type == 't5':
            self.model = T5Generator()
            self.tokenizer = T5Tokenizer.from_pretrained('t5-small')
        else:
            raise ValueError("Unsupported model type. Choose 'codebert' or 't5'.")

    def train(self, dataset: List[Dict], epochs: int = 3, batch_size: int = 8, learning_rate: float = 2e-5):
        """Train the model."""
        self.model.train()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(device)

        train_dataset = CodeDataset(self.tokenizer, dataset, max_length=512)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

        for epoch in range(epochs):
            print(f"Epoch {epoch + 1}/{epochs}")
            for batch in train_loader:
                optimizer.zero_grad()
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)

                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss if hasattr(outputs, 'loss') else outputs.logits
                loss.backward()
                optimizer.step()
                scheduler.step()
        print("Training complete.")

    def save_model(self):
        """Save the trained model."""
        if self.output_path:
            os.makedirs(self.output_path, exist_ok=True)
            torch.save(self.model.state_dict(), os.path.join(self.output_path, "pytorch_model.bin"))
            self.tokenizer.save_pretrained(self.output_path)
            print(f"Model saved to {self.output_path}")