void test(void) {
    f64 temp_f18;
    s32 temp_t0;
    f64 phi_f18;

    D_410260 = (u32) D_410250;
    D_410260 = (u32) D_410258;
    temp_t0 = D_410260;
    temp_f18 = (f64) temp_t0;
    phi_f18 = temp_f18;
    if (temp_t0 < 0) {
        phi_f18 = temp_f18 + 4294967296.0;
    }
    D_410258 = phi_f18;
    D_410250 = (f32) (u32) D_410260;
}
