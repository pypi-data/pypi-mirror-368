import re
import argparse

class UyghurPunctuationNormalizer(object):
    def __init__(self):
        """
        Uyghur punctuation normalizer for TTS input.
        Removes noisy symbols, normalizes punctuation and whitespace.
        """
        self.symbol_map = {
            '“': '"', '”': '"', '‘': "'", '’': "'",
            '،': ',', '；': ';', '：': ':',
            '؟': '?', '！': '!',
            '（': '(', '）': ')',
            '【': '[', '】': ']',
            '—': '-', '…': '...', '《': '"', '》': '"',
        }

        self.noise_pattern = re.compile(
            r'[\u263a-\U0001f645]|[#@♪★☆•·→←▲▼▶◀→←💡🔔🔊🚀✨❤💥🌀🧠🔥👀👍👎👏🖐️📝📢🔍📌🎯📊📈💡⏰]'
        )
        self.multispace_pattern = re.compile(r'\s+')

    def normalize(self, text: str) -> str:
        """
        Normalize punctuation using Uyghur punctuation
        :param text: text to be normalized
        :return: normalized text
        """
        text = self._replace_symbols(text)
        text = self._remove_noise(text)
        text = self._normalize_whitespace(text)
        text = text.strip()
        text = re.sub(r'\s+([.?!,:;])', r'\1', text)
        return text

    def _replace_symbols(self, text: str) -> str:
        """
        Replace symbols with their respective punctuation marks
        :param text: text to be processed
        :return: processed text
        """
        for orig, repl in self.symbol_map.items():
            text = text.replace(orig, repl)
        return text

    def _remove_noise(self, text: str) -> str:
        """
        Remove noise
        :param text: text to be processed
        :return: processed text
        """
        return self.noise_pattern.sub('', text)

    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace
        :param text: text to be processed
        :return: processed text
        """
        return self.multispace_pattern.sub(' ', text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean Uyghur text for TTS input")
    parser.add_argument("text", type=str, help="Raw Uyghur sentence to normalize")
    args = parser.parse_args()

    normalizer = UyghurPunctuationNormalizer()
    normalized = normalizer.normalize(args.text)
    print(normalized)
