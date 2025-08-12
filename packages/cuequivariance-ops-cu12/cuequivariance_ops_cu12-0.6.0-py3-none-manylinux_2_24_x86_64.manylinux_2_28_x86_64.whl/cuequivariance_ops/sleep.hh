/*
 * Copyright (c) 2025, NVIDIA CORPORATION. All rights reserved.
 *
 * This source code and/or documentation ("Licensed Deliverables") are
 * subject to NVIDIA intellectual property rights under U.S. and
 * international Copyright laws.
 */

#pragma once

#include <cstdint>

namespace kernelcatcher::sleep {

int run_sleep(float* seconds, int64_t* elapsed_ticks, void* stream);
int run_synchronize(float* elapsed_seconds, void* stream);

}  // namespace kernelcatcher::sleep
