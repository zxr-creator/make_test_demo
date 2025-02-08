#include <stdio.h>
#include "n7.h"  // n10 depends on n7
#include "n9.c"
#include "n10.h"

void n10_func(void) {
    n7_func();
    n9_func();
    printf("n10 function executed.\n");
}
