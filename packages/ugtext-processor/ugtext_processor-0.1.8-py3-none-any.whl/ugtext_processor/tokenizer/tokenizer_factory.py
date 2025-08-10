from enum import Enum
from typing import Type

from ugtext_processor.tokenizer.base_tokenizer import BaseTokenizer
from ugtext_processor.tokenizer.bpe_tokenizer import BpeTokenizer
from ugtext_processor.tokenizer.char_tokenizer import CharTokenizer
from ugtext_processor.tokenizer.sentencepiece_tokenizer import SentencePieceTokenizer
from ugtext_processor.tokenizer.word_tokenizer import WordTokenizer
from ugtext_processor.tokenizer.wordpiece_tokenizer import WordpieceTokenizer


class TokenizerType(Enum):
    WORD = "word"             # Tokenization based on spaces or linguistic rules
    CHARACTER = "char"        # Each character is treated as a token
    BPE = "bpe"               # Byte Pair Encoding, used in GPT/BERT
    WORDPIECE = "wordpiece"   # WordPiece, used in BERT
    SENTENCEPIECE = "sentencepiece"  # Unsupervised subword tokenization



def get_tokenizer_class(tokenizer_type: TokenizerType) -> Type[BaseTokenizer]:
    """
    Returns the tokenizer class based on the specified type.
    :param tokenizer_type: Type of tokenizer to return
    :return: Corresponding tokenizer class
    """

    if tokenizer_type == TokenizerType.WORD:
        return WordTokenizer
    elif tokenizer_type == TokenizerType.CHARACTER:
        return CharTokenizer
    elif tokenizer_type == TokenizerType.BPE:
        return BpeTokenizer
    elif tokenizer_type == TokenizerType.WORDPIECE:
        return WordpieceTokenizer
    elif tokenizer_type == TokenizerType.SENTENCEPIECE:
        return SentencePieceTokenizer
    else:
        raise ValueError(f"Unknown tokenizer type: {tokenizer_type}")