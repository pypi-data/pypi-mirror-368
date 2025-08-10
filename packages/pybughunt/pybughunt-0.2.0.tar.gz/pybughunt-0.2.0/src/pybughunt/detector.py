"""Main module for detecting errors in Python code."""

import os
from typing import Dict, List, Optional

import torch
from transformers import RobertaTokenizer, T5Tokenizer

from .logic_analyzer import LogicAnalyzer
from .models.models import CodeBERTClassifier, T5Generator
from .syntax_analyzer import SyntaxAnalyzer


class CodeErrorDetector:
    """Main class for detecting errors in Python code."""

    def __init__(self, model_type: str = 'static', model_path: Optional[str] = None):
        self.syntax_analyzer = SyntaxAnalyzer()
        self.model_type = model_type
        self.model = None
        self.tokenizer = None
        self.logic_analyzer = LogicAnalyzer(None) # For static analysis

        if self.model_type != 'static':
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            if self.model_type == 'codebert':
                self.model = CodeBERTClassifier()
                self.tokenizer = RobertaTokenizer.from_pretrained('microsoft/codebert-base')
            elif self.model_type == 't5':
                self.model = T5Generator()
                self.tokenizer = T5Tokenizer.from_pretrained('t5-small')

            if model_path and os.path.exists(os.path.join(model_path, "pytorch_model.bin")):
                self.model.load_state_dict(torch.load(os.path.join(model_path, "pytorch_model.bin"), map_location=device))
            self.model.to(device)
            self.model.eval()

    def analyze(self, code: str) -> Dict[str, List[Dict]]:
        """Analyze Python code for errors."""
        result = {"syntax_errors": [], "logic_errors": []}
        syntax_errors = self.syntax_analyzer.analyze(code)
        if syntax_errors:
            result["syntax_errors"] = syntax_errors
            return result

        if self.model_type == 'static':
            result["logic_errors"] = self.logic_analyzer.analyze(code)
        elif self.model:
            inputs = self.tokenizer(code, return_tensors='pt', max_length=512, padding='max_length', truncation=True)
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.no_grad():
                if self.model_type == 'codebert':
                    outputs = self.model(**inputs)
                    prediction = torch.argmax(outputs, dim=1).item()
                    if prediction == 1:
                        result["logic_errors"].append({"line": 0, "message": "Logical error detected by CodeBERT"})
                elif self.model_type == 't5':
                    outputs = self.model.generate(inputs['input_ids'], attention_mask=inputs['attention_mask'])
                    error_desc = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                    if error_desc:
                        result["logic_errors"].append({"line": 0, "message": f"T5 Suggestion: {error_desc}"})

        return result