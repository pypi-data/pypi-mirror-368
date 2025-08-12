# cython: language_level=3
# distutils: extra_compile_args = -fopenmp
# distutils: extra_link_args = -fopenmp

# define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

cimport numpy as cnp
import numpy as np
from .serial_graph import MDLGraphProxy, MDLSentence
from libc.stdlib cimport malloc, free, realloc
from libc.string cimport memcpy
from cython.parallel cimport prange
from libc.math cimport log as log_func
ctypedef cnp.int16_t int16_t

cdef extern:
    void atomic_add(int16_t* x, int y) nogil

cdef struct MDLSentenceStruct:
    int length
    int16_t *counter

cdef struct MDLPatternStruct:
    int *linked
    int linked_size
    int *starts
    int *ends

cdef class MDLGraph:
    cdef:
        MDLPatternStruct *patterns
        MDLSentenceStruct *sentences
        int num_patterns
        int num_sentences
        int current_sentences
        int *states
        bint need_log
        bint reduction
        bint allow_atomic
        float eps

    def __init__(self, int num_patterns, int num_sentences, pattern_length_in = None, initial_states_in = None,
                 log = True, reduction = True, allow_atomic = False, eps = 1e-3):
        cdef cnp.ndarray[int, mode = "c"] initial_states
        cdef cnp.ndarray[int, mode = "c"] pattern_length
        if initial_states_in is None: raise Exception("initial_states cannot be None")
        else: initial_states = initial_states_in
        if pattern_length_in is None: raise Exception("pattern_length_in cannot be None")
        else: pattern_length = pattern_length_in

        self.patterns = <MDLPatternStruct *>malloc(num_patterns * sizeof(MDLPatternStruct))
        self.sentences = <MDLSentenceStruct *>malloc(num_sentences * sizeof(MDLSentenceStruct))
        # Copy states
        self.states = <int *> malloc(num_patterns * sizeof(int))
        if not self.states:
            raise MemoryError("Could not allocate memory for states array.")
        memcpy(self.states, <int *> initial_states.data, num_patterns * sizeof(int))
        self.num_patterns = num_patterns
        self.num_sentences = num_sentences
        self.current_sentences = 0
        self.need_log = log
        self.reduction = reduction
        self.allow_atomic = allow_atomic
        self.eps = eps

        for i in range(num_patterns):
            self.patterns[i].linked = <int *>malloc(pattern_length[i] * sizeof(int))
            self.patterns[i].starts = <int *>malloc(pattern_length[i] * sizeof(int))
            self.patterns[i].ends = <int *>malloc(pattern_length[i] * sizeof(int))
            self.patterns[i].linked_size = 0

        for i in range(num_sentences):
            self.sentences[i].counter = NULL
            self.sentences[i].length = 0

    def __len__(self):
        return self.num_sentences

    @property
    def total_sentence_num(self):
        return self.current_sentences

    def __dealloc__(self):
        for i in range(self.num_patterns):
            free(self.patterns[i].linked)
            free(self.patterns[i].starts)
            free(self.patterns[i].ends)
        free(self.patterns)
        for i in range(self.num_sentences):
            if self.sentences[i].counter != NULL:
                free(self.sentences[i].counter)
        free(self.sentences)
        if self.states:
            free(self.states)


    cpdef void merge_single_sentence(self, int length, type_counter=None):
        cdef cnp.ndarray[int16_t, mode = "c"] counter = type_counter

        self.current_sentences += 1
        self.sentences[self.current_sentences - 1].length = length
        self.sentences[self.current_sentences - 1].counter = <int16_t *> malloc(length * sizeof(int16_t))

        for i in range(length):
            self.sentences[self.current_sentences - 1].counter[i] = counter[i]

    cpdef void merge_pattern(self, int index, int merge_length, type_linked=None, type_interval=None):
        cdef cnp.ndarray[int, mode = "c"] linked = type_linked
        cdef int[:, :] interval = type_interval

        for i in range(merge_length):
            start = interval[i, 0]
            end = interval[i, 1]
            self.patterns[index].linked_size += 1
            self.patterns[index].linked[self.patterns[index].linked_size - 1] = linked[i]
            self.patterns[index].starts[self.patterns[index].linked_size - 1] = start
            self.patterns[index].ends[self.patterns[index].linked_size - 1] = end


    cpdef void add_sentence(self, int length, typed_pattern_intervals=None, int base=0):
        cdef int[:, :] pattern_intervals

        self.num_sentences += 1
        self.sentences = <MDLSentenceStruct *>realloc(self.sentences, self.num_sentences * sizeof(MDLSentenceStruct))
        self.sentences[self.num_sentences - 1].length = length
        self.sentences[self.num_sentences - 1].counter = <int16_t *>malloc(length * sizeof(int16_t))
        for i in range(length):
            self.sentences[self.num_sentences - 1].counter[i] = 0

        cdef int pattern_index, start, end
        if typed_pattern_intervals is not None:
            pattern_intervals = typed_pattern_intervals
        else:
            return

        for i in range(pattern_intervals.shape[0]):
            pattern_index = pattern_intervals[i, 0]
            start = pattern_intervals[i, 1]
            end = pattern_intervals[i, 2]
            self.patterns[pattern_index].linked_size += 1
            self.patterns[pattern_index].linked = <int *>realloc(self.patterns[pattern_index].linked, self.patterns[pattern_index].linked_size * sizeof(int))
            self.patterns[pattern_index].starts = <int *>realloc(self.patterns[pattern_index].starts, self.patterns[pattern_index].linked_size * sizeof(int))
            self.patterns[pattern_index].ends = <int *>realloc(self.patterns[pattern_index].ends, self.patterns[pattern_index].linked_size * sizeof(int))
            self.patterns[pattern_index].linked[self.patterns[pattern_index].linked_size - 1] = self.num_sentences - 1 + base
            self.patterns[pattern_index].starts[self.patterns[pattern_index].linked_size - 1] = start
            self.patterns[pattern_index].ends[self.patterns[pattern_index].linked_size - 1] = end

            if self.states[pattern_index]:
                for j in range(start, end):
                    self.sentences[self.num_sentences - 1].counter[j] += 1

    cdef void process_interval(self, MDLSentenceStruct* sentence, int start, int end, int value) nogil:
        if self.allow_atomic:
            for j in range(start, end):
                atomic_add(&sentence.counter[j], value)
        else:
            for j in range(start, end):
                sentence.counter[j] += value

    cdef void modify_pattern(self, int index, int pos, int value) nogil:
        cdef int idx, start, end
        idx = self.patterns[index].linked[pos]
        start = self.patterns[index].starts[pos]
        end = self.patterns[index].ends[pos]
        self.process_interval(&self.sentences[idx], start, end, value)

    cdef void add_pattern(self, int index) nogil:
        cdef int i
        if self.allow_atomic:
            for i in prange(self.patterns[index].linked_size, nogil=True):
                self.modify_pattern(index, i, 1)
        else:
            for i in range(self.patterns[index].linked_size):
                self.modify_pattern(index, i, 1)

    cdef void remove_pattern(self, int index) nogil:
        cdef int i, idx, start, end
        if self.allow_atomic:
            for i in prange(self.patterns[index].linked_size, nogil=True):
                self.modify_pattern(index, i, -1)
        else:
            for i in range(self.patterns[index].linked_size):
                self.modify_pattern(index, i, -1)

    cpdef int diff_update(self, states):
        cdef cnp.ndarray[int, mode = "c"] new_states = states
        cdef int idx
        cdef int num_elements
        cdef int delta = 0
        cdef int *temp_states

        num_elements = new_states.size
        if num_elements != self.num_patterns:
            raise ValueError("Size of new states array does not match the number of patterns.")
        temp_states = <int *> malloc(self.num_patterns * sizeof(int))
        if not temp_states:
            raise MemoryError("Could not allocate memory for new states array.")
        memcpy(temp_states, <int *> new_states.data, self.num_patterns * sizeof(int))

        if self.allow_atomic:
            for idx in prange(self.num_patterns, nogil=True):
                if self.states[idx] != temp_states[idx]:
                    if temp_states[idx]:
                        self.add_pattern(idx)
                    else:
                        self.remove_pattern(idx)
                    delta += 1
        else:
            for idx in range(self.num_patterns):
                if self.states[idx] != temp_states[idx]:
                    if temp_states[idx]:
                        self.add_pattern(idx)
                    else:
                        self.remove_pattern(idx)
                    delta += 1

        if self.states:
            free(self.states)

        self.states = temp_states
        return delta

    @property
    def avg_cover(self):
        cdef int i, j, count = 0
        cdef float sum_cover = 0.0, local_sum =0.0
        for i in prange(self.num_sentences, nogil=True, schedule='guided'):
            local_sum = 0.0
            count = 0
            for j in range(self.sentences[i].length):
                if self.sentences[i].counter[j] > 0:
                    count += 1
            local_sum += (count / float(self.sentences[i].length))
            if self.need_log:
                local_sum = log_func(local_sum + self.eps)
            sum_cover += local_sum
        if self.reduction:
            return sum_cover / self.num_sentences
        else:
            return sum_cover

    @property
    def avg_overlap(self):
        cdef int i, j, count = 0
        cdef float sum_overlap = 0.0, local_sum = 0.0
        for i in prange(self.num_sentences, nogil=True, schedule='guided'):
            local_sum = 0.0
            count = 0
            for j in range(self.sentences[i].length):
                if self.sentences[i].counter[j] > 1:
                    count += 1
            local_sum += (count / float(self.sentences[i].length))
            if self.need_log:
                local_sum = log_func(local_sum + self.eps)
            sum_overlap += local_sum
        if self.reduction:
            return sum_overlap / self.num_sentences
        else:
            return sum_overlap

    @property
    def avg_metrics(self):
        cdef int i, j, count_cover = 0, count_overlap = 0
        cdef float sum_overlap = 0.0, sum_cover = 0.0, local_sum_cover = 0.0, local_sum_overlap = 0.0
        for i in prange(self.num_sentences, nogil=True, schedule='guided'):
            local_sum_cover = 0.0
            local_sum_overlap = 0.0
            count_cover = 0
            count_overlap = 0
            for j in range(self.sentences[i].length):
                if self.sentences[i].counter[j] > 1:
                    count_overlap += 1
                if self.sentences[i].counter[j] > 0:
                    count_cover += 1
            local_sum_overlap += (count_overlap / float(self.sentences[i].length))
            local_sum_cover += (count_cover / float(self.sentences[i].length))
            if self.need_log:
                local_sum_cover = log_func(local_sum_cover + self.eps)
                local_sum_overlap = log_func(local_sum_overlap + self.eps)
            sum_overlap += local_sum_overlap
            sum_cover += local_sum_cover
        if self.reduction:
            return sum_cover / self.num_sentences, sum_overlap / self.num_sentences
        else:
            return sum_cover, sum_overlap

    def to_proxy(self):
        proxy_obj = MDLGraphProxy(self.num_patterns, np.array([self.states[i] for i in range(self.num_patterns)], dtype=np.int32))
        for pattern_index in range(self.num_patterns):
            pattern = self.patterns[pattern_index]
            for linked_index in range(pattern.linked_size):
                idx = pattern.linked[linked_index]
                start = pattern.starts[linked_index]
                end = pattern.ends[linked_index]
                proxy_obj.patterns[pattern_index].link_sentence(idx, (start, end))

        for sentence_index in range(self.num_sentences):
            sentence = self.sentences[sentence_index]
            sentence_adder = MDLSentence(sentence.length)
            for i in range(sentence.length):
                sentence_adder.counter[i] = sentence.counter[i]
            proxy_obj.sentences.append(sentence_adder)
        return proxy_obj

    @staticmethod
    def from_proxy(proxy_obj: MDLGraphProxy, log: bool = True, reduction: bool = True, allow_atomic: bool = False,
                   eps: bool = 1e-3) -> MDLGraph:
        initial_states = np.array(proxy_obj.states, dtype=np.int32)
        pattern_length = np.zeros(len(proxy_obj.patterns), dtype=np.int32)
        for pattern_index, pattern in enumerate(proxy_obj.patterns):
            pattern_length[pattern_index] = len(pattern.linked)
        cython_obj = MDLGraph(len(proxy_obj.patterns), len(proxy_obj.sentences), pattern_length, initial_states,
                              log=log, reduction=reduction, allow_atomic=allow_atomic, eps=eps)

        for sentence in proxy_obj.sentences:
            cython_obj.merge_single_sentence(sentence.length, sentence.counter)

        for pattern_index, pattern in enumerate(proxy_obj.patterns):
            if len(pattern.linked) == 0: continue
            merge_length = len(pattern.linked)
            links = np.array(pattern.linked, dtype=np.int32)
            intervals = np.array(pattern.intervals, dtype=np.int32)
            cython_obj.merge_pattern(pattern_index, len(links), links, intervals)

        return cython_obj
