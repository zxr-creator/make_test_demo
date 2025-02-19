#include <stdio.h>
#include "n3.h"  // n13 depends on n3
#include "n13.h"

void n13_func(void) {
    n3_func();
    printf("n13 function executed.\n");
}
