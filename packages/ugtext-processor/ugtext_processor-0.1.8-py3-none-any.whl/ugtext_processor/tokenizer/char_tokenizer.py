import re

from ugtext_processor.tokenizer.base_tokenizer import BaseTokenizer


class CharTokenizer(BaseTokenizer):
    """
    Character-level tokenizer: returns a list of characters as tokens
    """

    def tokenize(self,text: str, keep_punctuation: bool = False) -> list[str]:
        """
        Tokenizes the input text into characters.
        :param text: input string
        :param keep_punctuation: whether to keep punctuation as characters
        :return: list of character tokens
        """
        if not keep_punctuation:
            # Remove punctuation before splitting into characters
            text = re.sub(r"[،؛؟。：！？…«»“”‘’\"'.,!?؛:]", "", text)
        return list(text)



if __name__ == "__main__":
    text = "بۈگۈن ئۇيغۇر تىلى كۈنى بولۇپ، دۇنيانىڭ ھەرقايسى جايلىرىدىكى ئۇيغۇرلار بۇ كۈننى ئۆزگىچە خاتىرىلەيدۇ."
    tokens_no_punc = CharTokenizer.tokenize(text)
    print(tokens_no_punc)
    tokens_with_punc = CharTokenizer.tokenize(text, keep_punctuation=True)
    print(tokens_with_punc)
