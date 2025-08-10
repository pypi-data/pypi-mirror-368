from abc import ABC, abstractmethod
from typing import Any


class BaseTokenizer(ABC):
    """
    abstract base class for text tokenizers
    """

    @abstractmethod
    def tokenize(self, text: str, **kwargs) -> Any:
        """
        Tokenizes the input text into a list of tokens
        this method must be implemented by subclasses
        """
        pass

    def train_tokenizer(self, corpus_path: str, **kwargs) -> Any:
        """
        Trains the tokenizer on the provided corpus
        :param corpus_path: Path to the text corpus for training
        :return: Trained tokenizer object
        """
        raise NotImplementedError("This method should be implemented by subclasses ")

    def save_tokenizer(self, file_path: str, **kwargs) -> None:
        """
        Saves the tokenizer to a file.
        :param file_path: Path to save the tokenizer
        """
        raise NotImplementedError("This method should be implemented by subclasses")

    def load_tokenizer(self, file_path: str, **kwargs) -> None:
        """
        Loads the tokenizer from a file.
        :param file_path: Path to load the tokenizer from
        """
        raise NotImplementedError("This method should be implemented by subclasses")

    def verbose(self,**kwargs) -> str:
        """
        verbose corresponds to the tokenizer
        """
        raise NotImplementedError("This method should be implemented by subclasses")
