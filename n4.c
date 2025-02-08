#include <stdio.h>
#include "n3.h"  // n4 depends on n3

void n4_func(void) {
    n3_func();
    printf("n4 function executed.\n");
}
