void test(s32 x, short *y, s32 z, char *r, short *s, int *t, long *u) {
    int *phi_s0;

    phi_s0 = NULL;
loop_1:
    phi_s0 = foo(phi_s0, y, t);
    goto loop_1;
}
