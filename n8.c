#include <stdio.h>
#include "n6.c"  // alternatively, if n6 has a header file, include that (e.g., "n6.h")

void n8_func(void) {
    n6_func();
    printf("n8 function executed.\n");
}
