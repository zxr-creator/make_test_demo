#include <stdio.h>
#include "n3.h"  // n5 depends on n3
#include "n5.h"

void n5_func(void) {
    n3_func();
    printf("n5 function executed.\n");
}
