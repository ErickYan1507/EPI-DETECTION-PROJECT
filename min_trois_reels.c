#include <stdio.h>

int main()
{
    float a, b, c, min;

    printf("Entrez trois nombres reels : ");
    scanf("%f %f %f", &a, &b, &c);

    min = a;
    if (b < min)
        min = b;
    if (c < min)
        min = c;

    printf("Le minimum est : %.2f\n", min);

    return 0;
}
