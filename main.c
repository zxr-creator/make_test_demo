#include <stdio.h>

// Forward declarations. In a real project, include the appropriate headers.
void n18_func(void);

int main(void) {
    printf("Starting the build sequence:\n\n");
    n2_func();
    n4_func();
    n8_func();
    n9_func();
    n11_func();
    n12_func();
    n16_func();
    n17_func();
    n18_func();

    printf("\nBuild sequence complete.\n");
    return 0;
}
