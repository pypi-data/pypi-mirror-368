# cython: language_level=3
# distutils: language = c++

from libc.stdlib cimport malloc, free, realloc
import numpy as np
import time
from libc.stdint cimport uintptr_t
from cython.parallel cimport prange
from libcpp.unordered_map cimport unordered_map


cdef extern from *:
    """
    #define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
    """


cdef extern from *:
    """
    #include <unordered_map>
    #include <cstdint>

    using namespace std;

    unordered_map<int, uintptr_t>* create_unordered_map() {
        return new unordered_map<int, uintptr_t>();
    }

    unordered_map<int, int>* create_unordered_int_map() {
        return new unordered_map<int, int>();
    }

    void set_unordered_map(unordered_map<int, uintptr_t>* map, int key, uintptr_t value) {
        (*map)[key] = value;
    }

    void set_unordered_int_map(unordered_map<int, int>* map, int key, int value) {
        (*map)[key] = value;
    }

    uintptr_t get_unordered_map(unordered_map<int, uintptr_t>* map, int key) {
        auto it = map->find(key);
        if (it != map->end()) {
            return it->second;
        }
        return (uintptr_t)NULL;
    }

    int get_unordered_int_map(unordered_map<int, int>* map, int key) {
            auto it = map->find(key);
            if (it != map->end()) {
                return it->second;
            }
            return -1;
        }

    struct UnorderedMapIterator {
        unordered_map<int, uintptr_t>::iterator it;
        unordered_map<int, uintptr_t>::iterator end;
    };

    UnorderedMapIterator begin_unordered_map(unordered_map<int, uintptr_t>* map) {
        UnorderedMapIterator umi;
        umi.it = map->begin();
        umi.end = map->end();
        return umi;
    }

    bool is_end(UnorderedMapIterator* umi) {
        return umi->it == umi->end;
    }

    void get_current(UnorderedMapIterator* umi, int* key, uintptr_t* value) {
        if (umi->it != umi->end) {
            *key = umi->it->first;
            *value = umi->it->second;
        }
    }

    void move_next(UnorderedMapIterator* umi) {
        if (umi->it != umi->end) {
            ++umi->it;
        }
    }

    size_t get_unordered_map_size(unordered_map<int, uintptr_t>* map) {
        return map->size();
    }
    """
    ctypedef struct UnorderedMapIterator:
        pass
    unordered_map[int, uintptr_t]* create_unordered_map() nogil
    unordered_map[int, int] * create_unordered_int_map() nogil
    void set_unordered_map(unordered_map[int, uintptr_t]* map, int key, uintptr_t value) nogil
    void set_unordered_int_map(unordered_map[int, int] * map, int key, int value) nogil
    uintptr_t get_unordered_map(unordered_map[int, uintptr_t] * map, int key) nogil
    int get_unordered_int_map(unordered_map[int, int] * map, int key) nogil
    UnorderedMapIterator begin_unordered_map(unordered_map[int, uintptr_t] * map) nogil
    bint is_end(UnorderedMapIterator * umi) nogil
    void get_current(UnorderedMapIterator * umi, int * key, uintptr_t * value) nogil
    void move_next(UnorderedMapIterator * umi) nogil
    size_t get_unordered_map_size(unordered_map[int, uintptr_t] * map) nogil


cdef struct ACNodeStruct:
    unordered_map[int, uintptr_t]* children
    ACNodeStruct* fail
    int word_end
    int word_id
    int depth

cdef struct Result:
    int word_id
    int start
    int end

cdef struct ArrayInfo:
    int *data
    int rows
    int cols

cdef struct SequenceResult:
    Result* results
    int results_size

cdef struct Interval:
    int start
    int end

