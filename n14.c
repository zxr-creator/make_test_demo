#include <stdio.h>
#include "n13.h"  // n14 depends on n13

void n14_func(void) {
    n13_func();
    printf("n14 function executed.\n");
}
