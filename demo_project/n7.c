#include <stdio.h>
#include "n5.h"  // n7 depends on n5
#include "n7.h"

void n7_func(void) {
    n5_func();
    printf("n7 function executed.\n");
}