cdef class ACMatcherMemory:
    cdef ACNodeStruct root
    cdef dict encoder

    def __init__(self, cxs_encoder):
        self.root.children = create_unordered_map()
        if not self.root.children:
            raise MemoryError("Unable to allocate memory for unordered_map in root")
        self.root.fail = NULL
        self.root.word_end = -1
        self.root.word_id = -1
        self.root.depth = 0
        self.encoder = cxs_encoder
        self.construct_trie()

    def __dealloc__(self):
        self.free_tree(&self.root)

    cdef void free_tree(self, ACNodeStruct * node) nogil:
        cdef uintptr_t child_addr
        cdef ACNodeStruct * child
        cdef UnorderedMapIterator umi
        cdef int child_key

        if node is NULL:
            return

        umi = begin_unordered_map(node.children)
        while not is_end(&umi):
            get_current(&umi, &child_key, &child_addr)
            child = <ACNodeStruct *> child_addr
            self.free_tree(child)
            free(child)
            move_next(&umi)

        del node.children
        node.children = NULL

    cdef void add_child(self, ACNodeStruct * node, int value, int depth) nogil:
        cdef ACNodeStruct * new_node = <ACNodeStruct *> malloc(sizeof(ACNodeStruct))
        if not new_node:
            raise MemoryError("Unable to allocate memory for ACNodeStruct")
        new_node.children = create_unordered_map()
        if not new_node.children:
            raise MemoryError("Unable to allocate memory for unordered_map in new_node")
        new_node.fail = NULL
        new_node.word_end = -1
        new_node.word_id = -1
        new_node.depth = depth + 1
        set_unordered_map(node.children, value, <uintptr_t>new_node)

    cdef ACNodeStruct * find_child(self, ACNodeStruct * node, int value) nogil:
        cdef uintptr_t child_addr = get_unordered_map(node.children, value)
        if child_addr != <uintptr_t>NULL:
            return <ACNodeStruct *> child_addr
        else:
            return NULL

    def construct_trie(self):
        for key, value in self.encoder.items():
            self.add_word(key, value)
        self.build()

    cdef void add_word(self, tuple word, int word_id):
        cdef ACNodeStruct * node = &self.root
        cdef int num
        for num in word:
            if not self.find_child(node, num):
                self.add_child(node, num, node.depth)
            node = self.find_child(node, num)
        node.word_end = len(word)
        node.word_id = word_id

    cdef void build(self):
        cdef:
            ACNodeStruct * curr_node
            ACNodeStruct** queue
            int queue_capacity = 1000
            int queue_start = 0, queue_end = 0
            int child_key
            uintptr_t child_addr
            ACNodeStruct * child_node
            ACNodeStruct * fail_node
            UnorderedMapIterator umi

        queue = <ACNodeStruct**> malloc(sizeof(ACNodeStruct *) * queue_capacity)
        if not queue:
            raise MemoryError("Unable to allocate memory for queue")
        queue[queue_end] = &self.root
        queue_end += 1

        while queue_start < queue_end:
            curr_node = queue[queue_start]
            queue_start += 1

            umi = begin_unordered_map(curr_node.children)
            while not is_end(&umi):
                get_current(&umi, &child_key, &child_addr)
                child_node = <ACNodeStruct *> child_addr
                fail_node = curr_node.fail
                while fail_node and not self.find_child(fail_node, child_key):
                    fail_node = fail_node.fail

                if fail_node:
                    child_node.fail = self.find_child(fail_node, child_key)
                else:
                    child_node.fail = &self.root

                if queue_end >= queue_capacity:
                    queue_capacity *= 2
                    queue = <ACNodeStruct**> realloc(queue, sizeof(ACNodeStruct *) * queue_capacity)
                    if not queue:
                        raise MemoryError("Unable to reallocate memory for queue")

                queue[queue_end] = child_node
                queue_end += 1
                move_next(&umi)

        free(queue)

    cdef Result * parallel_search(self, int * data, int * mask, int num_rows, int num_cols, int mask_rows,
                                  int * results_size) nogil:
        cdef:
            Result * results = NULL
            int results_capacity = 1000
            unordered_map[int, uintptr_t] *result_set
            unordered_map[int, int] *inner_map_ptr
            uintptr_t * queue = NULL
            int queue_capacity = 1000
            int queue_start = 0, queue_end = 0
            uintptr_t node_ptr
            ACNodeStruct * node
            int i, j, k
            int num
            int offset, right_offset
            uintptr_t child_addr, cxs_umap_addr
            size_t size
            int cxs_start, cxs_end, map_res
            UnorderedMapIterator umi

        results = <Result *> malloc(sizeof(Result) * results_capacity)
        result_set = create_unordered_map()
        queue = <uintptr_t *> malloc(sizeof(uintptr_t) * queue_capacity * 3)

        queue[queue_end] = <uintptr_t> &self.root
        queue_end += 1
        queue[queue_end] = 0
        queue_end += 1
        queue[queue_end] = 0
        queue_end += 1
        results_size[0] = 0

        while queue_start < queue_end:
            node_ptr = queue[queue_start]
            queue_start += 1
            i = <int> queue[queue_start]
            queue_start += 1
            offset = <int> queue[queue_start]
            queue_start += 1
            node = <ACNodeStruct *> node_ptr

            if i >= num_rows:
                continue

            in_mask, skip_mask = False, False
            right_offset = 0
            for k in range(mask_rows):
                if mask[k * 2 + 1] < i:
                    continue
                if mask[k * 2] > i:
                    break
                if i >= mask[k * 2] and i <= mask[k * 2 + 1]:
                    in_mask = True
                    if i > mask[k * 2]:
                        skip_mask = True
                    right_offset = mask[k * 2 + 1] - mask[k * 2]
                    break


            for j in range(num_cols):
                num = data[i * num_cols + j]
                if skip_mask and j > 0:
                    continue
                child_addr = get_unordered_map(node.children, num)
                if child_addr != <uintptr_t> NULL:
                    child_node = <ACNodeStruct *> child_addr
                    temp = child_node
                    while temp and temp != &self.root:
                        if temp.word_end != -1:
                            if results_size[0] >= results_capacity:
                                results_capacity *= 2
                                results = <Result *> realloc(results, sizeof(Result) * results_capacity)
                            cxs_start = i - temp.word_end - offset + 1
                            cxs_end = i + right_offset + 1
                            cxs_umap_addr = get_unordered_map(result_set, cxs_end)
                            if cxs_umap_addr != <uintptr_t> NULL:
                                inner_map_ptr = <unordered_map[int, int] *> cxs_umap_addr
                                map_res = get_unordered_int_map(inner_map_ptr, temp.word_id)
                                if map_res < 0:
                                    set_unordered_int_map(inner_map_ptr, temp.word_id, results_size[0])
                                else:
                                    results[map_res].start = cxs_start
                                    temp = temp.fail
                                    continue
                            else:
                                inner_map_ptr = create_unordered_int_map()
                                set_unordered_map(result_set, cxs_end, <uintptr_t>inner_map_ptr)
                                set_unordered_int_map(inner_map_ptr, temp.word_id, results_size[0])
                            results[results_size[0]].word_id = temp.word_id
                            results[results_size[0]].start = cxs_start
                            results[results_size[0]].end = cxs_end
                            results_size[0] += 1
                        temp = temp.fail
                    if queue_end + 3 > queue_capacity:
                        queue_capacity *= 3
                        queue = <uintptr_t *> realloc(queue, sizeof(uintptr_t) * queue_capacity)
                    queue[queue_end] = <uintptr_t> child_node
                    queue_end += 1
                    if j > 0 and in_mask:
                        queue[queue_end] = i + right_offset + 1
                    else:
                        queue[queue_end] = i + 1
                    queue_end += 1
                    if j > 0 and in_mask:
                        queue[queue_end] = offset + right_offset
                    else:
                        queue[queue_end] = offset
                    queue_end += 1

            size = get_unordered_map_size(node.children)
            if node == &self.root or (get_unordered_map_size(node.children) == 0):
                if queue_end + 3 > queue_capacity:
                    queue_capacity *= 3
                    queue = <uintptr_t *> realloc(queue, sizeof(uintptr_t) * queue_capacity)
                if node == &self.root:
                    queue[queue_end] = <uintptr_t> &self.root
                    queue_end += 1
                    queue[queue_end] = i + 1
                    queue_end += 1
                    queue[queue_end] = 0
                    queue_end += 1
                elif node.fail:
                    queue[queue_end] = <uintptr_t> node.fail
                    queue_end += 1
                    queue[queue_end] = i
                    queue_end += 1
                    queue[queue_end] = offset
                    queue_end += 1

        free(queue)
        umi = begin_unordered_map(result_set)
        while not is_end(&umi):
            get_current(&umi, &cxs_end, &cxs_umap_addr)
            inner_map_ptr = <unordered_map[int, int] *> cxs_umap_addr
            del inner_map_ptr
            move_next(&umi)
        del result_set
        return results

    cpdef match(self, list sequences, list sequence_wwmasks, int num_workers):
        cdef:
            int num_sequences = len(sequences)
            list results = []
            int i, j
            int num_rows
            int num_cols
            int mask_rows
            Result * res
            SequenceResult * sequence_results = <SequenceResult *> malloc(sizeof(SequenceResult) * num_sequences)
            SequenceResult *thread_results
            ArrayInfo *arrays = <ArrayInfo *>malloc(num_sequences * sizeof(ArrayInfo))
            ArrayInfo *wwmask_array = <ArrayInfo *> malloc(sizeof(ArrayInfo) * num_sequences)
            int[:, :] arr, wwmasks
            int *data, *mask

        if arrays == NULL or sequence_results == NULL or wwmask_array == NULL:
            raise MemoryError("Unable to allocate memory")

        array_list, wwmask_list = [], []

        for i in range(num_sequences):
            arr = np.ascontiguousarray(sequences[i], dtype=np.int32)
            arrays[i].data = &arr[0, 0]
            arrays[i].rows = arr.shape[0]
            arrays[i].cols = arr.shape[1]
            array_list.append(arr)

            wwmasks = np.ascontiguousarray(sequence_wwmasks[i], dtype=np.int32)
            wwmask_array[i].data = &wwmasks[0, 0]
            wwmask_array[i].rows = wwmasks.shape[0]
            wwmask_array[i].cols = wwmasks.shape[1]
            wwmask_list.append(wwmasks)

        t0 = time.perf_counter()
        for i in prange(num_sequences, nogil=True, num_threads=num_workers):
            data = arrays[i].data
            num_rows = arrays[i].rows
            num_cols = arrays[i].cols
            mask = wwmask_array[i].data
            mask_rows = wwmask_array[i].rows
            sequence_results[i].results = self.parallel_search(data, mask, num_rows, num_cols, mask_rows,
                                                               &sequence_results[i].results_size)

        for i in range(num_sequences):
            thread_result = sequence_results[i]
            res_list = []
            for j in range(thread_result.results_size):
                res_list.append(
                    (thread_result.results[j].word_id, thread_result.results[j].start, thread_result.results[j].end))
            results.append(res_list)
            free(thread_result.results)

        free(sequence_results)
        free(arrays)
        free(wwmask_array)
        del wwmask_list
        del array_list
        return results
