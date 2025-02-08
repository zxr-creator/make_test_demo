#include <stdio.h>
#include "n5.h"  // n6 depends on n5

void n6_func(void) {
    n5_func();
    printf("n6 function executed.\n");
}
