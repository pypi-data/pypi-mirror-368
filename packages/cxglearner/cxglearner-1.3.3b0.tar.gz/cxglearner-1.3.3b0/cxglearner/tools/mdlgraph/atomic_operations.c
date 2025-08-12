#include <stdint.h>
#include <omp.h>

void atomic_add(int16_t* x, int y) {
    #pragma omp atomic
    *x += y;
}
