from cxglearner.utils.multi_processor import multi_processor, mp_allocate_data


class Test(object):
    @multi_processor
    def run(self, proc_id, worker_num, a, b):
        a = mp_allocate_data(a, proc_id, worker_num)
        b = mp_allocate_data(b, proc_id, worker_num)
        c = [a[_] + b[_] for _ in range(len(a))]
        return c


@multi_processor
def func_run(proc_id, worker_num, a, b):
    a = mp_allocate_data(a, proc_id, worker_num)
    b = mp_allocate_data(b, proc_id, worker_num)
    c = [a[_] + b[_] for _ in range(len(a))]
    return c


if __name__ == '__main__':
    a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    b = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    # Class method
    t = Test()
    c1 = t.run(t, a, b, worker_num=7)
    print(c1)
    # Ordinary method
    c2 = func_run(a, b, worker_num=5)
    print(c2)
