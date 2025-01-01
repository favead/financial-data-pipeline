from typing import List

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pymorphy3


nltk.download("stopwords")
nltk.download("punkt_tab")


class TextProcesser:
    """
    Text handler for analyze and processing data
    """

    def __init__(self) -> None:
        self.morph = pymorphy3.MorphAnalyzer()
        self.stop_words_ru = set(stopwords.words("russian"))
        self.stop_words_en = set(stopwords.words("english"))
        self.all_stopwords = self.stop_words_en | self.stop_words_ru

    def process_text(self, text: str) -> List[str]:
        """
        Auto detect language (en or ru) and apply:
        - tokenization
        - lematization
        - delete stop words

        Parameters
        ----------
        text: str
            Input data in russian or english language

        Returns
        -------
        List[str]
            Tokens without stop words in normal form
        """
        tokens = word_tokenize(text)
        processed_tokens = []
        for token in tokens:
            token_lower = token.lower()
            if not (
                token_lower.isalpha()
                and any(c.isalpha() for c in token_lower)
                and token_lower not in self.all_stopwords
            ):
                continue
            lemma = self.morph.parse(token)[0].normal_form
            processed_tokens.append(lemma)
        return processed_tokens
