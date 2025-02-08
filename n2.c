#include <stdio.h>
#include "n1.h"  // n2 depends on n1

void n2_func(void) {
    // Use functionality from n1
    n1_func();
    printf("n2 function executed.\n");
}
