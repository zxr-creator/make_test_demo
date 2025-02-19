#include <stdio.h>
#include "n10.h"  // n12 depends on n10
#include "n11.c"
#include "n16.c" 

void n12_func(void) {
    n10_func();
    n11_func();
    n16_func();
    printf("n12 function executed.\n");
}
