import os
import sentencepiece as spm
from ugtext_processer.tokenizer.base_tokenizer import BaseTokenizer


class SentencePieceTokenizer(BaseTokenizer):
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.sp = spm.SentencePieceProcessor()
        if model_path and os.path.exists(model_path):
            self.sp.load(model_path)

    def train_tokenizer(self, corpus_path: str, model_prefix: str = "spm", vocab_size: int = 50000,
                        model_type: str = "unigram", save_dir: str = "./", **kwargs):
        if not os.path.exists(corpus_path):
            raise FileNotFoundError(f"Corpus file not found: {corpus_path}")

        os.makedirs(save_dir, exist_ok=True)

        model_prefix_full = os.path.join(save_dir, model_prefix)
        spm.SentencePieceTrainer.train(
            input=corpus_path,
            model_prefix=model_prefix_full,
            vocab_size=vocab_size,
            model_type=model_type,
            character_coverage=1.0,
            unk_id=0,
            bos_id=1,
            eos_id=2,
            pad_id=3,
            **kwargs
        )

        self.model_path = model_prefix_full + ".model"
        self.sp.load(self.model_path)

    def tokenize(self, text: str, **kwargs):
        if not self.sp:
            raise ValueError("Tokenizer is not initialized. Train or load a model first.")
        return self.sp.encode(text, out_type=str)

    def save_tokenizer(self, file_path: str, **kwargs):
        if not self.model_path or not os.path.exists(self.model_path):
            raise ValueError("No model to save. Train the tokenizer first.")
        os.rename(self.model_path, file_path)
        self.model_path = file_path

    def load_tokenizer(self, file_path: str, **kwargs):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Model file not found: {file_path}")
        self.model_path = file_path
        self.sp.load(file_path)

    def verbose(self, **kwargs) -> str:
        if not self.model_path:
            return "SentencePieceTokenizer (not loaded)"
        return (
            f"SentencePieceTokenizer\n"
            f"  Model path: {self.model_path}\n"
            f"  Vocabulary size: {self.sp.get_piece_size()}"
        )
