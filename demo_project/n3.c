#include <stdio.h>
#include "n1.h"  // n3 depends on n1
#include "n3.h"

void n3_func(void) {
    n1_func();
    printf("n3 function executed.\n");
}
