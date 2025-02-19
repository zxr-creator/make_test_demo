#include <stdio.h>
#include "n15.c"  // or include "n15.h" if available
#include "n12.c" 

void n18_func(void) {
    n15_func();
    n12_func();
    printf("n18 function executed.\n");
}
