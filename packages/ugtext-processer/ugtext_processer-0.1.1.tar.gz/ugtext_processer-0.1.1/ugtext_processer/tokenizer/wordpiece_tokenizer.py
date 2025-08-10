

import os
from typing import Any
from tokenizers import Tokenizer, models, trainers, pre_tokenizers
from ugtext_processer.tokenizer.base_tokenizer import BaseTokenizer


class WordpieceTokenizer(BaseTokenizer):
    def __init__(self, tokenizer: Tokenizer = None):
        self.tokenizer = tokenizer
        self.tokenizer_path = None

    def train_tokenizer(self, corpus_path: str, save_dir: str = None, vocab_size: int = 50000, **kwargs) -> Any:
        if not os.path.exists(corpus_path):
            raise FileNotFoundError(f"file not found : {corpus_path}")

        tokenizer = Tokenizer(models.WordPiece(unk_token="[UNK]"))
        tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()

        trainer = trainers.WordPieceTrainer(
            vocab_size=vocab_size,
            special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]
        )

        tokenizer.train([corpus_path], trainer)

        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            self.tokenizer_path = os.path.join(save_dir, "tokenizer.json")
            tokenizer.save(self.tokenizer_path)
        else:
            self.tokenizer_path = None

        self.tokenizer = tokenizer
        return tokenizer

    def tokenize(self, text: str, **kwargs) -> Any:
        if not self.tokenizer:
            raise ValueError("Please load tokenizer")
        return self.tokenizer.encode(text).tokens

    def save_tokenizer(self, file_path: str, **kwargs) -> None:
        if not self.tokenizer:
            raise ValueError("tokenizer is not initialized, please train or load it first")
        self.tokenizer.save(file_path)
        self.tokenizer_path = file_path

    def load_tokenizer(self, file_path: str, **kwargs) -> None:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"tokenizer file not found : {file_path}")
        self.tokenizer = Tokenizer.from_file(file_path)
        self.tokenizer_path = file_path

    def verbose(self, **kwargs) -> str:
        if not self.tokenizer:
            return "Tokenizer not initialized. Please train or load a tokenizer first "
        info = f"WordPieceTokenizer\n"
        if self.tokenizer_path:
            info += f" model path : {self.tokenizer_path}\n"
        info += f"  vocab size: {self.tokenizer.get_vocab_size()}"
        return info


