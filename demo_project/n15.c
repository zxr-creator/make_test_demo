#include <stdio.h>
#include "n13.h"  // n15 depends on n13

void n15_func(void) {
    n13_func();
    printf("n15 function executed.\n");
}
