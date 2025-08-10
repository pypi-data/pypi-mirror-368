from pathlib import Path
from typing import Optional, List

from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.trainers import BpeTrainer

from ugtext_processor.tokenizer.base_tokenizer import BaseTokenizer




class BpeTokenizer(BaseTokenizer):
    """
    BPE tokenizer using HuggingFace tokenizers library.
    Implements the abstract Tokenizer interface.
    """

    def __init__(self, special_tokens: Optional[List[str]] = None):
        """
        Initializes the BPE tokenizer.
        :param special_tokens:  List of special tokens to add to the tokenizer.
        """
        self.tokenizer: Optional[Tokenizer] = None
        self.special_tokens = special_tokens or ["<unk>", "<pad>", "<bos>", "<eos>", "<mask>", "<cls>", "<sep>"]

    def train_tokenizer(self, corpus_path: str, saving_path: str, vocab_size: int = 50000) -> Tokenizer:
        """
        Trains a BPE tokenizer using a single corpus file.
        :param corpus_path: Path to a text file with one sentence per line.
        :param vocab_size: Size of the vocabulary to be generated.
        :return: Trained Tokenizer instance.
        """

        print(f"[BPE] start training ：{corpus_path}")

        if not Path(corpus_path).is_file():
            raise FileNotFoundError(f"file not found : {corpus_path}  ")

        self.tokenizer = Tokenizer(BPE())
        self.tokenizer.pre_tokenizer = Whitespace()

        trainer = BpeTrainer(vocab_size=vocab_size, special_tokens=self.special_tokens )
        self.tokenizer.train([corpus_path], trainer)

        print(f"[BPE] training finish，vocab size : {self.tokenizer.get_vocab_size()}")

        self.save_tokenizer(saving_path)

        return self.tokenizer

    def tokenize(self, text: str, **kwargs) -> List[str]:
        """
        Tokenizes the input text into a list of tokens.
        :param text: The text to tokenize.
        :return: A list of string tokens.
        """
        if not self.tokenizer:
            raise RuntimeError("Tokenizer has not been trained or loaded yet.")

        return self.tokenizer.encode(text).tokens

    def save_tokenizer(self, file_path: str, **kwargs) -> None:
        """
        Saves the tokenizer to a file.
        :param file_path: Path to save the tokenizer (e.g., 'data/tokenizer/bpe.json').
        """
        if not self.tokenizer:
            raise RuntimeError("No tokenizer to save. Train one first.")

        save_path = Path(file_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.tokenizer.save(str(save_path))
            logger.info(f"[BPE] Tokenizer saved to: {save_path}")
        except Exception as e:
            logger.error(f"Error saving BPE tokenizer to {save_path}: {e}")

    def load_model(self, path: str):
        try:
            self.tokenizer = Tokenizer.from_file(path)
            print(f"[BPE] Tokenizer loaded from: {path}")
        except Exception as e:
            print(f"Error loading BPE tokenizer from {path}: {e}")
            self.tokenizer = None # Set to None if loading fails

    def verbose(self, **kwargs) -> str:
        """
        Returns a verbose description of the tokenizer.
        """
        if not self.tokenizer:
            return "BpeTokenizer (not trained/loaded)"

        vocab_size = self.tokenizer.get_vocab_size()
        return f"BpeTokenizer (HuggingFace) | Vocab size: {vocab_size} | Special tokens: {self.special_tokens}"
