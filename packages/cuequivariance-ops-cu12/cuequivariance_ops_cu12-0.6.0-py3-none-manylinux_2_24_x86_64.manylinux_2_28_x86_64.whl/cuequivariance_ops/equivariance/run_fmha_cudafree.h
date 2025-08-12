/*
 * SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: LicenseRef-NvidiaProprietary
 *
 * NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
 * property and proprietary rights in and to this material, related
 * documentation and any modifications thereto. Any use, reproduction,
 * disclosure or distribution of this material and related documentation
 * without an express license agreement from NVIDIA CORPORATION or
 * its affiliates is strictly prohibited.
 */
#ifndef CUDNN_FMHA_RUN_FMHA_CUDAFREE_H
#define CUDNN_FMHA_RUN_FMHA_CUDAFREE_H

#include <cstdint>  // for uint32_t

namespace cudnn_fmha {
using DType = void;

enum class Datatype : uint32_t {
  kFloat32  = 0,
  kFloat64  = 1,
  kFloat16  = 2,
  kBFloat16 = 3,
  kInt32    = 4,
  kInt64    = 5
};

__attribute__((visibility("default"))) void run_fmha_for_dtype(
  Datatype dtype,
  DType* q_ptr,              // [B, N, H, S_qo, D]
  DType* k_ptr,              // [B, N, H, S_kv, D]
  DType* v_ptr,              // [B, N, H, S_kv, D]
  DType* o_ptr,              // [B, N, H, S_qo, D] output
  bool* mask_bias_ptr,       // [B, N, 1, 1, S_kv]
  float* triangle_bias_ptr,  // [B, 1, H, S_qo, S_kv]
  float* softmax_lse_ptr,    // [B, N, H, S_qo, 1] output
  float* softmax_max_ptr,    // [B, N, H, S_qo, 1] output
  const uint32_t B,
  const uint32_t I,
  const uint32_t H,
  const uint32_t S_qo,
  const uint32_t S_kv,
  const uint32_t D,
  const float bmm_scale,
  bool use_tf32,
  void* stream = nullptr);

__attribute__((visibility("default"))) void run_fmha_bwd_for_dtype(
  Datatype dtype,
  DType* do_ptr,              // [B, N, H, S_qo, D]
  DType* o_ptr,               // [B, N, H, S_qo, D]
  float* softmax_lse_ptr,     // [B, N, H, S_qo, 1]
  DType* q_ptr,               // [B, N, H, S_qo, D]
  DType* k_ptr,               // [B, N, H, S_kv, D]
  DType* v_ptr,               // [B, N, H, S_kv, D]
  bool* mask_bias_ptr,        // [B, N, 1, 1, S_kv]
  float* triangle_bias_ptr,   // [B, 1, H, S_qo, S_kv]
  DType* dq_ptr,              // [B, N, H, S_qo, D] output
  DType* dk_ptr,              // [B, N, H, S_kv, D] output
  DType* dv_ptr,              // [B, N, H, S_kv, D] output
  float* triangle_dbias_ptr,  // [B, 1, H, S_qo, S_kv] output
  float* do_o_dot_ptr,        // [B, N, H, S_qo, 1] worspace
  float* dq_fp32_buf_ptr,     // [B, N, H, S_qo, D] workspace
  const uint32_t B,
  const uint32_t I,
  const uint32_t H,
  const uint32_t S_qo,
  const uint32_t S_kv,
  const uint32_t D,
  const float bmm_scale,
  bool use_tf32,
  void* stream);

}  // namespace cudnn_fmha

#endif  // CUDNN_FMHA_RUN_FMHA_CUDAFREE_H
