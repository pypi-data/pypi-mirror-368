from typing import List
from dataclasses import dataclass


@dataclass
class ChineseSentenceSplitter:
    buffer: str = ""
    min_sentence_length: int = 10
    use_level2_threshold: int = 30
    use_level3_threshold: int = 100

    def process_text(
        self,
        text: str,
        is_last: bool = False,
        special_text: str | None = None,
    ) -> List[str]:
        self.buffer = self.buffer + text
        if special_text is not None:
            if self.buffer.endswith(special_text):
                return [self.buffer]
        sentences, indices = self.split_sentences(self.buffer)
        assert len(sentences) == len(indices), (
            "The number of sentences and indices do not match"
        )
        if not is_last:
            if len(indices) != 0:
                self.buffer = self.buffer[indices[-1] + 1 :]
            return sentences
        else:
            if len(sentences) == 0:
                sentences = [self.buffer]
                self.buffer = ""
                return sentences
            if indices[-1] == len(self.buffer) - 1:
                self.buffer = ""
                return sentences
            else:
                self.buffer = ""
                return sentences + [text[indices[-1] + 1 :]]

    def split_sentences(self, text: str) -> List[str]:
        indices = self.get_sentence_end_indices(text)
        sentences = []
        sent_indices = []
        start = 0
        for i in indices:
            sent = text[start : i + 1]
            if len(sent) > 0 and len(sent) >= self.min_sentence_length:
                sentences.append(sent)
                sent_indices.append(i)
                start = i + 1
        return sentences, sent_indices

    def is_sentence_end_level1(self, text: str) -> bool:
        return text.endswith(
            (
                "!",
                "?",
                "。",
                "？",
                "！",
                "；",
                ";",
            )
        )

    def is_sentence_end_level2(self, text: str) -> bool:
        return text.endswith(
            (
                "、",
                "...",
                "…",
                ",",
                "，",
            )
        )

    def is_sentence_end_level3(self, text: str) -> bool:
        return text.endswith(
            (
                ":",
                "：",
            )
        )

    def get_sentence_end_indices(self, text: str) -> List[int]:
        sents_l1 = [i for i, c in enumerate(text) if self.is_sentence_end_level1(c)]
        if len(sents_l1) == 0 and len(text) > self.use_level2_threshold:
            sents_l2 = [i for i, c in enumerate(text) if self.is_sentence_end_level2(c)]
            if len(sents_l2) == 0 and len(text) > self.use_level3_threshold:
                sents_l3 = [
                    i for i, c in enumerate(text) if self.is_sentence_end_level3(c)
                ]
                return sents_l3
            else:
                return sents_l2

        else:
            return sents_l1

    def reset(self):
        self.buffer = ""
