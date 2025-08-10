import re
from typing import List

from ugtext_processor.tokenizer.base_tokenizer import BaseTokenizer


class WordTokenizer(BaseTokenizer):
    """
    Tokenizer for Uyghur script that can tokenize text by:
    - Removing punctuation and splitting by whitespace
    - Keeping punctuation as separate tokens
    """

    def tokenize(self, text: str, keep_punctuation: bool = False) -> List[str]:
        """
        Tokenizes the input text into words.
        :param text: input string
        :param keep_punctuation: whether to keep punctuation as separate tokens
        :return: list of tokens
        """
        if keep_punctuation:
            return re.findall(r"\w+|[،؛؟。：！？…«»“”‘’.,!?]", text)
        else:
            text = re.sub(r"[،؛؟؟۔۔٫٪…«»“”‘’\"'.,!?؛:]", "", text)
            return text.split()


if __name__ == "__main__":
    text_tmp = "بۈگۈن ئۇيغۇر تىلى كۈنى بولۇپ، دۇنيانىڭ ھەرقايسى جايلىرىدىكى ئۇيغۇرلار بۇ كۈننى ئۆزگىچە خاتىرىلەيدۇ."
    tokenizer = WordTokenizer()
    tokens_no_punc = tokenizer.tokenize(text_tmp)
    print("No punctuation:", tokens_no_punc)

    tokens_with_punc = tokenizer.tokenize(text_tmp, keep_punctuation=True)
    print("With punctuation:", tokens_with_punc)
