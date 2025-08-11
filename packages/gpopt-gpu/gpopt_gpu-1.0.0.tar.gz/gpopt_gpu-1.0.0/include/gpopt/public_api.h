#pragma once

#ifdef __cplusplus
extern "C" {
#endif

    // Pointer to the C++ evolution object
    typedef struct GpoptHandle GpoptHandle;

    GpoptHandle* gpopt_create();
    void gpopt_destroy(GpoptHandle* handle);
    void gpopt_run(GpoptHandle* handle);

#ifdef __cplusplus
}
#endif