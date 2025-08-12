import numpy as np
from typing import List, Tuple
try:  # Avoid cythonize error
    from .mdl_ds import MDLGraph
except:
    MDLGraph = None


class MDLSentence:
    def __init__(self, length: int):
        self.length = length
        self.counter = np.zeros(length, dtype=np.int16)

    def process_interval(self, intervals: List[List[int]], value: int = 1):
        for start, end in intervals:
            self.counter[start:end] += value

    def insert_pattern(self, intervals: List[List[int]]):
        self.process_interval(intervals)

    def remove_pattern(self, intervals: List[List[int]]):
        self.process_interval(intervals, value=-1)


class MDLPattern:
    def __init__(self):
        self.linked = []
        self.intervals = []

    def link_sentence(self, sentence_index: int, interval: Tuple[int, int], base: int = 0):
        self.linked.append(sentence_index + base)
        self.intervals.append(interval)


class MDLGraphProxy:
    def __init__(self, num_patterns: int, initial_states: np.ndarray):
        self.patterns = []
        self.sentences = []
        self.states = initial_states.astype(np.bool_).tolist()
        self.initialize_patterns(num_patterns)

    def initialize_patterns(self, num_patterns: int):
        for _ in range(num_patterns):
            self.patterns.append(MDLPattern())

    def add_sentence(self, length: int, patterns: np.array, base: int = 0):
        sentence = MDLSentence(length)
        for pattern_index, start, end in patterns:
            self.patterns[pattern_index].link_sentence(len(self.sentences), (start, end), base)
            if self.states[pattern_index]:
                sentence.insert_pattern([[start, end]])
        self.sentences.append(sentence)

    def add_pattern(self, index: int):
        pattern = self.patterns[index]
        for idx, interval in zip(pattern.linked, pattern.intervals):
            self.sentences[idx].insert_pattern([interval])

    def remove_pattern(self, index: int):
        pattern = self.patterns[index]
        for idx, interval in zip(pattern.linked, pattern.intervals):
            self.sentences[idx].remove_pattern([interval])

    def to_cython(self):
        return MDLGraph.from_proxy(self)

    @staticmethod
    def from_cython(cython_obj):
        return cython_obj.to_proxy()