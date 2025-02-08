#include <stdio.h>
#include "n10.h"  // n11 depends on n10

void n11_func(void) {
    n10_func();
    printf("n11 function executed.\n");
}
