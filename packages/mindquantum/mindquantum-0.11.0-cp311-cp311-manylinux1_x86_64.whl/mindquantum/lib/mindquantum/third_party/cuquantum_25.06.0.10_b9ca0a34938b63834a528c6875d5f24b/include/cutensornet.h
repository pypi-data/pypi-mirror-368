/*
 * Copyright 2021-2025 NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
 *
 * NOTICE TO LICENSEE:
 *
 * This source code and/or documentation ("Licensed Deliverables") are
 * subject to NVIDIA intellectual property rights under U.S. and
 * international Copyright laws.
 *
 * These Licensed Deliverables contained herein is PROPRIETARY and
 * CONFIDENTIAL to NVIDIA and is being provided under the terms and
 * conditions of a form of NVIDIA software license agreement by and
 * between NVIDIA and Licensee ("License Agreement") or electronically
 * accepted by Licensee.  Notwithstanding any terms or conditions to
 * the contrary in the License Agreement, reproduction or disclosure
 * of the Licensed Deliverables to any third party without the express
 * written consent of NVIDIA is prohibited.
 *
 * NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
 * LICENSE AGREEMENT, NVIDIA MAKES NO REPRESENTATION ABOUT THE
 * SUITABILITY OF THESE LICENSED DELIVERABLES FOR ANY PURPOSE.  IT IS
 * PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND.
 * NVIDIA DISCLAIMS ALL WARRANTIES WITH REGARD TO THESE LICENSED
 * DELIVERABLES, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY,
 * NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
 * NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
 * LICENSE AGREEMENT, IN NO EVENT SHALL NVIDIA BE LIABLE FOR ANY
 * SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, OR ANY
 * DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
 * WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
 * ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
 * OF THESE LICENSED DELIVERABLES.
 *
 * U.S. Government End Users.  These Licensed Deliverables are a
 * "commercial item" as that term is defined at 48 C.F.R. 2.101 (OCT
 * 1995), consisting of "commercial computer software" and "commercial
 * computer software documentation" as such terms are used in 48
 * C.F.R. 12.212 (SEPT 1995) and is provided to the U.S. Government
 * only as a commercial end item.  Consistent with 48 C.F.R.12.212 and
 * 48 C.F.R. 227.7202-1 through 227.7202-4 (JUNE 1995), all
 * U.S. Government End Users acquire the Licensed Deliverables with
 * only those rights set forth herein.
 *
 * Any use of the Licensed Deliverables in individual and commercial
 * software must include, in the user documentation and internal
 * comments to the code, the above Disclaimer and U.S. Government End
 * Users Notice.
 * </blockquote>}
 */

/**
 * @file
 * @brief This file contains all public function declarations of the cuTensorNet
 * library.
 */
#pragma once

#define CUTENSORNET_MAJOR 2 //!< cuTensorNet major version.
#define CUTENSORNET_MINOR 8 //!< cuTensorNet minor version.
#define CUTENSORNET_PATCH 0 //!< cuTensorNet patch version.
#define CUTENSORNET_VERSION (CUTENSORNET_MAJOR * 10000 + CUTENSORNET_MINOR * 100 + CUTENSORNET_PATCH)

#include <cutensornet/types.h>
#include <cutensornet/typesDistributed.h>

#if defined(__cplusplus)
#include <cstdint>
#include <cstdio>

extern "C" {
#else
#include <stdint.h>
#include <stdio.h>

#endif /* __cplusplus */

#if defined(__GNUC__)
#define CUTENSORNET_DEPRECATED(new_func) __attribute__((deprecated("please use " #new_func " instead")))
#else
#define CUTENSORNET_DEPRECATED(new_func)
#endif

#if defined(__GNUC__)
#define CUTENSORNET_EXPERIMENTAL(func) __attribute__((warning("" #func " is an experimental API and subject to future change")))
#else
#define CUTENSORNET_EXPERIMENTAL(func)
#endif

/**
 * \brief Initializes the cuTensorNet library
 *
 * \details The device associated with a particular cuTensorNet handle is assumed to remain
 * unchanged after the cutensornetCreate() call. In order for the cuTensorNet library to
 * use a different device, the application must set the new device to be used by
 * calling cudaSetDevice() and then create another cuTensorNet handle, which will
 * be associated with the new device, by calling cutensornetCreate().
 *
 * \param[out] handle Pointer to ::cutensornetHandle_t
 *
 * \returns ::CUTENSORNET_STATUS_SUCCESS on success and an error code otherwise
 * \remarks blocking, no reentrant, and thread-safe
 */
cutensornetStatus_t cutensornetCreate(cutensornetHandle_t *handle);

/**
 * \brief Destroys the cuTensorNet library handle
 *
 * \details This function releases resources used by the cuTensorNet library handle. This function is the last call with a particular handle to the cuTensorNet library.
 * Calling any cuTensorNet function which uses ::cutensornetHandle_t after cutensornetDestroy() will return an error.
 *
 * \param[in,out] handle Opaque handle holding cuTensorNet's library context.
 */
cutensornetStatus_t cutensornetDestroy(cutensornetHandle_t handle);

/**
 * \mainpage cuTensorNet: A high-level CUDA library that is dedicated to operations on tensor networks (i.e., a collection of tensors)
 */

/**
 * \brief Initializes a ::cutensornetNetworkDescriptor_t, describing the connectivity (i.e., network topology) between the tensors.
 *
 * Note that this function allocates data on the heap; hence, it is critical that cutensornetDestroyNetworkDescriptor() is called once \p networkDesc is no longer required.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] numInputs Number of input tensors.
 * \param[in] numModesIn Array of size \p numInputs; ``numModesIn[i]`` denotes the number of modes available in the i-th tensor.
 * \param[in] extentsIn Array of size \p numInputs; ``extentsIn[i]`` has ``numModesIn[i]`` many entries with ``extentsIn[i][j]`` (``j`` < ``numModesIn[i]``) corresponding to the extent of the j-th mode of tensor ``i``.
 * \param[in] stridesIn Array of size \p numInputs; ``stridesIn[i]`` has ``numModesIn[i]`` many entries with ``stridesIn[i][j]`` (``j`` < ``numModesIn[i]``) corresponding to the linearized offset -- in physical memory -- between two logically-neighboring elements w.r.t the j-th mode of tensor ``i``.
 * \param[in] modesIn Array of size \p numInputs; ``modesIn[i]`` has ``numModesIn[i]`` many entries -- each entry corresponds to a mode. Each mode that does not appear in the input tensor is implicitly contracted.
 * \param[in] qualifiersIn Array of size \p numInputs; ``qualifiersIn[i]`` denotes the qualifiers of i-th input tensor. Refer to ::cutensornetTensorQualifiers_t
 * \param[in] numModesOut number of modes of the output tensor. On entry, if this value is ``-1`` and the output modes are not provided, the network will infer the output modes. If this value is ``0``, the network is force reduced.
 * \param[in] extentsOut Array of size \p numModesOut; ``extentsOut[j]`` (``j`` < ``numModesOut``) corresponding to the extent of the j-th mode of the output tensor.
 * \param[in] stridesOut Array of size \p numModesOut; ``stridesOut[j]`` (``j`` < ``numModesOut``) corresponding to the linearized offset -- in physical memory -- between two logically-neighboring elements w.r.t the j-th mode of the output tensor.
 * \param[in] modesOut Array of size \p numModesOut; ``modesOut[j]`` denotes the j-th mode of the output tensor.
 * output tensor.
 * \param[in] dataType Denotes the data type for all input an output tensors.
 * \param[in] computeType Denotes the compute type used throughout the computation.
 * \param[out] networkDesc Pointer to a ::cutensornetNetworkDescriptor_t.
 *
 * \note If \p stridesIn (\p stridesOut) is set to 0 (\p NULL), it means the input tensors (output tensor) are in the Fortran (column-major) layout.
 * \note \p numModesOut can be set to ``-1`` for cuTensorNet to infer the output modes based on the input modes, or to ``0`` to perform a full reduction.
 * \note If \p qualifiersIn is set to 0 (\p NULL), cuTensorNet will use the defaults in ::cutensornetTensorQualifiers_t .
 *
 * Supported data-type combinations are:
 *
 * \verbatim embed:rst:leading-asterisk
 * +-------------+----------------------------+-------------+
 * |  Data type  |       Compute type         | Tensor Core |
 * +=============+============================+=============+
 * | CUDA_R_16F  | CUTENSORNET_COMPUTE_32F    | Volta+      |
 * +-------------+----------------------------+-------------+
 * | CUDA_R_16BF | CUTENSORNET_COMPUTE_32F    | Ampere+     |
 * +-------------+----------------------------+-------------+
 * | CUDA_R_32F  | CUTENSORNET_COMPUTE_32F    | No          |
 * +-------------+----------------------------+-------------+
 * | CUDA_R_32F  | CUTENSORNET_COMPUTE_TF32   | Ampere+     |
 * +-------------+----------------------------+-------------+
 * | CUDA_R_32F  | CUTENSORNET_COMPUTE_3XTF32 | Ampere+     |
 * +-------------+----------------------------+-------------+
 * | CUDA_R_32F  | CUTENSORNET_COMPUTE_16BF   | Ampere+     |
 * +-------------+----------------------------+-------------+
 * | CUDA_R_32F  | CUTENSORNET_COMPUTE_16F    | Volta+      |
 * +-------------+----------------------------+-------------+
 * | CUDA_R_64F  | CUTENSORNET_COMPUTE_64F    | Ampere+     |
 * +-------------+----------------------------+-------------+
 * | CUDA_R_64F  | CUTENSORNET_COMPUTE_32F    | No          |
 * +-------------+----------------------------+-------------+
 * | CUDA_C_32F  | CUTENSORNET_COMPUTE_32F    | No          |
 * +-------------+----------------------------+-------------+
 * | CUDA_C_32F  | CUTENSORNET_COMPUTE_TF32   | Ampere+     |
 * +-------------+----------------------------+-------------+
 * | CUDA_C_32F  | CUTENSORNET_COMPUTE_3XTF32 | Ampere+     |
 * +-------------+----------------------------+-------------+
 * | CUDA_C_64F  | CUTENSORNET_COMPUTE_64F    | Ampere+     |
 * +-------------+----------------------------+-------------+
 * | CUDA_C_64F  | CUTENSORNET_COMPUTE_32F    | No          |
 * +-------------+----------------------------+-------------+
 * \endverbatim
 */
cutensornetStatus_t cutensornetCreateNetworkDescriptor(const cutensornetHandle_t handle,
                                                       int32_t numInputs,
                                                       const int32_t numModesIn[],
                                                       const int64_t *const extentsIn[],
                                                       const int64_t *const stridesIn[],
                                                       const int32_t *const modesIn[],
                                                       const cutensornetTensorQualifiers_t qualifiersIn[],
                                                       int32_t numModesOut,
                                                       const int64_t extentsOut[],
                                                       const int64_t stridesOut[],
                                                       const int32_t modesOut[],
                                                       cudaDataType_t dataType,
                                                       cutensornetComputeType_t computeType,
                                                       cutensornetNetworkDescriptor_t *networkDesc);

/**
 * \brief Frees all the memory associated with the network descriptor.
 *
 * \param[in,out] networkDesc Opaque handle to a tensor network descriptor.
 */
cutensornetStatus_t cutensornetDestroyNetworkDescriptor(cutensornetNetworkDescriptor_t networkDesc);

/**
 * \brief Gets attributes of networkDescriptor.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] networkDesc Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[out] buffer On return, this buffer (of size \p sizeInBytes) holds the value that corresponds to \p attr within \p networkDesc.
 * \param[in] sizeInBytes Size of \p buffer (in bytes).
 */
cutensornetStatus_t cutensornetNetworkGetAttribute(const cutensornetHandle_t handle,
                                                   const cutensornetNetworkDescriptor_t networkDesc,
                                                   cutensornetNetworkAttributes_t attr,
                                                   void *buffer,
                                                   size_t sizeInBytes);

/**
 * \brief Sets attributes of networkDescriptor.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in,out] networkDesc Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[in] buffer This buffer (of size \p sizeInBytes) determines the value to which \p attr will be set.
 * \param[in] sizeInBytes Size of \p buffer (in bytes).
 */
cutensornetStatus_t cutensornetNetworkSetAttribute(const cutensornetHandle_t handle,
                                                   cutensornetNetworkDescriptor_t networkDesc,
                                                   cutensornetNetworkAttributes_t attr,
                                                   const void *buffer,
                                                   size_t sizeInBytes);

/**
 * \brief DEPRECATED: Gets the number of output modes, data size, modes, extents, and strides of the output tensor.
 *
 * If all information regarding the output tensor is needed by the user, this function should be called twice
 * (the first time to retrieve \p numModes for allocating memory, and the second to retrieve \p modesLabels, \p extents, and \p strides).
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] networkDesc Pointer to a ::cutensornetNetworkDescriptor_t.
 * \param[out] numModes on return, holds the number of modes of the output tensor. Cannot be null.
 * \param[out] dataSize if not null on return, holds the size (in bytes) of the memory needed for the output tensor. Optionally, can be null.
 * \param[out] modeLabels if not null on return, holds the mode labels of the output tensor. Optionally, can be null.
 * \param[out] extents if not null on return, holds the extents of the output tensor. Optionally, can be null.
 * \param[out] strides if not null on return, holds the strides of the output tensor. Optionally, can be null.
 */
CUTENSORNET_DEPRECATED(cutensornetGetOutputTensorDescriptor)
cutensornetStatus_t cutensornetGetOutputTensorDetails(const cutensornetHandle_t handle,
                                                      const cutensornetNetworkDescriptor_t networkDesc,
                                                      int32_t *numModes,
                                                      size_t *dataSize,
                                                      int32_t *modeLabels,
                                                      int64_t *extents,
                                                      int64_t *strides);

/**
 * \brief Creates a ::cutensornetTensorDescriptor_t representing the output tensor of the network.
 *
 * This function will create a descriptor pointed to by \p outputTensorDesc. The user is responsible for calling
 * ::cutensornetDestroyTensorDescriptor to destroy the descriptor.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] networkDesc Pointer to a ::cutensornetNetworkDescriptor_t.
 * \param[out] outputTensorDesc an opaque ::cutensornetTensorDescriptor_t struct. Cannot be null. On return, a new ::cutensornetTensorDescriptor_t holds the meta-data of the \p networkDesc output tensor.
 */
cutensornetStatus_t cutensornetGetOutputTensorDescriptor(const cutensornetHandle_t handle,
                                                         const cutensornetNetworkDescriptor_t networkDesc,
                                                         cutensornetTensorDescriptor_t *outputTensorDesc);

/**
 * \brief Gets the number of output modes, data size, mode labels, extents, and strides of a tensor.
 *
 * If all information regarding the tensor is needed by the user, this function should be called twice
 * (the first time to retrieve \p numModes for allocating memory, and the second to retrieve \p modeLabels, \p extents, and \p strides).
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] tensorDesc Opaque handle to a tensor descriptor.
 * \param[out] numModes On return, holds the number of modes of the tensor. Cannot be null.
 * \param[out] dataSize If not null on return, holds the size (in bytes) of the memory needed for the tensor. Optionally, can be null.
 * \param[out] modeLabels If not null on return, holds the mode labels of the tensor. Optionally, can be null.
 * \param[out] extents If not null on return, holds the extents of the tensor. Optionally, can be null.
 * \param[out] strides If not null on return, holds the strides of the tensor. Optionally, can be null.
 */
cutensornetStatus_t cutensornetGetTensorDetails(const cutensornetHandle_t handle,
                                                const cutensornetTensorDescriptor_t tensorDesc,
                                                int32_t *numModes,
                                                size_t *dataSize,
                                                int32_t *modeLabels,
                                                int64_t *extents,
                                                int64_t *strides);

/**
 * \brief Creates a workspace descriptor that holds information about the user provided memory buffer.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[out] workDesc Pointer to the opaque workspace descriptor.
 */
cutensornetStatus_t cutensornetCreateWorkspaceDescriptor(const cutensornetHandle_t handle,
                                                         cutensornetWorkspaceDescriptor_t *workDesc);

/**
 * \brief DEPRECATED: Computes the workspace size needed to contract the input tensor network using the provided contraction path.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] networkDesc Describes the tensor network (i.e., its tensors and their connectivity).
 * \param[in] optimizerInfo Opaque structure.
 * \param[out] workDesc The workspace descriptor in which the information is collected.
 */
CUTENSORNET_DEPRECATED(cutensornetWorkspaceComputeContractionSizes)
cutensornetStatus_t cutensornetWorkspaceComputeSizes(const cutensornetHandle_t handle,
                                                     const cutensornetNetworkDescriptor_t networkDesc,
                                                     const cutensornetContractionOptimizerInfo_t optimizerInfo,
                                                     cutensornetWorkspaceDescriptor_t workDesc);

/**
 * \brief Computes the workspace size needed to contract the tensor network using the provided contraction path.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] networkDesc Describes the tensor network (i.e., its tensors and their connectivity).
 * \param[in] optimizerInfo Opaque structure.
 * \param[out] workDesc The workspace descriptor in which the information is collected.
 */
cutensornetStatus_t cutensornetWorkspaceComputeContractionSizes(const cutensornetHandle_t handle,
                                                                const cutensornetNetworkDescriptor_t networkDesc,
                                                                const cutensornetContractionOptimizerInfo_t optimizerInfo,
                                                                cutensornetWorkspaceDescriptor_t workDesc);

/**
 * \brief DEPRECATED: Retrieves the needed workspace size for the given workspace preference and memory space.
 *
 * The needed sizes for different tasks must be pre-calculated by calling the corresponding API, e.g,
 * cutensornetWorkspaceComputeContractionSizes(), cutensornetWorkspaceComputeQRSizes(),
 * cutensornetWorkspaceComputeSVDSizes() and cutensornetWorkspaceComputeGateSplitSizes().
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] workDesc Opaque structure describing the workspace.
 * \param[in] workPref Preference of workspace for planning.
 * \param[in] memSpace The memory space where the workspace is allocated.
 * \param[out] workspaceSize Needed workspace size.
 */
CUTENSORNET_DEPRECATED(cutensornetWorkspaceGetMemorySize)
cutensornetStatus_t cutensornetWorkspaceGetSize(const cutensornetHandle_t handle,
                                                const cutensornetWorkspaceDescriptor_t workDesc,
                                                cutensornetWorksizePref_t workPref,
                                                cutensornetMemspace_t memSpace,
                                                uint64_t *workspaceSize);

/**
 * \brief Retrieves the needed workspace size for the given workspace preference, memory space, workspace kind.
 *
 * The needed sizes for different tasks must be pre-calculated by calling the corresponding API, e.g,
 * cutensornetWorkspaceComputeContractionSizes(), cutensornetWorkspaceComputeQRSizes(),
 * cutensornetWorkspaceComputeSVDSizes() and cutensornetWorkspaceComputeGateSplitSizes().
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] workDesc Opaque structure describing the workspace.
 * \param[in] workPref Preference of workspace for planning.
 * \param[in] memSpace The memory space where the workspace is allocated.
 * \param[in] workKind The kind of workspace.
 * \param[out] memorySize Needed workspace size.
 */
cutensornetStatus_t cutensornetWorkspaceGetMemorySize(const cutensornetHandle_t handle,
                                                      const cutensornetWorkspaceDescriptor_t workDesc,
                                                      cutensornetWorksizePref_t workPref,
                                                      cutensornetMemspace_t memSpace,
                                                      cutensornetWorkspaceKind_t workKind,
                                                      int64_t *memorySize);

/**
 * \brief DEPRECATED: Sets the memory address and workspace size of workspace provided by user.
 *
 * A workspace is valid in the following cases:
 *
 *   - \p workspacePtr is valid and \p workspaceSize > 0
 *   - \p workspacePtr is null and \p workspaceSize > 0 (used during cutensornetCreateContractionPlan() to provide the available workspace).
 *   - \p workspacePtr is null and \p workspaceSize = 0 (workspace memory will be drawn from the user's mempool)
 *
 * A workspace will be validated against the minimal required at usage (cutensornetCreateContractionPlan(), cutensornetContractionAutotune(), cutensornetContraction())
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in,out] workDesc Opaque structure describing the workspace.
 * \param[in] memSpace The memory space where the workspace is allocated.
 * \param[in] workspacePtr Workspace memory pointer, may be null.
 * \param[in] workspaceSize Workspace size, must be >= 0.
 */
CUTENSORNET_DEPRECATED(cutensornetWorkspaceSetMemory)
cutensornetStatus_t cutensornetWorkspaceSet(const cutensornetHandle_t handle,
                                            cutensornetWorkspaceDescriptor_t workDesc,
                                            cutensornetMemspace_t memSpace,
                                            void *const workspacePtr,
                                            uint64_t workspaceSize);
/**
 * \brief Sets the memory address and workspace size of the workspace provided by user.
 *
 * A workspace is valid in the following cases:
 *
 *   - \p memoryPtr is valid and \p memorySize > 0
 *   - \p memoryPtr is null and \p memorySize > 0: used to indicate memory with the indicated \p memorySize should be drawn from the mempool, or for cutensornetCreateContractionPlan() to indicate the available workspace size.
 *   - \p memoryPtr is null and \p memorySize = 0: indicates the workspace of the specified kind is disabled (currently applies to CACHE kind only).
 *   - \p memoryPtr is null and \p memorySize < 0: indicates workspace memory should be drawn from the user's mempool with the ::CUTENSORNET_WORKSIZE_PREF_RECOMMENDED size (see ::cutensornetWorksizePref_t).
 *
 * The \p memorySize of the SCRATCH kind will be validated against the minimal required at usage (cutensornetCreateContractionPlan(), cutensornetContractionAutotune(), cutensornetContraction(), cutensornetContractSlices())
 * The CACHE memory size can be any, the larger the better.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in,out] workDesc Opaque structure describing the workspace.
 * \param[in] memSpace The memory space where the workspace is allocated.
 * \param[in] workKind The kind of workspace.
 * \param[in] memoryPtr Workspace memory pointer, may be null.
 * \param[in] memorySize Workspace size.
 */
cutensornetStatus_t cutensornetWorkspaceSetMemory(const cutensornetHandle_t handle,
                                                  cutensornetWorkspaceDescriptor_t workDesc,
                                                  cutensornetMemspace_t memSpace,
                                                  cutensornetWorkspaceKind_t workKind,
                                                  void *const memoryPtr,
                                                  int64_t memorySize);

/**
 * \brief DEPRECATED: Retrieves the memory address and workspace size of workspace hosted in the workspace descriptor.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] workDesc Opaque structure describing the workspace.
 * \param[in] memSpace The memory space where the workspace is allocated.
 * \param[out] workspacePtr Workspace memory pointer.
 * \param[out] workspaceSize Workspace size.
 */
CUTENSORNET_DEPRECATED(cutensornetWorkspaceGetMemory)
cutensornetStatus_t cutensornetWorkspaceGet(const cutensornetHandle_t handle,
                                            const cutensornetWorkspaceDescriptor_t workDesc,
                                            cutensornetMemspace_t memSpace,
                                            void **workspacePtr,
                                            uint64_t *workspaceSize);

/**
 * \brief Retrieves the memory address and workspace size of workspace hosted in the workspace descriptor.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] workDesc Opaque structure describing the workspace.
 * \param[in] memSpace The memory space where the workspace is allocated.
 * \param[in] workKind The kind of workspace.
 * \param[out] memoryPtr Workspace memory pointer.
 * \param[out] memorySize Workspace size.
 */
cutensornetStatus_t cutensornetWorkspaceGetMemory(const cutensornetHandle_t handle,
                                                  const cutensornetWorkspaceDescriptor_t workDesc,
                                                  cutensornetMemspace_t memSpace,
                                                  cutensornetWorkspaceKind_t workKind,
                                                  void **memoryPtr,
                                                  int64_t *memorySize);

/**
 * \brief Purges the cached data in the specified memory space.
 *
 * \details Purges/invalidates the cached data in the ::CUTENSORNET_WORKSPACE_CACHE workspace kind on the \p memSpace memory space,
 * but does not free the memory nor return it to the memory pool.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in,out] workDesc Opaque structure describing the workspace.
 * \param[in] memSpace The memory space where the workspace is allocated.
 */
cutensornetStatus_t cutensornetWorkspacePurgeCache(const cutensornetHandle_t handle,
                                                    cutensornetWorkspaceDescriptor_t workDesc,
                                                    cutensornetMemspace_t memSpace);

/**
 * \brief Frees the workspace descriptor.
 *
 * Note that this API does not free the memory provided by cutensornetWorkspaceSetMemory().
 *
 * \param[in,out] workDesc Opaque structure.
 */
cutensornetStatus_t cutensornetDestroyWorkspaceDescriptor(cutensornetWorkspaceDescriptor_t workDesc);

/**
 * \brief Sets up the required hyper-optimization parameters for the contraction order solver (see cutensornetContractionOptimize())
 *
 * Note that this function allocates data on the heap; hence, it is critical that cutensornetDestroyContractionOptimizerConfig() is called once \p optimizerConfig is no longer required.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[out] optimizerConfig This data structure holds all information about the user-requested hyper-optimization parameters.
 */
cutensornetStatus_t cutensornetCreateContractionOptimizerConfig(const cutensornetHandle_t handle,
                                                                cutensornetContractionOptimizerConfig_t *optimizerConfig);

/**
 * \brief Frees all the memory associated with \p optimizerConfig.
 *
 * \param[in,out] optimizerConfig Opaque structure.
 */
cutensornetStatus_t cutensornetDestroyContractionOptimizerConfig(cutensornetContractionOptimizerConfig_t optimizerConfig);

/**
 * \brief Gets attributes of \p optimizerConfig.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] optimizerConfig Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[out] buffer On return, this buffer (of size \p sizeInBytes) holds the value that corresponds to \p attr within \p optimizerConfig.
 * \param[in] sizeInBytes Size of \p buffer (in bytes).
 */
cutensornetStatus_t
cutensornetContractionOptimizerConfigGetAttribute(const cutensornetHandle_t handle,
                                                  const cutensornetContractionOptimizerConfig_t optimizerConfig,
                                                  cutensornetContractionOptimizerConfigAttributes_t attr,
                                                  void *buffer,
                                                  size_t sizeInBytes);
/**
 * \brief Sets attributes of \p optimizerConfig.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in,out] optimizerConfig Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[in] buffer This buffer (of size \p sizeInBytes) determines the value to which \p attr will be set.
 * \param[in] sizeInBytes Size of \p buffer (in bytes).
 */
cutensornetStatus_t
cutensornetContractionOptimizerConfigSetAttribute(const cutensornetHandle_t handle,
                                                  cutensornetContractionOptimizerConfig_t optimizerConfig,
                                                  cutensornetContractionOptimizerConfigAttributes_t attr,
                                                  const void *buffer,
                                                  size_t sizeInBytes);

/**
 * \brief Frees all the memory associated with \p optimizerInfo
 *
 * \param[in,out] optimizerInfo Opaque structure.
 */
cutensornetStatus_t cutensornetDestroyContractionOptimizerInfo(cutensornetContractionOptimizerInfo_t optimizerInfo);

/**
 * \brief Allocates resources for \p optimizerInfo.
 *
 * Note that this function allocates data on the heap; hence, it is critical that cutensornetDestroyContractionOptimizerInfo() is called once \p optimizerInfo is no longer required.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] networkDesc Describes the tensor network (i.e., its tensors and their connectivity) for which \p optimizerInfo is created.
 * \param[out] optimizerInfo Pointer to ::cutensornetContractionOptimizerInfo_t.
 */
cutensornetStatus_t cutensornetCreateContractionOptimizerInfo(const cutensornetHandle_t handle,
                                                              const cutensornetNetworkDescriptor_t networkDesc,
                                                              cutensornetContractionOptimizerInfo_t *optimizerInfo);

/**
 * \brief Computes an "optimized" contraction order as well as slicing info (for more information see Overview section) for a given tensor network such that the total time to solution is minimized while adhering to the user-provided memory constraint.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] networkDesc Describes the topology of the tensor network (i.e., all tensors, their connectivity and modes).
 * \param[in] optimizerConfig Holds all hyper-optimization parameters that govern the search for an "optimal" contraction order.
 * \param[in] workspaceSizeConstraint Maximal device memory that will be provided by the user (i.e., cuTensorNet has to find a viable path/slicing solution within this user-defined constraint).
 * \param[in,out] optimizerInfo On return, this object will hold all necessary information about the optimized path and the related slicing information. \p optimizerInfo will hold information including (see ::cutensornetContractionOptimizerInfoAttributes_t):
 *      - Total number of slices.
 *      - Total number of sliced modes.
 *      - Information about the sliced modes (i.e., the IDs of the sliced modes (see \p modesIn w.r.t. cutensornetCreateNetworkDescriptor()) as well as their extents (see Overview section for additional documentation).
 *      - Optimized path.
 *      - FLOP count.
 *      - Total number of elements in the largest intermediate tensor.
 *      - The mode labels for all intermediate tensors.
 *      - The estimated runtime and "effective" flops.
 */
cutensornetStatus_t cutensornetContractionOptimize(const cutensornetHandle_t handle,
                                                   const cutensornetNetworkDescriptor_t networkDesc,
                                                   const cutensornetContractionOptimizerConfig_t optimizerConfig,
                                                   uint64_t workspaceSizeConstraint,
                                                   cutensornetContractionOptimizerInfo_t optimizerInfo);

/**
 * \brief Gets attributes of \p optimizerInfo.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] optimizerInfo Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[out] buffer On return, this buffer (of size \p sizeInBytes) holds the value that corresponds to \p attr within \p optimizeInfo.
 * \param[in] sizeInBytes Size of \p buffer (in bytes).
 */
cutensornetStatus_t
cutensornetContractionOptimizerInfoGetAttribute(const cutensornetHandle_t handle,
                                                const cutensornetContractionOptimizerInfo_t optimizerInfo,
                                                cutensornetContractionOptimizerInfoAttributes_t attr,
                                                void *buffer,
                                                size_t sizeInBytes);

/**
 * \brief Sets attributes of optimizerInfo.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in,out] optimizerInfo Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[in] buffer This buffer (of size \p sizeInBytes) determines the value to which \p attr will be set.
 * \param[in] sizeInBytes Size of \p buffer (in bytes).
 */
cutensornetStatus_t
cutensornetContractionOptimizerInfoSetAttribute(const cutensornetHandle_t handle,
                                                cutensornetContractionOptimizerInfo_t optimizerInfo,
                                                cutensornetContractionOptimizerInfoAttributes_t attr,
                                                const void *buffer,
                                                size_t sizeInBytes);

/**
 * \brief Gets the packed size of the \p optimizerInfo object.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] optimizerInfo Opaque structure of type cutensornetContractionOptimizerInfo_t.
 * \param[out] sizeInBytes The packed size (in bytes).
 */
cutensornetStatus_t
cutensornetContractionOptimizerInfoGetPackedSize(const cutensornetHandle_t handle,
                                                 const cutensornetContractionOptimizerInfo_t optimizerInfo,
                                                 size_t *sizeInBytes);

/**
 * \brief Packs the \p optimizerInfo object into the provided buffer.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] optimizerInfo Opaque structure of type cutensornetContractionOptimizerInfo_t.
 * \param[out] buffer On return, this buffer holds the contents of optimizerInfo in packed form.
 * \param[in] sizeInBytes The size of the buffer (in bytes).
 */
cutensornetStatus_t
cutensornetContractionOptimizerInfoPackData(const cutensornetHandle_t handle,
                                            const cutensornetContractionOptimizerInfo_t optimizerInfo,
                                            void *buffer,
                                            size_t sizeInBytes);

/**
 * \brief Create an optimizerInfo object from the provided buffer.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] networkDesc Describes the tensor network (i.e., its tensors and their connectivity) for which \p optimizerInfo is created.
 * \param[in] buffer A buffer with the contents of optimizerInfo in packed form.
 * \param[in] sizeInBytes The size of the buffer (in bytes).
 * \param[out] optimizerInfo Pointer to ::cutensornetContractionOptimizerInfo_t.
 */
cutensornetStatus_t
cutensornetCreateContractionOptimizerInfoFromPackedData(const cutensornetHandle_t handle,
                                                        const cutensornetNetworkDescriptor_t networkDesc,
                                                        const void *buffer,
                                                        size_t sizeInBytes,
                                                        cutensornetContractionOptimizerInfo_t *optimizerInfo);

/**
 * \brief Update the provided \p optimizerInfo object from the provided buffer.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] buffer A buffer with the contents of optimizerInfo in packed form.
 * \param[in] sizeInBytes The size of the buffer (in bytes).
 * \param[in,out] optimizerInfo Opaque object of type ::cutensornetContractionOptimizerInfo_t that will be updated.
 */
cutensornetStatus_t
cutensornetUpdateContractionOptimizerInfoFromPackedData(const cutensornetHandle_t handle,
                                                        const void *buffer,
                                                        size_t sizeInBytes,
                                                        cutensornetContractionOptimizerInfo_t optimizerInfo);

/**
 * \brief Initializes a ::cutensornetContractionPlan_t.
 *
 * Note that this function allocates data on the heap; hence, it is critical that cutensornetDestroyContractionPlan() is called once \p plan is no longer required.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] networkDesc Describes the tensor network (i.e., its tensors and their connectivity).
 * \param[in] optimizerInfo Opaque structure.
 * \param[in] workDesc Opaque structure describing the workspace. At the creation of the contraction plan, only the workspace size is needed; the pointer to the workspace memory may be left null.
 * If a device memory handler is set, \p workDesc can be set either to null (in which case the "recommended" workspace size is inferred, see ::CUTENSORNET_WORKSIZE_PREF_RECOMMENDED) or to a valid ::cutensornetWorkspaceDescriptor_t with the desired workspace size set and a null workspace pointer, see Memory Management API section.
 * \param[out] plan cuTensorNet's contraction plan holds all the information required to perform
 * the tensor contractions; to be precise, it initializes a \p cutensorContractionPlan_t for
 * each tensor contraction that is required to contract the entire tensor network.
 */
cutensornetStatus_t cutensornetCreateContractionPlan(const cutensornetHandle_t handle,
                                                     const cutensornetNetworkDescriptor_t networkDesc,
                                                     const cutensornetContractionOptimizerInfo_t optimizerInfo,
                                                     const cutensornetWorkspaceDescriptor_t workDesc,
                                                     cutensornetContractionPlan_t *plan);

/**
 * \brief Frees all resources owned by \p plan.
 *
 * \param[in,out] plan Opaque structure.
 */
cutensornetStatus_t cutensornetDestroyContractionPlan(cutensornetContractionPlan_t plan);

/**
 * \brief Auto-tunes the contraction plan to find the best \p cutensorContractionPlan_t for each pair-wise contraction.
 *
 * \note This function is blocking due to the nature of the auto-tuning process.
 * \note Input and output data pointers are recommended to be 256-byte aligned for best performance.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in,out] plan The plan must already be created (see cutensornetCreateContractionPlan()); the individual contraction plans will be fine-tuned.
 * \param[in] rawDataIn Array of N pointers (N being the number of input tensors specified cutensornetCreateNetworkDescriptor()); ``rawDataIn[i]`` points to the data associated with the i-th input tensor (in device memory).
 * \param[out] rawDataOut Points to the raw data of the output tensor (in device memory).
 * \param[in] workDesc Opaque structure describing the workspace. The provided workspace must be \em valid (the workspace size must be the same as or larger than both the minimum needed and the value provided at plan creation). See cutensornetCreateContractionPlan(), cutensornetWorkspaceGetMemorySize() & cutensornetWorkspaceSetMemory().
 * If a device memory handler is set, the \p workDesc can be set to null, or the workspace pointer in \p workDesc can be set to null, and the workspace size can be set either to 0 (in which case the "recommended" size is used, see ::CUTENSORNET_WORKSIZE_PREF_RECOMMENDED) or to a \em valid size. A workspace of the specified size will be drawn from the user's mempool and released back once done.
 * \param[in] pref Controls the auto-tuning process and gives the user control over how much time is spent in this routine.
 * \param[in] stream The CUDA stream on which the computation is performed.
 */
cutensornetStatus_t cutensornetContractionAutotune(const cutensornetHandle_t handle,
                                                   cutensornetContractionPlan_t plan,
                                                   const void *const rawDataIn[],
                                                   void *rawDataOut,
                                                   cutensornetWorkspaceDescriptor_t workDesc,
                                                   const cutensornetContractionAutotunePreference_t pref,
                                                   cudaStream_t stream);

/**
 * \brief Sets up the required auto-tune parameters for the contraction plan
 *
 * Note that this function allocates data on the heap; hence, it is critical that cutensornetDestroyContractionAutotunePreference() is called once \p autotunePreference is no longer required.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[out] autotunePreference This data structure holds all information about the user-requested auto-tune parameters.
 */
cutensornetStatus_t cutensornetCreateContractionAutotunePreference(const cutensornetHandle_t handle,
                                                                   cutensornetContractionAutotunePreference_t *autotunePreference);

/**
 * \brief Gets attributes of \p autotunePreference.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] autotunePreference Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[out] buffer On return, this buffer (of size \p sizeInBytes) holds the value that corresponds to \p attr within \p autotunePreference.
 * \param[in] sizeInBytes Size of \p buffer (in bytes).
 */
cutensornetStatus_t
cutensornetContractionAutotunePreferenceGetAttribute(const cutensornetHandle_t handle,
                                                     const cutensornetContractionAutotunePreference_t autotunePreference,
                                                     cutensornetContractionAutotunePreferenceAttributes_t attr,
                                                     void *buffer,
                                                     size_t sizeInBytes);
/**
 * \brief Sets attributes of \p autotunePreference.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in,out] autotunePreference Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[in] buffer This buffer (of size \p sizeInBytes) determines the value to which \p attr will be set.
 * \param[in] sizeInBytes Size of \p buffer (in bytes).
 */
cutensornetStatus_t
cutensornetContractionAutotunePreferenceSetAttribute(const cutensornetHandle_t handle,
                                                     cutensornetContractionAutotunePreference_t autotunePreference,
                                                     cutensornetContractionAutotunePreferenceAttributes_t attr,
                                                     const void *buffer,
                                                     size_t sizeInBytes);

/**
 * \brief Frees all the memory associated with \p autotunePreference
 *
 * \param[in,out] autotunePreference Opaque structure.
 */
cutensornetStatus_t cutensornetDestroyContractionAutotunePreference(cutensornetContractionAutotunePreference_t autotunePreference);

/**
 * \brief DEPRECATED: Performs the actual contraction of the tensor network.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in,out] plan Encodes the execution of a tensor network contraction (see cutensornetCreateContractionPlan() and cutensornetContractionAutotune()). Some internal meta-data may be updated upon contraction.
 * \param[in] rawDataIn Array of N pointers (N being the number of input tensors specified cutensornetCreateNetworkDescriptor()); ``rawDataIn[i]`` points to the data associated with the i-th input tensor (in device memory).
 * \param[out] rawDataOut Points to the raw data of the output tensor (in device memory).
 * \param[in] workDesc Opaque structure describing the workspace. The provided workspace must be \em valid (the workspace size must be the same as or larger than both the minimum needed and the value provided at plan creation). See cutensornetCreateContractionPlan(), cutensornetWorkspaceGetMemorySize() & cutensornetWorkspaceSetMemory()).
 * If a device memory handler is set, then \p workDesc can be set to null, or the workspace pointer in \p workDesc can be set to null, and the workspace size can be set either to 0 (in which case the "recommended" size is used, see ::CUTENSORNET_WORKSIZE_PREF_RECOMMENDED) or to a \em valid size. A workspace of the specified size will be drawn from the user's mempool and released back once done.
 * \param[in] sliceId The ID of the slice that is currently contracted (this value ranges between ``0`` and ``optimizerInfo.numSlices``); use ``0`` if no slices are used.
 * \param[in] stream The CUDA stream on which the computation is performed.
 *
 * \note If multiple slices are created, the order of contracting over slices using cutensornetContraction() should be ascending
 * starting from slice 0. If parallelizing over slices manually (in any fashion: streams, devices, processes, etc.), please make
 * sure the output tensors (that are subject to a global reduction) are zero-initialized.
 *
 * \note Input and output data pointers are recommended to be 256-byte aligned for best performance.
 *
 * \note This function is asynchronous w.r.t. the calling CPU thread. The user should guarantee that the memory buffer provided in \p workDesc is valid until a synchronization with the stream or the device is executed.
 */
CUTENSORNET_DEPRECATED(cutensornetContractSlices)
cutensornetStatus_t cutensornetContraction(const cutensornetHandle_t handle,
                                           cutensornetContractionPlan_t plan,
                                           const void *const rawDataIn[],
                                           void *rawDataOut,
                                           cutensornetWorkspaceDescriptor_t workDesc,
                                           int64_t sliceId,
                                           cudaStream_t stream);

/**
 * \brief Create a `cutensornetSliceGroup_t` object from a range, which produces a sequence of slice IDs from the specified start (inclusive) to the specified stop (exclusive) values with the specified step. The sequence can be increasing or decreasing depending on the start and stop values.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] sliceIdStart The start slice ID.
 * \param[in] sliceIdStop The final slice ID is the largest (smallest) integer that excludes this value and all those above (below) for an increasing (decreasing) sequence.
 * \param[in] sliceIdStep The step size between two successive slice IDs. A negative step size should be specified for a decreasing sequence.
 * \param[out] sliceGroup Opaque object specifying the slice IDs.
 */
cutensornetStatus_t cutensornetCreateSliceGroupFromIDRange(const cutensornetHandle_t handle,
                                                           int64_t sliceIdStart,
                                                           int64_t sliceIdStop,
                                                           int64_t sliceIdStep,
                                                           cutensornetSliceGroup_t *sliceGroup);
/**
 * \brief Create a `cutensornetSliceGroup_t` object from a sequence of slice IDs. Duplicates in the input slice ID sequence will be removed.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] beginIDSequence A pointer to the beginning of the slice ID sequence.
 * \param[in] endIDSequence A pointer to the end of the slice ID sequence.
 * \param[out] sliceGroup Opaque object specifying the slice IDs.
 */
cutensornetStatus_t cutensornetCreateSliceGroupFromIDs(const cutensornetHandle_t handle,
                                                       const int64_t *beginIDSequence,
                                                       const int64_t *endIDSequence,
                                                       cutensornetSliceGroup_t *sliceGroup);

/**
 * \brief  Releases the resources associated with a `cutensornetSliceGroup_t` object and sets its value to null.
 *
 * \param[in,out] sliceGroup Opaque object specifying the slices to be contracted (see cutensornetCreateSliceGroupFromIDRange() and cutensornetCreateSliceGroupFromIDs()).
 */
cutensornetStatus_t cutensornetDestroySliceGroup(cutensornetSliceGroup_t sliceGroup);

/**
 * \brief Performs the actual contraction of the tensor network.
 *
 * \warning In the current release, this function will synchronize the stream
 * in case distributed execution is activated (via ::cutensornetDistributedResetConfiguration)
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in,out] plan Encodes the execution of a tensor network contraction (see cutensornetCreateContractionPlan() and cutensornetContractionAutotune()). Some internal meta-data may be updated upon contraction.
 * \param[in] rawDataIn Array of N pointers (N being the number of input tensors specified in cutensornetCreateNetworkDescriptor()): ``rawDataIn[i]`` points to the data associated with the i-th input tensor (in device memory).
 * \param[out] rawDataOut Points to the raw data of the output tensor (in device memory).
 * \param[in] accumulateOutput If 0, write the contraction result into rawDataOut; otherwise accumulate the result into rawDataOut.
 * \param[in] workDesc Opaque structure describing the workspace.
 * The provided ::CUTENSORNET_WORKSPACE_SCRATCH workspace must be \em valid (the workspace pointer must be device accessible, see ::cutensornetMemspace_t, and the workspace size must be the same as or larger than both the minimum needed and the value provided at plan creation). See cutensornetCreateContractionPlan(), cutensornetWorkspaceGetMemorySize() & cutensornetWorkspaceSetMemory().
 * The provided ::CUTENSORNET_WORKSPACE_CACHE workspace must be device accessible, see ::cutensornetMemspace_t; it can be of any size, the larger the better, up to the size that can be queried with cutensornetWorkspaceGetMemorySize().
 * If a device memory handler is set, then \p workDesc can be set to null, or the memory pointer in \p workDesc of either the workspace kinds can be set to null, and the workspace size can be set either to a negative value (in which case the "recommended" size is used, see ::CUTENSORNET_WORKSIZE_PREF_RECOMMENDED) or to a \em valid size.
 * For a workspace of kind ::CUTENSORNET_WORKSPACE_SCRATCH, a memory buffer with the specified size will be drawn from the user's mempool and released back once done.
 * For a workspace of kind ::CUTENSORNET_WORKSPACE_CACHE, a memory buffer with the specified size will be drawn from the user's mempool and released back once the \p workDesc is destroyed, if \p workDesc != NULL, otherwise, once the \p plan is destroyed, or an alternative \p workDesc with a different memory address/size is provided in a subsequent cutensornetContractSlices() call.
 * \param[in] sliceGroup Opaque object specifying the slices to be contracted (see cutensornetCreateSliceGroupFromIDRange() and cutensornetCreateSliceGroupFromIDs()). *If set to null, all slices will be contracted.*
 * \param[in] stream The CUDA stream on which the computation is performed.
 *
 * \note Input and output data pointers are recommended to be at least 256-byte aligned for best performance.
 */
cutensornetStatus_t cutensornetContractSlices(const cutensornetHandle_t handle,
                                              cutensornetContractionPlan_t plan,
                                              const void *const rawDataIn[],
                                              void *rawDataOut,
                                              int32_t accumulateOutput,
                                              cutensornetWorkspaceDescriptor_t workDesc,
                                              const cutensornetSliceGroup_t sliceGroup,
                                              cudaStream_t stream);

/**
 * \brief Computes the gradients of the network w.r.t. the input tensors whose gradients are required. The network must have been contracted and loaded in the \p workDesc CACHE. Operates only on networks with single slice and no singleton modes.
 *
 * \note This function is experimental and is subject to change in future releases.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in,out] plan Encodes the execution of a tensor network contraction (see cutensornetCreateContractionPlan() and cutensornetContractionAutotune()). Some internal meta-data may be updated upon contraction.
 * \param[in] rawDataIn Array of N pointers (N being the number of input tensors specified in cutensornetCreateNetworkDescriptor()): ``rawDataIn[i]`` points to the data associated with the i-th input tensor (in device memory).
 * \param[in] outputGradient Gradient of the output tensor (in device memory). Must have the same memory layout (strides) as the output tensor of the tensor network.
 * \param[in,out] gradients Array of N pointers: ``gradients[i]`` points to the gradient data associated with the i-th input tensor in device memory. Setting ``gradients[i]`` to null would skip computing the gradient of the i-th input tensor. Generated gradient data has the same memory layout (strides) as their corresponding input tensors.
 * \param[in] accumulateOutput If 0, write the gradient results into \p gradients; otherwise accumulates the results into \p gradients.
 * \param[in] workDesc Opaque structure describing the workspace.
 * The provided ::CUTENSORNET_WORKSPACE_SCRATCH workspace must be \em valid (the workspace pointer must be device accessible, see ::cutensornetMemspace_t, and the workspace size must be the same as or larger than the minimum needed). See cutensornetWorkspaceComputeContractionSizes(), cutensornetWorkspaceGetMemorySize() & cutensornetWorkspaceSetMemory().
 * The provided ::CUTENSORNET_WORKSPACE_CACHE workspace must be \em valid (the workspace pointer must be device accessible, see ::cutensornetMemspace_t), and contains the cached intermediate tensors from the corresponding cutensornetContractSlices() call.
 * If a device memory handler is set, and \p workDesc is set to null, or the memory pointer in \p workDesc of either the workspace kinds is set to null, for both calls to cutensornetContractSlices() and cutensornetComputeGradientsBackward(), memory will be drawn from the memory pool. See cutensornetContractSlices() for details.
 * \param[in] stream The CUDA stream on which the computation is performed.
 *
 * \note This function should be preceded with a call to cutensornetContractSlices(); Both calls to cutensornetContractSlices() and cutensornetComputeGradientsBackward() should use either the same \p workDesc instance (in order to share the CACHE memory), or both pass null to \p workDesc to use same mempool allocation for CACHE. \p workDesc and \p plan should not be altered in between these calls.
 * \note Calling cutensornetWorkspacePurgeCache() is necessary for computing gradients of different data sets (the combo cutensornetContractSlices() and cutensornetComputeGradientsBackward() calls generate cached data that is only valid for the corresponding dataset and should be purged when the input tensors' data change)
 * \note Input data's, output data's, and workspace buffers' pointers are recommended to be at least 256-byte aligned for best performance.
 * \note When the provided ::CUTENSORNET_WORKSPACE_CACHE workspace is allocated on the host memory, this function will optimize data transfer from/to CPU memory through the provided SCRATCH buffer. Thus, providing a larger SCRATCH memory than the minimum required enables better performance.
 */
CUTENSORNET_EXPERIMENTAL(cutensornetComputeGradientsBackward)
cutensornetStatus_t cutensornetComputeGradientsBackward(const cutensornetHandle_t handle,
                                                        cutensornetContractionPlan_t plan,
                                                        const void *const rawDataIn[],
                                                        const void *outputGradient,
                                                        void *const gradients[],
                                                        int32_t accumulateOutput,
                                                        cutensornetWorkspaceDescriptor_t workDesc,
                                                        cudaStream_t stream);

/**
 * \brief Initializes a ::cutensornetTensorDescriptor_t, describing the information of a tensor.
 *
 * Note that this function allocates data on the heap; hence, it is critical that cutensornetDestroyTensorDescriptor() is called once \p tensorDesc is no longer required.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] numModes The number of modes of the tensor.
 * \param[in] extents Array of size \p numModes; ``extents[j]`` corresponding to the extent of the j-th mode of the tensor.
 * \param[in] strides Array of size \p numModes; ``strides[j]`` corresponding to the linearized offset -- in physical memory -- between two logically-neighboring elements w.r.t the j-th mode of the tensor.
 * \param[in] modeLabels Array of size \p numModes; ``modeLabels[j]`` denotes the label of j-th mode of the tensor.
 * \param[in] dataType Denotes the data type for the tensor.
 * \param[out] tensorDesc Pointer to a ::cutensornetTensorDescriptor_t.
 *
 * \note If \p strides is set to \p NULL, it means the tensor is in the Fortran (column-major) layout.
 */
cutensornetStatus_t cutensornetCreateTensorDescriptor(const cutensornetHandle_t handle,
                                                      int32_t numModes,
                                                      const int64_t extents[],
                                                      const int64_t strides[],
                                                      const int32_t modeLabels[],
                                                      cudaDataType_t dataType,
                                                      cutensornetTensorDescriptor_t *tensorDesc);

/**
 * \brief Frees all the memory associated with the tensor descriptor.
 *
 * \param[in,out] tensorDesc Opaque handle to a tensor descriptor.
 */
cutensornetStatus_t cutensornetDestroyTensorDescriptor(cutensornetTensorDescriptor_t tensorDesc);

/**
 * \brief Sets up the options for singular value decomposition and truncation.
 *
 * Note that this function allocates data on the heap; hence, it is critical that cutensornetDestroyTensorSVDConfig() is called once \p svdConfig is no longer required.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[out] svdConfig This data structure holds the user-requested svd parameters.
 */
cutensornetStatus_t cutensornetCreateTensorSVDConfig(const cutensornetHandle_t handle,
                                                     cutensornetTensorSVDConfig_t *svdConfig);

/**
 * \brief Frees all the memory associated with the tensor svd configuration.
 *
 * \param[in,out] svdConfig Opaque handle to a tensor svd configuration.
 */
cutensornetStatus_t cutensornetDestroyTensorSVDConfig(cutensornetTensorSVDConfig_t svdConfig);

/**
 * \brief Gets attributes of \p svdConfig.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] svdConfig Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[out] buffer On return, this buffer (of size \p sizeInBytes) holds the value that corresponds to \p attr within \p svdConfig.
 * \param[in] sizeInBytes Size of \p buffer (in bytes).
 */
cutensornetStatus_t cutensornetTensorSVDConfigGetAttribute(const cutensornetHandle_t handle,
                                                           const cutensornetTensorSVDConfig_t svdConfig,
                                                           cutensornetTensorSVDConfigAttributes_t attr,
                                                           void *buffer,
                                                           size_t sizeInBytes);

/**
 * \brief Sets attributes of \p svdConfig.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] svdConfig Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[in] buffer This buffer (of size \p sizeInBytes) determines the value to which \p attr will be set.
 * \param[in] sizeInBytes Size of \p buffer (in bytes).
 */
cutensornetStatus_t cutensornetTensorSVDConfigSetAttribute(const cutensornetHandle_t handle,
                                                           cutensornetTensorSVDConfig_t svdConfig,
                                                           cutensornetTensorSVDConfigAttributes_t attr,
                                                           const void *buffer,
                                                           size_t sizeInBytes);

/**
 * \brief Computes the workspace size needed to perform the tensor SVD operation.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] descTensorIn Describes the modes, extents and other metadata information for a tensor.
 * \param[in] descTensorU Describes the modes, extents and other metadata information for the output tensor U.
 * \param[in] descTensorV Describes the modes, extents and other metadata information for the output tensor V.
 * \param[in] svdConfig This data structure holds the user-requested svd parameters.
 * \param[out] workDesc The workspace descriptor in which the information is collected.
 */
cutensornetStatus_t cutensornetWorkspaceComputeSVDSizes(const cutensornetHandle_t handle,
                                                        const cutensornetTensorDescriptor_t descTensorIn,
                                                        const cutensornetTensorDescriptor_t descTensorU,
                                                        const cutensornetTensorDescriptor_t descTensorV,
                                                        const cutensornetTensorSVDConfig_t svdConfig,
                                                        cutensornetWorkspaceDescriptor_t workDesc);

/**
 * \brief Computes the workspace size needed to perform the tensor QR operation.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] descTensorIn Describes the modes, extents and other metadata information for a tensor.
 * \param[in] descTensorQ Describes the modes, extents and other metadata information for the output tensor Q.
 * \param[in] descTensorR Describes the modes, extents and other metadata information for the output tensor R.
 * \param[out] workDesc The workspace descriptor in which the information is collected.
 */
cutensornetStatus_t cutensornetWorkspaceComputeQRSizes(const cutensornetHandle_t handle,
                                                       const cutensornetTensorDescriptor_t descTensorIn,
                                                       const cutensornetTensorDescriptor_t descTensorQ,
                                                       const cutensornetTensorDescriptor_t descTensorR,
                                                       cutensornetWorkspaceDescriptor_t workDesc);

/**
 * \brief Sets up the information for singular value decomposition.
 *
 * Note that this function allocates data on the heap; hence, it is critical that cutensornetDestroyTensorSVDInfo() is called once \p svdInfo is no longer required.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[out] svdInfo This data structure holds all information about the trucation at runtime.
 */
cutensornetStatus_t cutensornetCreateTensorSVDInfo(const cutensornetHandle_t handle,
                                                   cutensornetTensorSVDInfo_t *svdInfo);

/**
 * \brief Gets attributes of \p svdInfo.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] svdInfo Opaque structure that is accessed.
 * \param[in] attr Specifies the attribute that is requested.
 * \param[out] buffer On return, this buffer (of size \p sizeInBytes) holds the value that corresponds to \p attr within \p svdConfig.
 * \param[in] sizeInBytes Size of \p buffer (in bytes).
 */
cutensornetStatus_t cutensornetTensorSVDInfoGetAttribute(const cutensornetHandle_t handle,
                                                         const cutensornetTensorSVDInfo_t svdInfo,
                                                         cutensornetTensorSVDInfoAttributes_t attr,
                                                         void *buffer,
                                                         size_t sizeInBytes);

/**
 * \brief Frees all the memory associated with the TensorSVDInfo object.
 *
 * \param[in,out] svdInfo Opaque handle to a TensorSVDInfo object.
 */
cutensornetStatus_t cutensornetDestroyTensorSVDInfo(cutensornetTensorSVDInfo_t svdInfo);

/**
 * \brief Performs SVD decomposition of a tensor.
 *
 * \details The partition of all input modes in \p descTensorIn is specified in \p descTensorU and \p descTensorV.
 * \p descTensorU and \p descTensorV are expected to share exactly one mode. The extent of the shared mode shall not exceed the minimum of m (row dimension)
 * and n (column dimension) for the equivalent combined matrix SVD.
 * The following variants of tensor SVD are supported:
 *   - 1. Exact SVD: This can be specified by setting the extent of the shared mode in \p descTensorU and \p descTensorV to be the mininum of m and n, and setting \p svdConfig to \p NULL.
 *   - 2. SVD with fixed extent truncation: This can be specified by setting the extent of the shared mode in \p descTensorU and \p descTensorV to be lower than the mininum of m and n.
 *   - 3. SVD with value-based truncation: This can be specified by setting ::CUTENSORNET_TENSOR_SVD_CONFIG_ABS_CUTOFF or ::CUTENSORNET_TENSOR_SVD_CONFIG_REL_CUTOFF attribute of \p svdConfig.
 *   - 4. SVD with a combination of fixed extent and value-based truncation as described above.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] descTensorIn Describes the modes, extents, and other metadata information of a tensor.
 * \param[in] rawDataIn Pointer to the raw data of the input tensor (in device memory).
 * \param[in,out] descTensorU Describes the modes, extents, and other metadata information of the output tensor U.
 * The extents for uncontracted modes are expected to be consistent with \p descTensorIn.
 * \param[out] u Pointer to the output tensor data U (in device memory).
 * \param[out] s Pointer to the output tensor data S (in device memory).
 * Can be \p NULL when the ::CUTENSORNET_TENSOR_SVD_CONFIG_S_PARTITION attribute of \p svdConfig is not set to default (::CUTENSORNET_TENSOR_SVD_PARTITION_NONE).
 * \param[in,out] descTensorV Describes the modes, extents, and other metadata information of the output tensor V.
 * \param[out] v Pointer to the output tensor data V (in device memory).
 * \param[in] svdConfig This data structure holds the user-requested SVD parameters.
 * Can be \p NULL if users do not need to perform value-based truncation or singular value partitioning.
 * \param[out] svdInfo Opaque structure holding all information about the trucation at runtime. Can be \p NULL if runtime information on singular value truncation is not needed.
 * \param[in] workDesc Opaque structure describing the workspace. The provided workspace must be \em valid (the workspace size must be the same as or larger than the minimum needed). See cutensornetWorkspaceGetMemorySize() & cutensornetWorkspaceSetMemory().
 * \param[in] stream The CUDA stream on which the computation is performed.
 *
 * \note In the case of exact SVD or SVD with fixed extent truncation, \p descTensorU and \p descTensorV will remain constant after the execution.
 * The data in \p u and \p v will respect the \p extent and \p stride in these tensor descriptors.
 * \note When value-based truncation is requested in \p svdConfig, `cutensornetTensorSVD` searches for the minimal extent that satifies both the value-based truncation and fixed extent requirement.
 * If the resulting extent is found to be the same as the one specified in U/V tensor descriptors, the \p extent and \p stride from the tensor descriptors will be respected.
 * If the resulting extent is found to be lower than the one specified in U/V tensor descriptors, the data in \p u and \p v will adopt a new Fortran-layout matching the reduced extent found.
 * The \p extent and \p stride in \p descTensorU and \p descTensorV will also be overwritten to reflect this change.
 * The user can query the reduced extent with cutensornetTensorSVDInfoGetAttribute() or cutensornetGetTensorDetails() (which also returns the new strides).
 * \note As the reduced size for value-based truncation is not known until runtime, the user should always allocate based on the full data size specified by the initial \p descTensorU and \p descTensorV for \p u and \p v.
 *
 */
cutensornetStatus_t cutensornetTensorSVD(const cutensornetHandle_t handle,
                                         const cutensornetTensorDescriptor_t descTensorIn,
                                         const void *const rawDataIn,
                                         cutensornetTensorDescriptor_t descTensorU,
                                         void *u,
                                         void *s,
                                         cutensornetTensorDescriptor_t descTensorV,
                                         void *v,
                                         const cutensornetTensorSVDConfig_t svdConfig,
                                         cutensornetTensorSVDInfo_t svdInfo,
                                         const cutensornetWorkspaceDescriptor_t workDesc,
                                         cudaStream_t stream);

/**
 * \brief Performs QR decomposition of a tensor.
 *
 * \details The partition of all input modes in \p descTensorIn is specified in \p descTensorQ and \p descTensorR.
 * \p descTensorQ and \p descTensorR are expected to share exactly one mode and the extent of that mode shall not exceed the minimum of m (row dimension)
 * and n (column dimension) of the equivalent combined matrix QR.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] descTensorIn Describes the modes, extents, and other metadata information of a tensor.
 * \param[in] rawDataIn Pointer to the raw data of the input tensor (in device memory).
 * \param[in] descTensorQ Describes the modes, extents, and other metadata information of the output tensor Q.
 * \param[out] q Pointer to the output tensor data Q (in device memory).
 * \param[in] descTensorR Describes the modes, extents, and other metadata information of the output tensor R.
 * \param[out] r Pointer to the output tensor data R (in device memory).
 * \param[in] workDesc Opaque structure describing the workspace. The provided workspace must be \em valid (the workspace size must be the same as or larger than the minimum needed). See cutensornetWorkspaceGetMemorySize() & cutensornetWorkspaceSetMemory().
 * \param[in] stream The CUDA stream on which the computation is performed.
 */
cutensornetStatus_t cutensornetTensorQR(const cutensornetHandle_t handle,
                                        const cutensornetTensorDescriptor_t descTensorIn,
                                        const void *const rawDataIn,
                                        const cutensornetTensorDescriptor_t descTensorQ,
                                        void *q,
                                        const cutensornetTensorDescriptor_t descTensorR,
                                        void *r,
                                        const cutensornetWorkspaceDescriptor_t workDesc,
                                        cudaStream_t stream);

/**
 * \brief Computes the workspace size needed to perform the gating operation.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] descTensorInA Describes the modes, extents, and other metadata information of the input tensor A.
 * \param[in] descTensorInB Describes the modes, extents, and other metadata information of the input tensor B.
 * \param[in] descTensorInG Describes the modes, extents, and other metadata information of the input gate tensor.
 * \param[in] descTensorU Describes the modes, extents, and other metadata information of the output U tensor.
 * The extents of uncontracted modes are expected to be consistent with \p descTensorInA and \p descTensorInG.
 * \param[in] descTensorV Describes the modes, extents, and other metadata information of the output V tensor.
 * The extents of uncontracted modes are expected to be consistent with \p descTensorInB and \p descTensorInG.
 * \param[in] gateAlgo The algorithm to use for splitting the gate tensor onto tensor A and B.
 * \param[in] svdConfig Opaque structure holding the user-requested SVD parameters.
 * \param[in] computeType Denotes the compute type used throughout the computation.
 * \param[out] workDesc Opaque structure describing the workspace.
 *
 */
cutensornetStatus_t cutensornetWorkspaceComputeGateSplitSizes(const cutensornetHandle_t handle,
                                                              const cutensornetTensorDescriptor_t descTensorInA,
                                                              const cutensornetTensorDescriptor_t descTensorInB,
                                                              const cutensornetTensorDescriptor_t descTensorInG,
                                                              const cutensornetTensorDescriptor_t descTensorU,
                                                              const cutensornetTensorDescriptor_t descTensorV,
                                                              const cutensornetGateSplitAlgo_t gateAlgo,
                                                              const cutensornetTensorSVDConfig_t svdConfig,
                                                              cutensornetComputeType_t computeType,
                                                              cutensornetWorkspaceDescriptor_t workDesc);

/**
 * \brief Performs gate split operation.
 *
 * \details \p descTensorInA, \p descTensorInB, and \p descTensorInG are expected to form a fully connected graph where the uncontracted modes are partitioned
 * onto \p descTensorU and \p descTensorV via tensor SVD. \p descTensorU and \p descTensorV are expected to share exactly one mode. The extent of that mode shall not exceed the minimum of m (row dimension)
 * and n (column dimension) of the smallest equivalent matrix SVD problem.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] descTensorInA Describes the modes, extents, and other metadata information of the input tensor A.
 * \param[in] rawDataInA Pointer to the raw data of the input tensor A (in device memory).
 * \param[in] descTensorInB Describes the modes, extents, and other metadata information of the input tensor B.
 * \param[in] rawDataInB Pointer to the raw data of the input tensor B (in device memory).
 * \param[in] descTensorInG Describes the modes, extents, and other metadata information of the input gate tensor.
 * \param[in] rawDataInG Pointer to the raw data of the input gate tensor G (in device memory).
 * \param[in] descTensorU Describes the modes, extents, and other metadata information of the output U tensor.
 * The extents of uncontracted modes are expected to be consistent with \p descTensorInA and \p descTensorInG.
 * \param[out] u Pointer to the output tensor data U (in device memory).
 * \param[out] s Pointer to the output tensor data S (in device memory).
 * Can be \p NULL when the ::CUTENSORNET_TENSOR_SVD_CONFIG_S_PARTITION attribute of \p svdConfig is not set to default (::CUTENSORNET_TENSOR_SVD_PARTITION_NONE).
 * \param[in] descTensorV Describes the modes, extents, and other metadata information of the output V tensor.
 * The extents of uncontracted modes are expected to be consistent with \p descTensorInB and \p descTensorInG.
 * \param[out] v Pointer to the output tensor data V (in device memory).
 * \param[in] gateAlgo The algorithm to use for splitting the gate tensor into tensor A and B.
 * \param[in] svdConfig Opaque structure holding the user-requested SVD parameters.
 * \param[in] computeType Denotes the compute type used throughout the computation.
 * \param[out] svdInfo Opaque structure holding all information about the truncation at runtime.
 * \param[in] workDesc Opaque structure describing the workspace.
 * \param[in] stream The CUDA stream on which the computation is performed.
 *
 * \note The options for truncation and the treatment of \p extent and \p stride follows the same logic as tensor SVD, see cutensornetTensorSVD().
 */
cutensornetStatus_t cutensornetGateSplit(const cutensornetHandle_t handle,
                                         const cutensornetTensorDescriptor_t descTensorInA,
                                         const void *rawDataInA,
                                         const cutensornetTensorDescriptor_t descTensorInB,
                                         const void *rawDataInB,
                                         const cutensornetTensorDescriptor_t descTensorInG,
                                         const void *rawDataInG,
                                         cutensornetTensorDescriptor_t descTensorU,
                                         void *u,
                                         void *s,
                                         cutensornetTensorDescriptor_t descTensorV,
                                         void *v,
                                         const cutensornetGateSplitAlgo_t gateAlgo,
                                         const cutensornetTensorSVDConfig_t svdConfig,
                                         cutensornetComputeType_t computeType,
                                         cutensornetTensorSVDInfo_t svdInfo,
                                         const cutensornetWorkspaceDescriptor_t workDesc,
                                         cudaStream_t stream);

/**
 * \brief Get the current device memory handler.
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[out] devMemHandler If previously set, the struct pointed to by \p handler is filled in, otherwise ::CUTENSORNET_STATUS_NO_DEVICE_ALLOCATOR is returned.
 */
cutensornetStatus_t cutensornetGetDeviceMemHandler(const cutensornetHandle_t handle,
                                                   cutensornetDeviceMemHandler_t *devMemHandler);

/**
 * \brief Set the current device memory handler.
 *
 * Once set, when cuTensorNet needs device memory in various API calls it will allocate from the user-provided memory pool
 * and deallocate at completion. See ::cutensornetDeviceMemHandler_t and APIs that require ::cutensornetWorkspaceDescriptor_t
 * for further detail.
 *
 * The internal stream order is established using the user-provided stream passed to cutensornetContractionAutotune() and
 * cutensornetContraction().
 *
 * \warning It is <em> undefined behavior </em> for the following scenarios:
 *   - the library handle is bound to a memory handler and subsequently to another handler
 *   - the library handle outlives the attached memory pool
 *   - the memory pool is not <em> stream-ordered </em>
 *
 * \param[in] handle Opaque handle holding cuTensorNet's library context.
 * \param[in] devMemHandler the device memory handler that encapsulates the user's mempool. The struct content is copied internally.
 */
cutensornetStatus_t cutensornetSetDeviceMemHandler(cutensornetHandle_t handle,
                                                   const cutensornetDeviceMemHandler_t *devMemHandler);

/**
 * \brief This function sets the logging callback routine.
 * \param[in] callback Pointer to a callback function. Check ::cutensornetLoggerCallback_t.
 */
cutensornetStatus_t cutensornetLoggerSetCallback(cutensornetLoggerCallback_t callback);

/**
 * \brief This function sets the logging callback routine, along with user data.
 * \param[in] callback Pointer to a callback function. Check ::cutensornetLoggerCallbackData_t.
 * \param[in] userData Pointer to user-provided data to be used by the callback.
 */
cutensornetStatus_t cutensornetLoggerSetCallbackData(cutensornetLoggerCallbackData_t callback,
                                                     void *userData);

/**
 * \brief This function sets the logging output file.
 * \param[in] file An open file with write permission.
 */
cutensornetStatus_t cutensornetLoggerSetFile(FILE *file);

/**
 * \brief This function opens a logging output file in the given path.
 * \param[in] logFile Path to the logging output file.
 */
cutensornetStatus_t cutensornetLoggerOpenFile(const char *logFile);

/**
 * \brief This function sets the value of the logging level.
 * \param[in] level Log level, should be one of the following:
 * Level| Summary           | Long Description
 * -----|-------------------|-----------------
 *  "0" | Off               | logging is disabled (default)
 *  "1" | Errors            | only errors will be logged
 *  "2" | Performance Trace | API calls that launch CUDA kernels will log their parameters and important information
 *  "3" | Performance Hints | hints that can potentially improve the application's performance
 *  "4" | Heuristics Trace  | provides general information about the library execution, may contain details about heuristic status
 *  "5" | API Trace         | API Trace - API calls will log their parameter and important information
 */
cutensornetStatus_t cutensornetLoggerSetLevel(int32_t level);

/**
 * \brief This function sets the value of the log mask.
 *
 * \param[in]  mask  Value of the logging mask.
 * Masks are defined as a combination (bitwise OR) of the following masks:
 * Level| Description       |
 * -----|-------------------|
 *  "0" | Off               |
 *  "1" | Errors            |
 *  "2" | Performance Trace |
 *  "4" | Performance Hints |
 *  "8" | Heuristics Trace  |
 *  "16"| API Trace         |
 *
 * Refer to cutensornetLoggerSetLevel() for details.
 */
cutensornetStatus_t cutensornetLoggerSetMask(int32_t mask);

/**
 * \brief This function disables logging for the entire run.
 */
cutensornetStatus_t cutensornetLoggerForceDisable();

/**
 * \brief Returns Version number of the cuTensorNet library
 */
size_t cutensornetGetVersion();

/**
 * \brief Returns version number of the CUDA runtime that cuTensorNet was compiled against
 * \details Can be compared against the CUDA runtime version from cudaRuntimeGetVersion().
 */
size_t cutensornetGetCudartVersion();

/**
 * \brief Returns the description string for an error code
 * \param[in] error Error code to convert to string.
 * \returns the error string
 * \remarks non-blocking, no reentrant, and thread-safe
 */
const char *cutensornetGetErrorString(cutensornetStatus_t error);

/**
 * \brief Resets the distributed MPI parallelization configuration.
 *
 * \details This function accepts a user-provided MPI communicator in a type-erased form
 * and stores a copy of it inside the cuTensorNet library handle. The provided MPI communicator
 * must be explicitly created by calling MPI_Comm_dup (please see the MPI specification).
 * The subsequent calls to the contraction path finder, contraction plan autotuning, and
 * contraction execution will be parallelized across all MPI processes in the provided
 * MPI communicator. The provided MPI communicator is owned by the user, it should stay
 * alive until the next reset call with a different MPI communicator. If NULL is provided
 * as the pointer to the MPI communicator, no parallelization will be applied to the above
 * mentioned procedures such that those procedures will execute redundantly across all MPI
 * processes. As an example, please refer to the tensornet_example_mpi_auto.cu sample.
 *
 * To enable distributed parallelism, cuTensorNet requires users to set an environment variable
 * \p \$CUTENSORNET_COMM_LIB containing the path to a shared library wrapping the communication
 * primitives. For MPI users, we ship a wrapper source file \p cutensornet_distributed_interface_mpi.c
 * that can be compiled against the target MPI library using the build script provided in the same
 * folder inside the tar archive distribution. cuTensorNet will use the included function
 * pointers to perform inter-process communication using the chosen MPI library.
 *
 * \warning This is a collective call that must be executed by all MPI processes.
 * Note that one can still provide different (non-NULL) MPI communicators to different
 * subgroups of MPI processes (to create concurrent cuTensorNet distributed subgroups).
 *
 * \warning The provided MPI communicator must not be used by more than one
 * cuTensorNet library handle. This is automatically ensured by using MPI_Comm_dup.
 *
 * \warning The current library implementation assumes one GPU instance per MPI rank
 * since the cutensornet library handle is associated with a single GPU instance.
 * In case of multiple GPUs per node, each MPI process running on the same node
 * may still see all GPU devices if CUDA_VISIBLE_DEVICES was not set to provide an exclusive
 * access to each GPU. In such a case, the cutensornet library runtime will assign
 * GPU #(processRank % numVisibleDevices), where processRank is the rank of the current
 * process in its MPI communicator, and numVisibleDevices is the number of GPU devices
 * visible to the current MPI process. The assigned GPU must coincide with the one
 * associated with the cutensornet library handle, otherwise resulting in an error.
 * To ensure consistency, the user must call cudaSetDevice in each MPI process to
 * select the correct GPU device prior to creating a cutensornet library handle.
 *
 * \warning It is user's responsibility to ensure that each MPI process in each provided
 * MPI communicator executes exactly the same sequence of cutensornet API calls, which
 * otherwise will result in an undefined behavior.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] commPtr A pointer to the provided MPI communicator created by MPI_Comm_dup.
 * \param[in] commSize The size of the provided MPI communicator: sizeof(MPI_Comm).
 */
cutensornetStatus_t cutensornetDistributedResetConfiguration(
    cutensornetHandle_t handle,
    const void *commPtr,
    size_t commSize);

/**
 * \brief Queries the number of MPI ranks in the current distributed MPI configuration.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[out] numRanks Number of MPI ranks in the current distributed MPI configuration.
 * \warning The number of ranks corresponds to the MPI communicator used by the current
 * MPI process. If different subgroups of MPI processes used different MPI communicators,
 * the reported number will refer to their specific MPI communicators.
 */
cutensornetStatus_t cutensornetDistributedGetNumRanks(
    const cutensornetHandle_t handle,
    int32_t *numRanks);

/**
 * \brief Queries the rank of the current MPI process in the current distributed MPI configuration.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[out] procRank Rank of the current MPI process in the current distributed MPI configuration.
 * \warning The MPI process rank corresponds to the MPI communicator used by that MPI process.
 * If different subgroups of MPI processes used different MPI communicators, the reported number
 * will refer to their specific MPI communicators.
 */
cutensornetStatus_t cutensornetDistributedGetProcRank(
    const cutensornetHandle_t handle,
    int32_t *procRank);

/**
 * \brief Globally synchronizes all MPI processes in the current distributed MPI configuration,
 * ensuring that all preceding cutensornet API calls have completed across all MPI processes.
 * \warning This is a collective call that must be executed by all MPI processes.
 * \warning Prior to performing the global synchronization, the user is still required
 * to synchronize GPU operations locally (via CUDA stream synchronization).
 * \param[in] handle cuTensorNet library handle.
 */
cutensornetStatus_t cutensornetDistributedSynchronize(
    const cutensornetHandle_t handle);

/**
 * \brief Creates an empty tensor network state of a given shape
 * defined by the number of primary tensor modes and their extents.
 *
 * \details A tensor network state is a tensor representing the result
 * of a full contraction of some (yet unspecified) tensor network. That is,
 * a tensor network state is simply a tensor living in a given primary tensor
 * space constructed as a direct product of a given number of vector spaces
 * which are specified by their dimensions (each vector space represents a state mode).
 * A tensor network state (state tensor) can be either pure or mixed. A pure state
 * tensor resides in the defining primary direct-product space and is represented by
 * a tensor from that space. A mixed tensor network state (state tensor) resides
 * in the direct-product space formed by the defining primary direct-product space
 * tensored with its dual (conjugate) tensor space. A mixed state tensor is a tensor
 * with twice more modes, namely, the modes from the defining primary direct-product space,
 * followed by the same number of modes from its dual (conjugate) space. Subsequently,
 * the initial (empty) vacuum tensor state can be evolved into the final target tensor state
 * by applying user-defined tensor operators (e.g., quantum gates) via cutensornetStateApplyTensorOperator().
 * By default, the final target tensor state is formally represented by a single output tensor,
 * the result of the full tensor network contraction (it does not have to be explicitly computed).
 * However, the user may choose to impose a certain tensor factorization on the final tensor state
 * via the cutensornetStateFinalizeXXX() call, where the supported tensor factorizations (XXX) are:
 * MPS (Matrix Product State). In this case, the final tensor state, which now has to be computed
 * explicitly, will be represented by a tuple of output tensors according to the chosen factorization
 * scheme. The information on the output tensor(s) can be queried by calling cutensornetGetOutputStateDetails().
 *
 * \note To give a concrete example, a pure state tensor of any quantum circuit with
 * 4 qubits has the shape [2,2,2,2] (quantum circuit is a specific kind of tensor network).
 * A mixed state tensor in this case will have the shape [2,2,2,2, 2,2,2,2] corresponding
 * to the density matrix of the 4-qubit register, although there are still only 4 defining
 * modes associated with the primary direct-product space of 4 qubits in this case
 * (direct product of 4 vector spaces of dimension 2). That is, a mixed state tensor contains
 * two sets of modes, one from the primary direct-product space and one from its dual space,
 * but it is still defined by the modes of the primary direct-product space, specifically,
 * by a tuple of dimensions of the constituting vector spaces (2-dimensional vector spaces
 * in case of qubits). For clarity, we will refer to the modes of the primary direct-product
 * tensor space as State Modes. Subsequent actions of quantum gates on the tensor network
 * state via calls to cutensornetStateAppyTensor() can now be conveniently specified
 * via subsets of the state modes acted on by the quantum gate.
 *
 * \warning The current cuTensorNet library release only supports pure tensor network states
 * and provides the MPS factorization as a preview feature.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] purity Desired purity of the tensor network state (pure or mixed).
 * \param[in] numStateModes Number of the defining state modes, irrespective of state purity.
 * Note that both pure and mixed tensor network states are defined solely by the modes
 * of the primary direct-product space.
 * \param[in] stateModeExtents Pointer to the extents of the defining state modes
 * (dimensions of the vector spaces constituting the primary direct-product space).
 * \param[in] dataType Data type of the state tensor.
 * \param[out] tensorNetworkState Tensor network state (empty at this point, aka vacuum).
 */
cutensornetStatus_t cutensornetCreateState(const cutensornetHandle_t handle,
                                           cutensornetStatePurity_t purity,
                                           int32_t numStateModes,
                                           const int64_t *stateModeExtents,
                                           cudaDataType_t dataType,
                                           cutensornetState_t *tensorNetworkState);

/**
 * \brief DEPRECATED: Applies a tensor operator to the tensor network state.
 *
 * \details A tensor operator acts on a specified subset of the tensor state modes,
 * where the number of state modes acted upon defines its rank. A tensor operator
 * is represented by a tensor with twice more modes than the number of state modes
 * it acts on, where the first half of the tensor operator modes is contracted with
 * the state modes of the input state tensor while the second half of the tensor operator
 * modes forms the output state tensor modes. Since the default tensor storage strides
 * follow the generalized columnwise layout, the action of a rank-2 tensor operator G
 * on a rank-2 state tensor Q0 can be expressed symbolically as:
 * Q1(i1,i0) = Q0(j1,j0) * G(j1,j0,i1,i0),
 * which is simply the reversed form of the standard notation:
 * Q1(i0,i1) = G(i0,i1,j0,j1) * Q0(j0,j1),
 * given that a graphical representation of tensor circuits traditionally
 * applies tensor operators (gates) from left to right.
 * In this way, we conveniently ensure the standard row-following initialization
 * of the tensor operator (gate) when using the C-language array initialization syntax.
 * In the above example, tensor operator (gate) G has four modes and acts on two state modes.
 *
 * \note For the purpose of quantum circuit definition, our current convention conveniently
 * allows initialization of a 2-qubit CNOT gate (tensor operator) with a C array with elements
 * precisely following the canonical textbook (row-following) definition of the CNOT gate:
 * \f[
 *   \begin{pmatrix}
 *     1 & 0 & 0 & 0 \\
 *     0 & 1 & 0 & 0 \\
 *     0 & 0 & 0 & 1 \\
 *     0 & 0 & 1 & 0
 *   \end{pmatrix}
 * \f]
 *
 * \warning The pointer to the tensor operator elements is owned by the user
 * and it must stay valid for the whole lifetime of the tensor network state,
 * unless explicitly replaced by another pointer via `cutensornetStateUpdateTensorOperator`.
 *
 * \note In case the tensor operator elements change their value while
 * still residing at the same storage location, one must still call
 * `cutensornetStateUpdateTensorOperator` to register such a change
 * with the same pointer (storage location).
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkState Tensor network state.
 * \param[in] numStateModes Number of state modes the tensor operator acts on.
 * \param[in] stateModes Pointer to the state modes the tensor operator acts on.
 * \param[in] tensorData Elements of the tensor operator (must be of the same data type
 * as the elements of the state tensor).
 * \param[in] tensorModeStrides Strides of the tensor operator data layout (note that
 * the tensor operator has twice more modes than the number of state modes it acts on).
 * Passing NULL will assume the default generalized columnwise layout.
 * \param[in] immutable Whether or not the tensor operator data may change during
 * the lifetime of the tensor network state. Any data change must be registered
 * via a call to `cutensornetStateUpdateTensorOperator`.
 * \param[in] adjoint Whether or not the tensor operator is applied as an adjoint
 * (ket and bra modes reversed, with all tensor elements complex conjugated).
 * \param[in] unitary Whether or not the tensor operator is unitary with respect
 * to the first and second halves of its modes.
 * \param[out] tensorId Unique integer id (for later identification of the tensor operator).
 */
CUTENSORNET_DEPRECATED(cutensornetStateApplyTensorOperator)
cutensornetStatus_t cutensornetStateApplyTensor(const cutensornetHandle_t handle,
                                                cutensornetState_t tensorNetworkState,
                                                int32_t numStateModes,
                                                const int32_t *stateModes,
                                                void *tensorData,
                                                const int64_t *tensorModeStrides,
                                                const int32_t immutable,
                                                const int32_t adjoint,
                                                const int32_t unitary,
                                                int64_t *tensorId);

/**
 * \brief Applies a tensor operator to the tensor network state.
 *
 * \details A tensor operator acts on a specified subset of the tensor state modes,
 * where the number of state modes acted upon defines its rank. A tensor operator
 * is represented by a tensor with twice more modes than the number of state modes
 * it acts on, where the first half of the tensor operator modes is contracted with
 * the state modes of the input state tensor while the second half of the tensor operator
 * modes forms the output state tensor modes. Since the default tensor storage strides
 * follow the generalized columnwise layout, the action of a rank-2 tensor operator G
 * on a rank-2 state tensor Q0 can be expressed symbolically as:
 * Q1(i1,i0) = Q0(j1,j0) * G(j1,j0,i1,i0),
 * which is simply the reversed form of the standard notation:
 * Q1(i0,i1) = G(i0,i1,j0,j1) * Q0(j0,j1),
 * given that a graphical representation of tensor circuits traditionally
 * applies tensor operators (gates) from left to right.
 * In this way, we conveniently ensure the standard row-following initialization
 * of the tensor operator (gate) when using the C-language array initialization syntax.
 * In the above example, tensor operator (gate) G has four modes and acts on two state modes.
 *
 * \note For the purpose of quantum circuit definition, our current convention conveniently
 * allows initialization of a 2-qubit CNOT gate (tensor operator) with a C array with elements
 * precisely following the canonical textbook (row-following) definition of the CNOT gate:
 * \f[
 *   \begin{pmatrix}
 *     1 & 0 & 0 & 0 \\
 *     0 & 1 & 0 & 0 \\
 *     0 & 0 & 0 & 1 \\
 *     0 & 0 & 1 & 0
 *   \end{pmatrix}
 * \f]
 *
 * \warning The pointer to the tensor operator elements is owned by the user
 * and it must stay valid for the whole lifetime of the tensor network state,
 * unless explicitly replaced by another pointer via `cutensornetStateUpdateTensorOperator`.
 *
 * \note In case the tensor operator elements change their value while
 * still residing at the same storage location, one must still call
 * `cutensornetStateUpdateTensorOperator` to register such a change
 * with the same pointer (storage location).
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkState Tensor network state.
 * \param[in] numStateModes Number of state modes the tensor operator acts on.
 * \param[in] stateModes Pointer to the state modes the tensor operator acts on.
 * \param[in] tensorData Elements of the tensor operator (must be of the same data type
 * as the elements of the state tensor).
 * \param[in] tensorModeStrides Strides of the tensor operator data layout (note that
 * the tensor operator has twice more modes than the number of state modes it acts on).
 * Passing NULL will assume the default generalized columnwise storage layout.
 * \param[in] immutable Whether or not the tensor operator data may change during
 * the lifetime of the tensor network state. Any data change must be registered
 * via a call to `cutensornetStateUpdateTensorOperator`.
 * \param[in] adjoint Whether or not the tensor operator is applied as an adjoint
 * (ket and bra modes reversed, with all tensor elements complex conjugated).
 * \param[in] unitary Whether or not the tensor operator is unitary with respect
 * to the first and second halves of its modes.
 * \param[out] tensorId Unique integer id (for later identification of the tensor operator).
 */
cutensornetStatus_t cutensornetStateApplyTensorOperator(const cutensornetHandle_t handle,
                                                        cutensornetState_t tensorNetworkState,
                                                        int32_t numStateModes,
                                                        const int32_t *stateModes,
                                                        void *tensorData,
                                                        const int64_t *tensorModeStrides,
                                                        const int32_t immutable,
                                                        const int32_t adjoint,
                                                        const int32_t unitary,
                                                        int64_t *tensorId);

/**
 * \brief Applies a controlled tensor operator to the tensor network state.
 *
 * \details This API function performs the same operation as `cutensornetStateApplyTensorOperator`
 * except that the tensor operator is specified via the control-target representation
 * typical for multi-qubit quantum gates. Namely, only the target tensor of the full
 * controlled tensor operator needs to be provided here (the number of modes in the provided
 * target tensor is twice the number of the target state modes it acts on). The full tensor
 * operator representation will be automatically generated from the target tensor
 * and the list of control state modes/values.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkState Tensor network state.
 * \param numControlModes Number of control state modes used by the tensor operator.
 * \param stateControlModes Controlling state modes used by the tensor operator.
 * \param stateControlValues Control values for the controlling state modes.
 * A control value is the sequential integer id of the qudit basis component
 * which activates the action of the target tensor operator. If NULL, all control values
 * are assumed to be set to the max id (last qudit basis component), which will be 1 for qubits.
 * \param numTargetModes Number of target state modes acted on by the tensor operator.
 * \param stateTargetModes Target state modes acted on by the tensor operator.
 * \param[in] tensorData Elements of the target tensor of the controlled tensor operator
 * (must be of the same data type as the elements of the state tensor).
 * \param[in] tensorModeStrides Strides of the tensor operator data layout (note that
 * the tensor operator has twice more modes than the number of the target state modes it acts on).
 * Passing NULL will assume the default generalized columnwise storage layout.
 * \param[in] immutable Whether or not the tensor operator data may change during
 * the lifetime of the tensor network state. Any data change must be registered
 * via a call to `cutensornetStateUpdateTensorOperator`.
 * \param[in] adjoint Whether or not the tensor operator is applied as an adjoint
 * (ket and bra modes reversed, with all tensor elements complex conjugated).
 * \param[in] unitary Whether or not the controlled tensor operator is unitary with respect
 * to the first and second halves of its modes.
 * \param[out] tensorId Unique integer id (for later identification of the tensor operator).
 *
 */
cutensornetStatus_t cutensornetStateApplyControlledTensorOperator(const cutensornetHandle_t handle,
                                                                  cutensornetState_t tensorNetworkState,
                                                                  int32_t numControlModes,
                                                                  const int32_t *stateControlModes,
                                                                  const int64_t *stateControlValues,
                                                                  int32_t numTargetModes,
                                                                  const int32_t *stateTargetModes,
                                                                  void *tensorData,
                                                                  const int64_t *tensorModeStrides,
                                                                  const int32_t immutable,
                                                                  const int32_t adjoint,
                                                                  const int32_t unitary,
                                                                  int64_t *tensorId);

/**
 * \brief Registers an external update of the elements of the specified
 * tensor operator that was previously applied to the tensor network state.
 *
 * \note The provided pointer to the tensor elements location may or may not
 * coincide with the originally used pointer. However, the originally provided
 * strides of the tensor operator data layout are assumed applicable to the updated
 * tensor operator data location, that is, one cannot change the storage strides
 * during the tensor operator data update.
 *
 * \warning The pointer to the tensor operator elements is owned by the user
 * and it must stay valid for the whole lifetime of the tensor network state,
 * unless explicitly replaced by another pointer via `cutensornetStateUpdateTensorOperator`.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkState Tensor network state.
 * \param[in] tensorId Tensor id assigned during the `cutensornetStateApplyTensorOperator` call.
 * \param[in] tensorData Pointer to the updated elements of the tensor operator (tensor operator
 * elements must be of the same type as the state tensor).
 * \param[in] unitary Whether or not the tensor operator is unitary with respect
 * to the first and second halves of its modes. This parameter is not applicable
 * to the tensors that are part of a matrix product operator (MPO).
 */
CUTENSORNET_DEPRECATED(cutensornetStateUpdateTensorOperator)
cutensornetStatus_t cutensornetStateUpdateTensor(const cutensornetHandle_t handle,
                                                 cutensornetState_t tensorNetworkState,
                                                 int64_t tensorId,
                                                 void *tensorData,
                                                 int32_t unitary);

/**
 * \brief Registers an external update of the elements of the specified
 * tensor operator that was previously applied to the tensor network state.
 *
 * \note The provided pointer to the tensor elements location may or may not
 * coincide with the originally used pointer. However, the originally provided
 * strides of the tensor operator data layout are assumed applicable to the updated
 * tensor operator data location, that is, one cannot change the storage strides
 * during the tensor operator data update.
 *
 * \warning The pointer to the tensor operator elements is owned by the user
 * and it must stay valid for the whole lifetime of the tensor network state,
 * unless explicitly replaced by another pointer via `cutensornetStateUpdateTensorOperator`.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkState Tensor network state.
 * \param[in] tensorId Tensor id assigned during the `cutensornetStateApplyTensorOperator` call.
 * \param[in] tensorData Pointer to the updated elements of the tensor operator (tensor operator
 * elements must be of the same type as the state tensor).
 * \param[in] unitary Whether or not the tensor operator is unitary with respect
 * to the first and second halves of its modes. This parameter is not applicable
 * to the tensors that are part of a matrix product operator (MPO).
 */
cutensornetStatus_t cutensornetStateUpdateTensorOperator(const cutensornetHandle_t handle,
                                                         cutensornetState_t tensorNetworkState,
                                                         int64_t tensorId,
                                                         void *tensorData,
                                                         int32_t unitary);

/**
 * \brief Applies a tensor network operator to a tensor network state.
 *
 * \note Currently the applied tensor network operators are restricted to
 * those containing only one component (either a tensor product or an MPO).
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkState Tensor network state.
 * \param[in] tensorNetworkOperator Tensor network operator containg only a single component.
 * \param[in] immutable Whether or not the tensor network operator data may change during
 * the lifetime of the tensor network state.
 * \param[in] adjoint Whether or not the tensor network operator is applied as an adjoint.
 * \param[in] unitary Whether or not the tensor network operator is unitary with respect
 * to the first and second halves of its modes.
 * \param[out] operatorId Unique integer id (for later identification of the tensor network operator).
 *
 * \note The returned unique integer id (operatorId) defines the beginning of a contiguous
 * range of unique integer ids associated with the tensors constituting the sole component
 * of the tensor network operator: [operatorId..(operatorId + N - 1)], where N is the number
 * of tensors constituting the sole component of the tensor network operator. The tensor ids
 * from this contiguous range can then be used for registering updates on the corresponding
 * tensors via ``cutensornetStateUpdateTensorOperator``.
 *
 * \warning In the current release, only immutable tensor network operators are supported.
 * This restriction may be lifted in future.
 */
cutensornetStatus_t cutensornetStateApplyNetworkOperator(const cutensornetHandle_t handle,
                                                         cutensornetState_t tensorNetworkState,
                                                         const cutensornetNetworkOperator_t tensorNetworkOperator,
                                                         const int32_t immutable,
                                                         const int32_t adjoint,
                                                         const int32_t unitary,
                                                         int64_t *operatorId);

/**
 * \brief Applies a tensor channel consisting of one or more unitary
 * tensor operators to the tensor network state.
 *
 * \details A tensor channel is a completely positive trace-preserving
 * linear map represented by one or more tensor operators. A unitary
 * tensor channel solely consists of unitary tensor operators.
 * All constituting tensor operators have twice more modes
 * than the number of state modes they act on, as usually.
 *
 * \note The storage layout of all constituting tensor operators
 * must be the same, represented by a single `tensorModeStrides` argument.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkState Tensor network state.
 * \param[in] numStateModes Number of state modes the tensor channel acts on.
 * \param[in] stateModes Pointer to the state modes the tensor channel acts on.
 * \param[in] numTensors Number of constituting tensor operators defining the tensor channel.
 * \param[in] tensorData Elements of the tensor operators constituting the tensor
 * channel (must be of the same data type as the elements of the state tensor).
 * \param[in] tensorModeStrides Strides of the tensor data storage layout (note that
 * the supplied tensors have twice more modes than the number of state modes they act on).
 * Passing NULL will assume the default generalized columnwise storage layout.
 * \param[in] probabilities Probabilities associated with the individual tensor operators.
 * \param[out] channelId Unique integer id (for later identification of the tensor channel).
 * \return cutensornetStatus_t 
 */
cutensornetStatus_t cutensornetStateApplyUnitaryChannel(const cutensornetHandle_t handle,
                                                        cutensornetState_t tensorNetworkState,
                                                        int32_t numStateModes,
                                                        const int32_t *stateModes,
                                                        int32_t numTensors,
                                                        void *tensorData[],
                                                        const int64_t *tensorModeStrides,
                                                        const double probabilities[],
                                                        int64_t *channelId);

/**
 * \brief Applies a tensor channel consisting of one or more
 * gneral Kraus operators to the tensor network state.
 *
 * \details A tensor channel is a completely positive trace-preserving linear
 * map represented by one or more tensor operators.  All constituting tensor
 * operators have twice more modes than the number of state modes they act on,
 * as usually. For a general Kraus operator \f$K_i\f$, the action of the noise
 * channel on state \f$\rho\f$ is simulated as applying the operator
 * \f$\frac{1}{\sqrt{p_i}} K_i\f$ with probability \f$p_i = \text{Tr}(K_i \rho K_i^\dagger)\f$,
 * preserving the norm of the state.
 *
 * \note
 * - This API requires the input channel in \p tensorData to be trace-preserving.
 *   Supplying a non-trace-preserving channel may lead to unexpected results.
 * 
 * - The storage layout of all constituting tensor operators
 *   must be the same, represented by a single `tensorModeStrides` argument.
 * 
 * - As of cuTensorNet v2.7.0, this API only supports MPS simulation with `CUTENSORNET_STATE_CONFIG_MPS_GAUGE_OPTION` set to `CUTENSORNET_STATE_MPS_GAUGE_FREE` (default).
 *   Contraction based tensor network simulation and MPS simulation with `CUTENSORNET_STATE_MPS_GAUGE_SIMPLE` are not supported.
 * 
 * - For MPS simulation, the number of state modes must be either 1 or 2.
 * 
 * - The \p channelId cannot be used to update the channel using
 *   `cutensornetStateUpdateTensorOperator`.
 * 
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkState Tensor network state.
 * \param[in] numStateModes Number of state modes the tensor channel acts on.
 * \param[in] stateModes Pointer to the state modes the tensor channel acts on.
 * \param[in] numTensors Number of constituting tensor operators defining the tensor channel.
 * \param[in] tensorData Elements of the tensor operators constituting the tensor
 * channel (must be of the same data type as the elements of the state tensor).
 * \param[in] tensorModeStrides Strides of the tensor data storage layout (note that
 * the supplied tensors have twice more modes than the number of state modes they act on).
 * Passing NULL will assume the default generalized columnwise storage layout.
 * \param[out] channelId Unique integer id (for later identification of the tensor channel).
 * \return cutensornetStatus_t 
 */
cutensornetStatus_t cutensornetStateApplyGeneralChannel(const cutensornetHandle_t handle,
                                                        cutensornetState_t tensorNetworkState,
                                                        int32_t numStateModes,
                                                        const int32_t *stateModes,
                                                        int32_t numTensors,
                                                        void *tensorData[],
                                                        const int64_t *tensorModeStrides,
                                                        int64_t *channelId);

/**
 * \brief Imposes a user-defined MPS (Matrix Product State) factorization
 * on the initial tensor network state with the given shape and data.
 *
 * \note This API function may be called at any time during the lifetime of the tensor network state
 * to modify its initial state. If not called, the initial state will stay in the default vacuum state.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkState Tensor network state.
 * \param[in] boundaryCondition The boundary condition of the chosen MPS representation.
 * \param[in] extentsIn Array of size \p nStateModes specifying the extents of all tensors
 * defining the initial MPS representation. ``extents[i]`` is expected to be consistent
 * with the mode order (shared mode between (i-1)th and i-th MPS tensor, state mode of the i-th MPS tensor,
 * shared mode between i-th and the (i+1)th MPS tensor). For the open boundary condition,
 * the modes of the first tensor get reduced to (state mode, shared mode with the second site)
 * while the modes of the last tensor become (shared mode with the second to the last site, state mode).
 * \param[in] stridesIn Array of size \p nStateModes specifying the strides of all tensors
 * in the chosen MPS representation. Similar to \p extentsIn, \p stridesIn is also expected
 * to be consistent with the mode order of each MPS tensor. If NULL, the default generalized
 * column-major strides will be assumed.
 * \param[in] stateTensorsIn Array of size \p nStateModes specifying the data for all tensors defining
 * the chosen MPS representation. If NULL, the initial MPS-factorized state will represent the vacuum state.
 */
cutensornetStatus_t cutensornetStateInitializeMPS(const cutensornetHandle_t handle,
                                                  cutensornetState_t tensorNetworkState,
                                                  cutensornetBoundaryCondition_t boundaryCondition,
                                                  const int64_t* const extentsIn[],
                                                  const int64_t* const stridesIn[],
                                                  void* stateTensorsIn[]);

/**
 * \brief Imposes a user-defined MPS (Matrix Product State) factorization
 * on the final tensor network state with the given shape.
 *
 * \details By calling this API function, only the desired target tensor network state
 * representation (MPS representation) is specified without actual computation. Tensors
 * constituting the original tensor network state may still be updated with new data after
 * this API function call. The actual MPS factorization of the tensor network state will be
 * computed after calling `cutensornetStatePrepare` and `cutensornetStateCompute` API functions,
 * following this `cutensornetStateFinalizeMPS` call.
 *
 * \note The current MPS factorization feature is provided as a preview, with more
 * optimizations and enhanced functionality coming up in future releases. In the current
 * release, the primary goal of this feature is to facilitate implementation of the MPS
 * compression of tensor network states via a convenient high-level interface, targeting
 * a broader community of users interested in adding MPS algorithms to their simulators.
 *
 * \warning The current cuTensorNet library release supports MPS factorization of tensor network
 * states with two-dimensional state modes only (qubits only, using the quantum computing language).
 *
 * \warning In the current release, the MPS factorization does not benefit from distributed execution.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkState Tensor network state.
 * \param[in] boundaryCondition The boundary condition of the target MPS representation.
 * \param[in] extentsOut Array of size \p nStateModes specifying the maximal extents of all tensors
 * defining the target MPS representation. ``extentsOut[i]`` is expected to be consistent with the mode order
 * (shared mode between (i-1)th and i-th MPS tensor, state mode of the i-th MPS tensor,
 * shared mode between i-th and (i+1)th MPS tensor). For the open boundary condition, the modes for the first
 * tensor get reduced to (state mode, shared mode with the second site) while the modes for the last tensor become
 * (shared mode with the second last site, state mode).
 * \param[in] stridesOut Array of size \p nStateModes specifying the strides of all tensors defining
 * the target MPS representation. Similar to \p extentsOut, \p stridesOut is also expected to be consistent
 * with the mode order of each MPS tensor. If NULL, the default generalized column-major strides will be assumed.
 *
 * \note \p extentsOut can be used to specify the extent truncation for the shared bond between adjacent MPS tensors.
 *
 * \note As of cuTensorNet v2.7.0, this API does not support MPS simulation when the number of state modes is equal to 1.
 * Please use contraction based tensor network method for the simulation.
 * 
 * \warning If value-based SVD truncation is specified in CUTENSORNET_STATE_MPS_SVD_CONFIG,
 * \p extentsOut and \p stridesOut may not be respected during execution (e.g., in cutensornetStateCompute()).
 * In such cases, users can query runtime values of \p extentsOut and \p stridesOut in cutensornetStateCompute()
 * by providing valid pointers.
 * 
 * \warning As of current version, if \p tensorNetworkState has different extents on different modes, exact MPS factorization can not be computed 
 * if there are operators acting on two non-adjacent modes.
 */
cutensornetStatus_t cutensornetStateFinalizeMPS(const cutensornetHandle_t handle,
                                                cutensornetState_t tensorNetworkState,
                                                cutensornetBoundaryCondition_t boundaryCondition,
                                                const int64_t *const extentsOut[],
                                                const int64_t *const stridesOut[]);

/**
 * \brief Resets the tensor network state to the MPS state previously computed via `cutensornetStateCompute`
 *
 * \details By calling this API function, all tensor operators and tensor network operators
 * that have been applied to the state will be deleted. The new initial state will be reset
 * to the previously computed MPS state specified via a `cutensornetStateFinalizeMPS` call
 * and computed via a `cutensornetStateCompute` call. The MPS simulation settings that have been
 * specified via `cutensornetStateConfigure` and `cutensornetStateFinalizeMPS` will remain.
 *
 * \warning The deleted tensor operators and tensor network operators will no longer
 * be accessible via their integer Ids. The subsequent tensor operators and tensor network
 * operators will have new unique integer Ids which will not overlap with the old ones.
 *
 * \note This hepler API is equivalent to creating a `cutensornetState_t` with the previous
 * output MPS state as the initial MPS state while maintaining the same MPS simulation settings
 * and extents/strides of the output MPS tensors.
 * 
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkState Tensor network state.
 */
cutensornetStatus_t cutensornetStateCaptureMPS(const cutensornetHandle_t handle,
                                               cutensornetState_t tensorNetworkState);

/**
 * \brief Configures computation of the full tensor network state, either
 * in the exact or a factorized form.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkState Tensor network state.
 * \param[in] attribute Configuration attribute.
 * \param[in] attributeValue Pointer to the configuration attribute value (type-erased).
 * \param[in] attributeSize The size of the configuration attribute value.
 */
cutensornetStatus_t cutensornetStateConfigure(const cutensornetHandle_t handle,
                                              cutensornetState_t tensorNetworkState,
                                              cutensornetStateAttributes_t attribute,
                                              const void *attributeValue,
                                              size_t attributeSize);

/**
 * \brief Prepares computation of the full tensor network state, either
 * in the exact or a factorized form.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkState Tensor network state.
 * \param[in] maxWorkspaceSizeDevice Upper limit on the amount of available GPU scratch memory (bytes).
 * \param[out] workDesc Workspace descriptor (the required scratch/cache memory sizes will be set).
 * \param[in] cudaStream CUDA stream.
 *
 * \warning The cudaStream argument is unused in the current release (can be set to 0x0).
 */
cutensornetStatus_t cutensornetStatePrepare(const cutensornetHandle_t handle,
                                            cutensornetState_t tensorNetworkState,
                                            size_t maxWorkspaceSizeDevice,
                                            cutensornetWorkspaceDescriptor_t workDesc,
                                            cudaStream_t cudaStream);

/**
 * \brief Retrieves an attribute related to computation
 * of the full tensor network state, either in the exact or a factorized form.
 *
 * \note The Flop count INFO attribute may not always be available,
 * in which case the returned value will be zero.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkState Tensor network state.
 * \param[in] attribute Information attribute.
 * \param[out] attributeValue Pointer to the information attribute value (type-erased).
 * \param[in] attributeSize The size of the information attribute value.
 */
cutensornetStatus_t cutensornetStateGetInfo(const cutensornetHandle_t handle,
                                            const cutensornetState_t tensorNetworkState,
                                            cutensornetStateAttributes_t attribute,
                                            void *attributeValue,
                                            size_t attributeSize);

/**
 * \brief Performs the actual computation of the full tensor network state, either
 * in the exact or a factorized form.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkState Tensor network state.
 * \param[in] workDesc Workspace descriptor (the required scratch/cache memory buffers must be set by the user).
 * \param[out] extentsOut If not NULL, will hold the extents of all tensors defining the output state representation.
 * Optionally, it can be NULL if this data is not needed.
 * \param[out] stridesOut If not NULL, will hold the strides for all tensors defining the output state representation.
 * Optionally, it can be NULL if this data is not needed.
 * \param[in,out] stateTensorsOut An array of pointers to GPU storage for all tensors defining the output state representation.
 * \param[in] cudaStream CUDA stream.
 *
 * \note The length of \p extentsOut, \p stridesOut, and \p stateTensorsOut should correspond
 * to the final target state MPS representation. For instance, if the final target state is factorized as
 * an MPS with open boundary conditions, \p stateTensorsOut is expected to be an array of \p numStateModes pointers
 * and the buffer sizes for all ``stateTensorsOut[i]`` are expected to be consistent with the target extents
 * specified in the cutensornetStateFinalizeMPS() call prior to the state computation.
 * If no factorization is requested for the tensor network state, the shape and strides
 * of a single full output state tensor, which is computed in this API call, will be returned.
 *
 * \warning The provided workspace descriptor \p workDesc must have the Device Scratch buffer
 * set explicitly since user-provided memory pools are not supported in the current release.
 * Additionally, the attached workspace buffer must be 256-byte aligned in the current release.
 */
cutensornetStatus_t cutensornetStateCompute(const cutensornetHandle_t handle,
                                            cutensornetState_t tensorNetworkState,
                                            cutensornetWorkspaceDescriptor_t workDesc,
                                            int64_t *extentsOut[],
                                            int64_t *stridesOut[],
                                            void *stateTensorsOut[],
                                            cudaStream_t cudaStream);

/**
 * \brief Queries the number of tensors, number of modes, extents,
 * and strides for each of the final output state tensors.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkState Tensor network state.
 * \param[out] numTensorsOut On return, will hold the number of output state tensors (argument cannot be NULL).
 * \param[out] numModesOut If not NULL, will hold the number of modes for each output state tensor. Optionally, can be NULL.
 * \param[out] extentsOut If not NULL, will hold mode extents for each output state tensor. Optionally, can be NULL.
 * \param[out] stridesOut If not NULL, will hold strides for each output state tensor. Optionally, can be NULL.
 *
 * \note If all information regarding the output tensors is needed by the user,
 * this function should be called three times: the first time to retrieve \p numTensorsOut
 * for allocating \p numModesOut, the second time to retrieve \p numModesOut for allocating
 * \p extentsOut and \p stridesOut, and the last time to retrieve \p extentsOut and \p stridesOut.
 *
 * \warning To retrieve \p numTensorsOut and \p numModesOut, it is not necessary to first compute
 * the final target state via the cutensornetStateCompute() call. However, to obtain \p extentsOut
 * and \p stridesOut, cutensornetStateCompute() may need to be called first to compute the output
 * state factorization in case the output state is forced to be factorized (e.g., MPS-factorized).
 */
cutensornetStatus_t cutensornetGetOutputStateDetails(const cutensornetHandle_t handle,
                                                     const cutensornetState_t tensorNetworkState,
                                                     int32_t *numTensorsOut,
                                                     int32_t numModesOut[],
                                                     int64_t *extentsOut[],
                                                     int64_t *stridesOut[]);

/**
 * \brief Frees all resources owned by the tensor network state.
 *
 * \note After the tensor network state is destroyed, all pointers to the tensor
 * operator data used for specifying the final target state may be invalidated.
 *
 * \param[in] tensorNetworkState Tensor network state.
 */
cutensornetStatus_t cutensornetDestroyState(cutensornetState_t tensorNetworkState);

/**
 * \brief Creates an uninitialized tensor network operator of a given shape
 * defined by the number of state modes and their extents.
 *
 * \details A tensor network operator is an operator that maps tensor network states
 * from the primary direct-product space back to the same tensor space. The shape
 * of the tensor network operator is defined by the number of state modes and
 * their extents, which should match the definition of the tensor network states
 * the operator will be acting on. Note that formally the declared tensor network
 * operator will have twice more modes than the number of defining state modes,
 * the first half corresponding to the primary direct-product space it acts on
 * while the second half corresponding to the same primary direct-product space
 * where the resulting tensor network state lives.
 *
 * \note This API defines an abstract uninitialized tensor network operator.
 * Users may later initialize it using some concrete structure by appending components to it.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] numStateModes The number of state modes the operator acts on.
 * \param[in] stateModeExtents An array of size \p numStateModes specifying the extent of each state mode acted on.
 * \param[in] dataType Data type of the operator.
 * \param[out] tensorNetworkOperator Tensor network operator (empty at this point).
 */
cutensornetStatus_t cutensornetCreateNetworkOperator(const cutensornetHandle_t handle,
                                                     int32_t numStateModes,
                                                     const int64_t stateModeExtents[],
                                                     cudaDataType_t dataType,
                                                     cutensornetNetworkOperator_t *tensorNetworkOperator);

/**
 * \brief Appends a tensor product operator component to the tensor network operator.
 *
 * \details A tensor product operator component is defined as a tensor product of one or more tensor operators
 * acting on disjoint subsets of state modes. Note that each tensor operator (tensor factor) in the specified
 * tensor product has twice more modes than the number of state modes it acts on. Specifically, the first half
 * of tensor operator modes will be contracted with the state modes. A typical example would be a tensor
 * product of Pauli matrices in which each Pauli matrix acts on a specific mode of the tensor network state.
 * This API function is used for defining a tensor network operator as a sum over tensor operator products
 * with complex coefficients.
 *
 * \note All user-provided tensors used to define a tensor network operator
 * must stay alive during the entire lifetime of the tensor network operator.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkOperator Tensor network operator.
 * \param[in] coefficient Complex coefficient associated with the appended operator component.
 * \param[in] numTensors Number of tensor factors in the tensor product.
 * \param[in] numStateModes Number of state modes each appended tensor factor acts on.
 * \param[in] stateModes Modes each appended tensor factor acts on (length = ``numStateModes``).
 * \param[in] tensorModeStrides Tensor mode strides for each tensor factor (length = ``numStateModes`` * 2).
 * If NULL, the default generalized column-major strides will be used.
 * \param[in] tensorData Tensor data stored in GPU memory for each tensor factor.
 * \param[out] componentId Unique sequential integer identifier of the appended tensor network operator component.
 */
cutensornetStatus_t cutensornetNetworkOperatorAppendProduct(const cutensornetHandle_t handle,
                                                            cutensornetNetworkOperator_t tensorNetworkOperator,
                                                            cuDoubleComplex coefficient,
                                                            int32_t numTensors,
                                                            const int32_t numStateModes[],
                                                            const int32_t *stateModes[],
                                                            const int64_t *tensorModeStrides[],
                                                            const void *tensorData[],
                                                            int64_t *componentId);

/**
 * \brief Appends a Matrix Product Operator (MPO) component to the tensor network operator.
 *
 * \details The modes of the MPO tensors follow the standard cuTensorNet convention
 * (each internal MPO tensor has four modes):
 *   Mode 0: (i-1)th - (i)th connection;
 *   Mode 1: (i)th site open mode acting on the ket state mode;
 *   Mode 2: (i)th - (i+1)th connection;
 *   Mode 3: (i)th site open mode acting on the bra state mode;
 * When the open boundary condition is requested, the first MPO tensor will have mode 0 removed
 * while the last MPO tensor will have mode 2 removed, both having only three modes (in order).
 *
 * \note All user-provided MPO tensors used to define a tensor network operator
 * must stay alive during the entire lifetime of the tensor network operator.
 * 
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkOperator Tensor network operator.
 * \param[in] coefficient Complex coefficient associated with the appended operator component.
 * \param[in] numStateModes Number of state modes the MPO acts on (number of tensors in the MPO).
 * \param[in] stateModes State modes the MPO acts on.
 * \param[in] tensorModeExtents Tensor mode extents for each MPO tensor.
 * \param[in] tensorModeStrides Storage strides for each MPO tensor or NULL (default generalized column-wise strides).
 * \param[in] tensorData Tensor data stored in GPU memory for each MPO tensor factor.
 * \param[in] boundaryCondition MPO boundary condition.
 * \param[out] componentId Unique sequential integer identifier of the appended tensor network operator component.
 */
cutensornetStatus_t cutensornetNetworkOperatorAppendMPO(const cutensornetHandle_t handle,
                                                        cutensornetNetworkOperator_t tensorNetworkOperator,
                                                        cuDoubleComplex coefficient,
                                                        int32_t numStateModes,
                                                        const int32_t stateModes[],
                                                        const int64_t *tensorModeExtents[],
                                                        const int64_t *tensorModeStrides[],
                                                        const void *tensorData[],
                                                        cutensornetBoundaryCondition_t boundaryCondition,
                                                        int64_t *componentId);

/**
 * \brief Frees all resources owned by the tensor network operator.
 *
 * \param[in,out] tensorNetworkOperator Tensor network operator.
 */
cutensornetStatus_t cutensornetDestroyNetworkOperator(cutensornetNetworkOperator_t tensorNetworkOperator);

/**
 * \brief Creates a tensor network state amplitudes accessor.
 *
 * \details The state amplitudes accessor allows the user to extract
 * single state amplitudes (elements of the state tensor), slices of
 * state amplitudes (slices of the state tensor) as well as the full
 * state tensor. The choice of a specific slices is accomplished by
 * specifying the projected modes of the tensor network state, that is,
 * a subset of the tensor network state modes that will be projected
 * to specific basis vectors during the computation. The rest of the
 * tensor state modes (open modes) in their respective relative order
 * will define the shape of the resulting state amplitudes tensor
 * requested by the user.
 *
 * \note The provided tensor network state must stay alive during
 * the lifetime of the state amplitudes accessor. Additionally,
 * applying a tensor operator to the tensor network state after
 * it was used to create the state amplitudes accessor will
 * invalidate the state amplitudes accessor. On the other hand,
 * simply updating tensor operator data via cutensornetStateUpdateTensorOperator()
 * is allowed.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkState Defined tensor network state.
 * \param[in] numProjectedModes Number of projected state modes (tensor network state modes projected to specific basis vectors).
 * \param[in] projectedModes Projected state modes (may be NULL when none or all modes are projected).
 * \param[in] amplitudesTensorStrides Mode strides for the resulting amplitudes tensor. If NULL,
 * the default generalized column-major strides will be assumed.
 * \param[out] tensorNetworkAccessor Tensor network state amplitudes accessor.
 */
cutensornetStatus_t cutensornetCreateAccessor(const cutensornetHandle_t handle,
                                              cutensornetState_t tensorNetworkState,
                                              int32_t numProjectedModes,
                                              const int32_t *projectedModes,
                                              const int64_t *amplitudesTensorStrides,
                                              cutensornetStateAccessor_t *tensorNetworkAccessor);

/**
 * \brief Configures computation of the requested tensor network state amplitudes tensor.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkAccessor Tensor network state amplitudes accessor.
 * \param[in] attribute Configuration attribute.
 * \param[in] attributeValue Pointer to the configuration attribute value (type-erased).
 * \param[in] attributeSize The size of the configuration attribute value.
 */
cutensornetStatus_t cutensornetAccessorConfigure(const cutensornetHandle_t handle,
                                                 cutensornetStateAccessor_t tensorNetworkAccessor,
                                                 cutensornetAccessorAttributes_t attribute,
                                                 const void *attributeValue,
                                                 size_t attributeSize);

/**
 * \brief Prepares computation of the requested tensor network state amplitudes tensor.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkAccessor Tensor network state amplitudes accessor.
 * \param[in] maxWorkspaceSizeDevice Upper limit on the amount of available GPU scratch memory (bytes).
 * \param[out] workDesc Workspace descriptor (the required scratch/cache memory sizes will be set).
 * \param[in] cudaStream CUDA stream.
 *
 * \warning The cudaStream argument is unused in the current release (can be set to 0x0).
 */
cutensornetStatus_t cutensornetAccessorPrepare(const cutensornetHandle_t handle,
                                               cutensornetStateAccessor_t tensorNetworkAccessor,
                                               size_t maxWorkspaceSizeDevice,
                                               cutensornetWorkspaceDescriptor_t workDesc,
                                               cudaStream_t cudaStream);

/**
 * \brief Retrieves an attribute related to computation
 *  of the requested tensor network state amplitudes tensor.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkAccessor Tensor network state amplitudes accessor.
 * \param[in] attribute Information attribute.
 * \param[out] attributeValue Pointer to the information attribute value (type-erased).
 * \param[in] attributeSize The size of the information attribute value.
 */
cutensornetStatus_t cutensornetAccessorGetInfo(const cutensornetHandle_t handle,
                                               const cutensornetStateAccessor_t tensorNetworkAccessor,
                                               cutensornetAccessorAttributes_t attribute,
                                               void *attributeValue,
                                               size_t attributeSize);

/**
 * \brief Computes the amplitudes of the tensor network state.
 *
 * \note The computed amplitudes are not normalized automatically in cases
 * when the tensor circuit state is not guaranteed to have a unity norm.
 * In such cases, the squared state norm is returned as a separate parameter.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkAccessor Tensor network state amplitudes accessor.
 * \param[in] projectedModeValues The values of the projected state modes or NULL pointer if there are no projected modes.
 * \param[in] workDesc Workspace descriptor (the required scratch/cache memory buffers must be set by the user).
 * \param[in,out] amplitudesTensor Storage for the computed tensor network state amplitudes tensor.
 * \param[out] stateNorm The squared 2-norm of the underlying tensor circuit state (Host pointer). The returned scalar
 * will have the same numerical data type as the tensor circuit state. Providing a NULL pointer will ignore norm calculation.
 * \param[in] cudaStream CUDA stream.
 *
 * \warning The provided workspace descriptor \p workDesc must have the Device Scratch buffer
 * set explicitly since user-provided memory pools are not supported in the current release.
 * Additionally, the attached workspace buffer must be 256-byte aligned in the current release.
 *
 * \warning In the current release, the execution of this API function will synchronize
 * the provided CUDA stream. This restriction may be released in the future.
 */
cutensornetStatus_t cutensornetAccessorCompute(const cutensornetHandle_t handle,
                                               cutensornetStateAccessor_t tensorNetworkAccessor,
                                               const int64_t *projectedModeValues,
                                               cutensornetWorkspaceDescriptor_t workDesc,
                                               void *amplitudesTensor,
                                               void *stateNorm,
                                               cudaStream_t cudaStream);

/**
 * \brief Destroyes the tensor network state amplitudes accessor.
 *
 * \param[in,out] tensorNetworkAccessor Tensor network state amplitudes accessor.
 */
cutensornetStatus_t cutensornetDestroyAccessor(cutensornetStateAccessor_t tensorNetworkAccessor);

/**
 * \brief Creates a representation of the tensor network state expectation value.
 *
 * \details The tensor network state expectation value is the expectation value
 * of the given tensor network operator with respect to the given tensor network
 * state. Note that the computed expectation value is unnormalized, with the norm
 * of the tensor network state returned separately (optionally).
 *
 * \note The provided tensor network state must stay alive during
 * the lifetime of the tensor network state expectation value.
 * Additionally, applying a tensor operator to the tensor network state
 * after it was used to create the tensor network state expectation value
 * will invalidate the tensor network state expectation value. On the other hand,
 * simply updating tensor operator data via cutensornetStateUpdateTensorOperator()
 * is allowed.
 *
 * \note The provided tensor network operator must stay alive during
 * the lifetime of the tensor network state expectation value.
 * Additionally, appending new components to the tensor network operator
 * after it was used to create the tensor network state expectation value
 * will invalidate the tensor network state expectation value. On the other hand,
 * simply updating the tensor data inside the tensor network operator is allowed.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkState Defined tensor network state.
 * \param[in] tensorNetworkOperator Defined tensor network operator.
 * \param[out] tensorNetworkExpectation Tensor network expectation value representation.
 */
cutensornetStatus_t cutensornetCreateExpectation(const cutensornetHandle_t handle,
                                                 cutensornetState_t tensorNetworkState,
                                                 cutensornetNetworkOperator_t tensorNetworkOperator,
                                                 cutensornetStateExpectation_t *tensorNetworkExpectation);

/**
 * \brief Configures computation of the requested tensor network state expectation value.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkExpectation Tensor network state expectation value representation.
 * \param[in] attribute Configuration attribute.
 * \param[in] attributeValue Pointer to the configuration attribute value (type-erased).
 * \param[in] attributeSize The size of the configuration attribute value.
 */
cutensornetStatus_t cutensornetExpectationConfigure(const cutensornetHandle_t handle,
                                                    cutensornetStateExpectation_t tensorNetworkExpectation,
                                                    cutensornetExpectationAttributes_t attribute,
                                                    const void *attributeValue,
                                                    size_t attributeSize);

/**
 * \brief Prepares computation of the requested tensor network state expectation value.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkExpectation Tensor network state expectation value representation.
 * \param[in] maxWorkspaceSizeDevice Upper limit on the amount of available GPU scratch memory (bytes).
 * \param[out] workDesc Workspace descriptor (the required scratch/cache memory sizes will be set).
 * \param[in] cudaStream CUDA stream.
 *
 * \warning The cudaStream argument is unused in the current release (can be set to 0x0).
 */
cutensornetStatus_t cutensornetExpectationPrepare(const cutensornetHandle_t handle,
                                                  cutensornetStateExpectation_t tensorNetworkExpectation,
                                                  size_t maxWorkspaceSizeDevice,
                                                  cutensornetWorkspaceDescriptor_t workDesc,
                                                  cudaStream_t cudaStream);

/**
 * \brief Retrieves an attribute related to computation
 * of the requested tensor network state expectation value.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkExpectation Tensor network state expectation value representation.
 * \param[in] attribute Information attribute.
 * \param[out] attributeValue Pointer to the information attribute value (type-erased).
 * \param[in] attributeSize The size of the information attribute value.
 */
cutensornetStatus_t cutensornetExpectationGetInfo(const cutensornetHandle_t handle,
                                                  const cutensornetStateExpectation_t tensorNetworkExpectation,
                                                  cutensornetExpectationAttributes_t attribute,
                                                  void *attributeValue,
                                                  size_t attributeSize);

/**
 * \brief Computes an (unnormalized) expectation value of a given
 * tensor network operator over a given tensor network state.
 *
 * \note The computed expectation value is not normalized automatically in cases
 * when the tensor network state is not guaranteed to have a unity norm.
 * In such cases, the squared state norm is returned as a separate parameter.
 * The true tensor network state expectation value can then be obtained by dividing
 * the returned unnormalized expectation value by the returned squared state norm.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkExpectation Tensor network state expectation value representation.
 * \param[in] workDesc Workspace descriptor (the required scratch/cache memory buffers must be set by the user).
 * \param[out] expectationValue Computed unnormalized tensor network state expectation value (Host pointer).
 * The returned scalar will have the same numerical data type as the tensor circuit state.
 * \param[out] stateNorm The squared 2-norm of the underlying tensor circuit state (Host pointer). The returned scalar
 *  will have the same numerical data type as the tensor circuit state. Providing a NULL pointer will ignore norm calculation.
 * \param[in] cudaStream CUDA stream.
 *
 * \warning The provided workspace descriptor \p workDesc must have the Device Scratch buffer
 * set explicitly since user-provided memory pools are not supported in the current release.
 * Additionally, the attached workspace buffer must be 256-byte aligned in the current release.
 *
 * \warning In the current release, the execution of this API function will synchronize
 * the provided CUDA stream. This restriction may be released in the future.
 */
cutensornetStatus_t cutensornetExpectationCompute(const cutensornetHandle_t handle,
                                                  cutensornetStateExpectation_t tensorNetworkExpectation,
                                                  cutensornetWorkspaceDescriptor_t workDesc,
                                                  void *expectationValue,
                                                  void *stateNorm,
                                                  cudaStream_t cudaStream);

/**
 * \brief Destroyes the tensor network state expectation value representation.
 *
 * \param[in,out] tensorNetworkExpectation Tensor network state expectation value representation.
 */
cutensornetStatus_t cutensornetDestroyExpectation(cutensornetStateExpectation_t tensorNetworkExpectation);

/**
 * \brief Creates a representation of the specified marginal tensor for a given tensor network state.
 *
 * \details The tensor network state marginal tensor is formed by a direct product
 * of the tensor network state with its dual (conjugated) state, followed by a trace
 * over all state modes except the explicitly specified so-called open state modes.
 * The order of the specified open state modes will be respected when computing
 * the tensor network state marginal tensor. Additionally, prior to tracing, some of the
 * state modes can optionally be projected to specific individual basis states of those modes,
 * thus forming the so-called projected modes which will not be involved in tracing.
 * Note that the resulting marginal tensor will have twice more modes than
 * the number of the specified open modes, first half coming from the primary direct-product
 * space while the second half symmetrically coming from the dual (conjugate) space.
 *
 * \note In the quantum domain, the marginal tensor is known as the reduced density matrix.
 * For example, in quantum circuit simulations, the reduced density matrix is specified
 * by the state modes which are kept intact and the remaining state modes which are traced over.
 * Additionally, prior to tracing, one can project certain qudit modes to specific individual
 * basis states of those modes, resulting in a projected reduced density matrix.
 *
 * \note The provided tensor network state must stay alive during
 * the lifetime of the tensor network state marginal.
 * Additionally, applying a tensor operator to the tensor network state
 * after it was used to create the tensor network state marginal
 * will invalidate the tensor network state marginal. On the other hand,
 * simply updating tensor operator data via cutensornetStateUpdateTensorOperator()
 * is allowed.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkState Tensor network state.
 * \param[in] numMarginalModes Number of open state modes defining the marginal tensor.
 * \param[in] marginalModes Pointer to the open state modes defining the marginal tensor.
 * \param[in] numProjectedModes Number of projected state modes.
 * \param[in] projectedModes Pointer to the projected state modes.
 * \param[in] marginalTensorStrides Storage strides for the marginal tensor (number of tensor
 * modes is twice the number of the defining open modes). If NULL, the defaul generalized
 * column-major strides will be assumed.
 * \param[out] tensorNetworkMarginal Tensor network state marginal.
 */
cutensornetStatus_t cutensornetCreateMarginal(const cutensornetHandle_t handle,
                                              cutensornetState_t tensorNetworkState,
                                              int32_t numMarginalModes,
                                              const int32_t *marginalModes,
                                              int32_t numProjectedModes,
                                              const int32_t *projectedModes,
                                              const int64_t *marginalTensorStrides,
                                              cutensornetStateMarginal_t *tensorNetworkMarginal);

/**
 * \brief Configures computation of the requested tensor network state marginal tensor.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkMarginal Tensor network state marginal representation.
 * \param[in] attribute Configuration attribute.
 * \param[in] attributeValue Pointer to the configuration attribute value (type-erased).
 * \param[in] attributeSize The size of the configuration attribute value.
 */
cutensornetStatus_t cutensornetMarginalConfigure(const cutensornetHandle_t handle,
                                                 cutensornetStateMarginal_t tensorNetworkMarginal,
                                                 cutensornetMarginalAttributes_t attribute,
                                                 const void *attributeValue,
                                                 size_t attributeSize);

/**
 * \brief Prepares computation of the requested tensor network state marginal tensor.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkMarginal Tensor network state marginal representation.
 * \param[in] maxWorkspaceSizeDevice Upper limit on the amount of available GPU scratch memory (bytes).
 * \param[out] workDesc Workspace descriptor (the required scratch/cache memory sizes will be set).
 * \param[in] cudaStream CUDA stream.
 *
 * \warning The cudaStream argument is unused in the current release (can be set to 0x0).
 */
cutensornetStatus_t cutensornetMarginalPrepare(const cutensornetHandle_t handle,
                                               cutensornetStateMarginal_t tensorNetworkMarginal,
                                               size_t maxWorkspaceSizeDevice,
                                               cutensornetWorkspaceDescriptor_t workDesc,
                                               cudaStream_t cudaStream);

/**
 * \brief Retrieves an attribute related to computation
 * of the requested tensor network state marginal tensor.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkMarginal Tensor network state marginal representation.
 * \param[in] attribute Information attribute.
 * \param[out] attributeValue Pointer to the information attribute value (type-erased).
 * \param[in] attributeSize The size of the information attribute value.
 */
cutensornetStatus_t cutensornetMarginalGetInfo(const cutensornetHandle_t handle,
                                               const cutensornetStateMarginal_t tensorNetworkMarginal,
                                               cutensornetMarginalAttributes_t attribute,
                                               void *attributeValue,
                                               size_t attributeSize);

/**
 * \brief Computes the requested tensor network state marginal tensor.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkMarginal Tensor network state marginal representation.
 * \param[in] projectedModeValues Pointer to the values of the projected modes.
 * Each integer value corresponds to a basis state of the given (projected) state mode.
 * \param[in] workDesc Workspace descriptor (the required scratch/cache memory buffers must be set by the user).
 * \param[out] marginalTensor Pointer to the GPU storage of the marginal tensor which will be computed in this call.
 * \param[in] cudaStream CUDA stream.
 *
 * \warning The provided workspace descriptor \p workDesc must have the Device Scratch buffer
 * set explicitly since user-provided memory pools are not supported in the current release.
 * Additionally, the attached workspace buffer must be 256-byte aligned in the current release.
 *
 * \warning In the current release, the execution of this API function will synchronize
 * the provided CUDA stream. This restriction may be released in the future.
 */
cutensornetStatus_t cutensornetMarginalCompute(const cutensornetHandle_t handle,
                                               cutensornetStateMarginal_t tensorNetworkMarginal,
                                               const int64_t *projectedModeValues,
                                               cutensornetWorkspaceDescriptor_t workDesc,
                                               void *marginalTensor,
                                               cudaStream_t cudaStream);

/**
 * \brief Destroys the tensor network state marginal.
 *
 * \param[in] tensorNetworkMarginal Tensor network state marginal representation.
 */
cutensornetStatus_t cutensornetDestroyMarginal(cutensornetStateMarginal_t tensorNetworkMarginal);

/**
 * \brief Creates a tensor network state sampler.
 *
 * \details A tensor network state sampler produces samples from the state tensor
 * with the probability equal to the squared absolute value of the corresponding
 * element of the state tensor. One can also choose any subset of tensor network
 * state modes to sample only from the subspace spanned by them. The order of
 * specified state modes will be respected when producing the output samples.
 *
 * \note For the purpose of quantum circuit simulations, the tensor network state
 * sampler can generate bit-strings (or qudit-strings) from the output state of
 * the defined quantum circuit (i.e., the tensor network defined by gate applications).
 *
 * \note The provided tensor network state must stay alive during
 * the lifetime of the tensor network state sampler.
 * Additionally, applying a tensor operator to the tensor network state
 * after it was used to create the tensor network state sampler
 * will invalidate the tensor network state sampler. On the other hand,
 * simply updating tensor operator data via cutensornetStateUpdateTensorOperator()
 * is allowed.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkState Tensor network state.
 * \param[in] numModesToSample Number of the tensor network state modes to sample from.
 * \param[in] modesToSample Pointer to the state modes to sample from (can be NULL when all modes are requested).
 * \param[out] tensorNetworkSampler Tensor network sampler.
 */
cutensornetStatus_t cutensornetCreateSampler(const cutensornetHandle_t handle,
                                             cutensornetState_t tensorNetworkState,
                                             int32_t numModesToSample,
                                             const int32_t *modesToSample,
                                             cutensornetStateSampler_t *tensorNetworkSampler);

/**
 * \brief Configures the tensor network state sampler.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkSampler Tensor network state sampler.
 * \param[in] attribute Configuration attribute.
 * \param[in] attributeValue Pointer to the configuration attribute value (type-erased).
 * \param[in] attributeSize The size of the configuration attribute value.
 */
cutensornetStatus_t cutensornetSamplerConfigure(const cutensornetHandle_t handle,
                                                cutensornetStateSampler_t tensorNetworkSampler,
                                                cutensornetSamplerAttributes_t attribute,
                                                const void *attributeValue,
                                                size_t attributeSize);

/**
 * \brief Prepares the tensor network state sampler.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkSampler Tensor network state sampler.
 * \param[in] maxWorkspaceSizeDevice Upper limit on the amount of available GPU scratch memory (bytes).
 * \param[out] workDesc Workspace descriptor (the required scratch/cache memory sizes will be set).
 * \param[in] cudaStream CUDA stream.
 *
 * \warning The cudaStream argument is unused in the current release (can be set to 0x0).
 */
cutensornetStatus_t cutensornetSamplerPrepare(const cutensornetHandle_t handle,
                                              cutensornetStateSampler_t tensorNetworkSampler,
                                              size_t maxWorkspaceSizeDevice,
                                              cutensornetWorkspaceDescriptor_t workDesc,
                                              cudaStream_t cudaStream);

/**
 * \brief Retrieves an attribute related to tensor network state sampling.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkSampler Tensor network state sampler.
 * \param[in] attribute Information attribute.
 * \param[out] attributeValue Pointer to the information attribute value (type-erased).
 * \param[in] attributeSize The size of the information attribute value.
 */
cutensornetStatus_t cutensornetSamplerGetInfo(const cutensornetHandle_t handle,
                                              const cutensornetStateSampler_t tensorNetworkSampler,
                                              cutensornetSamplerAttributes_t attribute,
                                              void *attributeValue,
                                              size_t attributeSize);

/**
 * \brief Performs sampling of the tensor network state, that is, generates the requested number of samples.
 *
 * \note The pseudo-random number generator used internally is initialized with a random default seed, thus
 * generally resulting in a different set of samples generated upon each repeated execution. In future,
 * the ability to reset the seed to a user-defined value may be provided, to ensure generation of exactly
 * the same set of samples upon rerunning the application repeatedly (this could be useful for debugging).
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkSampler Tensor network state sampler.
 * \param[in] numShots Number of samples to generate.
 * \param[in] workDesc Workspace descriptor (the required scratch/cache memory buffers must be set by the user).
 * \param[out] samples Host memory pointer where the generated state tensor samples will be stored at.
 * The samples will be stored as samples[SampleId][ModeId] in C notation and the originally specified
 * order of the tensor network state modes to sample from will be respected.
 * \param[in] cudaStream CUDA stream.
 *
 * \warning The provided workspace descriptor \p workDesc must have the Device Scratch buffer
 * set explicitly since user-provided memory pools are not supported in the current release.
 * Additionally, the attached workspace buffer must be 256-byte aligned in the current release.
 *
 * \warning In the current release, the execution of this API function will synchronize
 * the provided CUDA stream. This restriction may be released in the future.
 */
cutensornetStatus_t cutensornetSamplerSample(const cutensornetHandle_t handle,
                                             cutensornetStateSampler_t tensorNetworkSampler,
                                             int64_t numShots,
                                             cutensornetWorkspaceDescriptor_t workDesc,
                                             int64_t *samples,
                                             cudaStream_t cudaStream);

/**
 * \brief Destroys the tensor network state sampler.
 *
 * \param[in] tensorNetworkSampler Tensor network state sampler.
 */
cutensornetStatus_t cutensornetDestroySampler(cutensornetStateSampler_t tensorNetworkSampler);

/**
 * \brief Creates an accumulative matrix product state (MPS) projection of a set of tensor network
 * states.
 *
 * \details A tensor network state MPS projection allows to project a weighted sum of tensor network states
 * into subspaces of an MPS. This API enables, for example, to variationally determine a compressed MPS representation
 * of the weighted sum of tensor network states. The projection is computed by accumulating the contraction of each
 * tensor network state with the dual (conjugated) tensors of the MPS, with the exception of a set of adjacent MPS tensors
 * which are absent from the network to be contracted, referred to as environment in the following.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] numStates Number of tensor network states for which the MPS projection is computed.
 * Currently only a single tensor network state is supported.
 * \param[in] tensorNetworkStates Tensor network states.
 * \param[in] coeffs CPU accessible pointer to scalar coefficients for each tensor network state.
 * If the tensor network states are of real datatype, the complex component of the coefficients will be ignored.
 * A nullptr for this argument will be interpreted as unit coefficient for all network states.
 * \param[in] symmetric Whether or not the initial state of all tensor network states is defined by the
 * values of the dual MPS tensors (in case of a symmetric MPS functional).
 * Note that currently only non-symmetric MPS are supported.
 * \param[in] numEnvs Number of requested environments.
 * \param[in] specEnvs Specification of each requested environment.
 * Environments are specified by providing the qudit indices to the left and right of the
 * excluded MPS tensors. 
 * Note that currently only 1-site environments are supported.
 * \param[in] boundaryCondition Boundary condition of the MPS.
 * Currently only open boundary condition MPS are supported.
 * \param[in] numTensors Number of tensors contained in the MPS.
 * Currently, numTensors must be equal to the number of qudits in the MPS.
 * \param[in] quditsPerTensor Number of consecutive qudits in each MPS tensor.
 * Currently, quditsPerTensor must be equal to 1.
 * A nullptr for this argument will be interpreted as a single qudit per tensor.
 * \param[in] extentsOut Maximum mode extents of all dual MPS output tensors,
 * passed as array of length number of qudits, holding pointer to integer arrays.
 * For pure states all extent arrays are of length 3, with the exception of open boundary condition MPS
 * for which the first and last extent arrays are of length 2.
 * \param[in] stridesOut Strides of all dual MPS output tensors, passed as array of length number of qudits,
 * holding pointer to integer arrays.
 * For pure states all stride arrays are of length 3, with the exception of open boundary condition MPS
 * for which the first and last stride array are of length 2.
 * \param[in,out] dualTensorsDataOut GPU-accessible pointers for storing dual MPS tensors.
 * Note that the MPS tensors residing in these data buffers are not conjugated, and will be
 * conjugated on-the-fly during the environment contraction.
 * cutensornetStateProjectionMPSExtractTensor() and cutensornetStateProjectionMPSInsertTensor() have side effects on the provided data.
 * \param[in] orthoSpec Specification of the orthogonality conditions on the provided MPS tensors.
 * \param[out] tensorNetworkProjection MPS projection of a set of tensor network states.
 * \return cutensornetStatus_t 
 */
cutensornetStatus_t cutensornetCreateStateProjectionMPS(const cutensornetHandle_t handle,
                                                   int32_t numStates,
                                                   const cutensornetState_t tensorNetworkStates[],
                                                   const cuDoubleComplex coeffs[],
                                                   int32_t symmetric,
                                                   int32_t numEnvs,
                                                   const cutensornetMPSEnvBounds_t specEnvs[],
                                                   cutensornetBoundaryCondition_t boundaryCondition,
                                                   int32_t numTensors,
                                                   const int32_t quditsPerTensor[],
                                                   const int64_t *extentsOut[],
                                                   const int64_t *stridesOut[],
                                                   void *dualTensorsDataOut[],
                                                   const cutensornetMPSEnvBounds_t *orthoSpec,
                                                   cutensornetStateProjectionMPS_t *tensorNetworkProjection);

/**
 * \brief Configures computation of the requested tensor network state MPS projection.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkProjection Tensor network state MPS projection.
 * \param[in] attribute Configuration attribute.
 * \param[in] attributeValue Pointer to the configuration attribute value (type-erased).
 * \param[in] attributeSize The size of the configuration attribute value.
 * \return cutensornetStatus_t 
 */
cutensornetStatus_t cutensornetStateProjectionMPSConfigure(const cutensornetHandle_t handle,
                                                      cutensornetStateProjectionMPS_t tensorNetworkProjection,
                                                      cutensornetStateProjectionMPSAttributes_t attribute,
                                                      const void *attributeValue,
                                                      size_t attributeSize);

/**
 * \brief Prepares computation of the requested tensor network state MPS projection.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkProjection Tensor network state MPS projection.
 * \param[in] maxWorkspaceSizeDevice Upper limit on the amount of available GPU scratch memory
 *(bytes).
 * \param[out] workDesc Workspace descriptor (the required scratch/cache memory sizes will be set).
 * \param[in] cudaStream CUDA stream.
 * \return cutensornetStatus_t 
 * 
 * \warning The cudaStream argument is unused in the current release (can be set to 0x0).
 */
cutensornetStatus_t cutensornetStateProjectionMPSPrepare(const cutensornetHandle_t handle,
                                                    cutensornetStateProjectionMPS_t tensorNetworkProjection,
                                                    size_t maxWorkspaceSizeDevice,
                                                    cutensornetWorkspaceDescriptor_t workDesc,
                                                    cudaStream_t cudaStream);

/**
 * \brief Computes the projection for the specified environment.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkProjection Tensor network state MPS projection.
 * \param[in] envSpec Specification of the requested environment.
 * Note that currently only single site environments are supported.
 * \param[in] stridesIn Strides of the provided MPS representation tensor for the specified environment.
 * Required to be a nullptr if MPS projection is symmetric.
 * \param[in] envTensorDataIn Optional input value (GPU-accessible pointer) for tensor to replace part of the initial state in the environment.
 * The extents of the tensor are indetical to the output tensor extents and it will replace the MPS tensors in between the lower and upper bounds of specified environment.
 * Required to be a nullptr if MPS projection is not symmetric.
 * \param[in] stridesOut Strides of the output tensor environment for the specified environment.
 * \param[out] envTensorDataOut Computed tensor environment for the specified contiguous
 * subset of sites (GPU-accessible pointer).
 * The provided buffer will be conjugated on-the-fly during the environment contraction.
 * \param[in] applyInvMetric Whether or not to apply the inverse metric of the MPS state with respect to the environment to the computed tensor environment.
 * Currently application of the inverse metric is not supported.
 * \param[in] reResolveChannels Whether or not to reresolve the channels of the computed tensor environment on compute call.
 * If true, the behaviour aligns with that of other State API properties computed on a State instance for which StateCompute has not yet been invoked.
 * If false, the behaviour aligns with that of other State API properties computed on a State instance for which StateCompute has already been invoked.
 * \param[in,out] workDesc Allocated workspace descriptor.
 * \param[in] cudaStream CUDA stream.
 * \return cutensornetStatus_t
 */
cutensornetStatus_t cutensornetStateProjectionMPSComputeTensorEnv(const cutensornetHandle_t handle,
                                                             cutensornetStateProjectionMPS_t tensorNetworkProjection,
                                                             const cutensornetMPSEnvBounds_t* envSpec,
                                                             const int64_t stridesIn[],
                                                             const void *envTensorDataIn,
                                                             const int64_t stridesOut[],
                                                             void *envTensorDataOut,
                                                             int32_t applyInvMetric,
                                                             int32_t reResolveChannels,
                                                             cutensornetWorkspaceDescriptor_t workDesc,
                                                             cudaStream_t cudaStream);


/**
 * \brief Queries the tensor dimension strides and extents for the MPS representation tensor for the specified contiguous 0-, 1-, or 2-site
 * subset of sites.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in] tensorNetworkProjection Tensor network state MPS projection.
 * \param[in] envSpec Specification of the environment for which the tensor metadata is requested.
 * Note that currently only single site environments are supported.
 * \param[out] extents Mode extents of the environment MPS tensor.
 * For pure states, the required length of the array is n+2 for an n-site environment specified by envSpec,
 * except for environments which comprise the boundary for open boundary conditions, which are of length n+1.
 * Note that currently only single site environments are supported.
 * \param[out] recommendedStrides Recommended strides of the environment MPS tensor, of the same length as the extents array.
 * Using the recommended strides may offer performance benefits.
 * \return cutensornetStatus_t
 */
cutensornetStatus_t cutensornetStateProjectionMPSGetTensorInfo(const cutensornetHandle_t handle,
    const cutensornetStateProjectionMPS_t tensorNetworkProjection,
    const cutensornetMPSEnvBounds_t* envSpec,
    int64_t extents[],
    int64_t recommendedStrides[]);

/**
 * \brief Computes the MPS representation tensor for the specified contiguous 0-, 1-, or 2-site subset of sites.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkProjection Tensor network state MPS projection.
 * \param[in] envSpec Specification of environment.
 * The environment has to have been requested during the creation of the tensor network state MPS projection.
 * Note that currently only single site environments are supported.
 * \param[in] strides Strides of the externally provided MPS representation tensor for the specified environment.
 * \param[out] envTensorData The computed tensor of the MPS representation for the specified environment will be written to this buffer with the provided strides.
 * Extents of the provided buffer need to be queried using cutensornetStateProjectionMPSGetTensorInfo().
 * \param[in,out] workDesc Allocated workspace descriptor.
 * \param[in] cudaStream CUDA stream.
 * \return cutensornetStatus_t 
 */
cutensornetStatus_t cutensornetStateProjectionMPSExtractTensor(const cutensornetHandle_t handle,
                                                          cutensornetStateProjectionMPS_t tensorNetworkProjection,
                                                          const cutensornetMPSEnvBounds_t* envSpec,
                                                          const int64_t strides[],
                                                          void *envTensorData,
                                                          cutensornetWorkspaceDescriptor_t workDesc,
                                                          cudaStream_t cudaStream);

/**
 * \brief Inserts the MPS representation tensor for the specified contiguous 0-, 1-, or 2-site subset of sites.
 *
 * \param[in] handle cuTensorNet library handle.
 * \param[in,out] tensorNetworkProjection Tensor network state MPS projection.
 * \param[in] envSpec Specification of environment.
 * \param[in] orthoSpec Specification of the orthogonality condition of the MPS after insertion.
 * For insertion of a 1-site environment, this argument is currently required to be identical to envSpec.
 * \param[in] strides Strides of the externally provided MPS representation tensor for the specified environment.
 * \param[in] envTensorData Externally provided MPS representation tensor for the specified environment.
 * If the projection MPS is configured with two-site environments, extents may have changed after insertion of tensors
 * and need to be queried using cutensornetStateProjectionMPSGetTensorInfo().
 * \param[in,out] workDesc Allocated workspace descriptor.
 * \param[in] cudaStream CUDA stream.
 * \return cutensornetStatus_t
 */
cutensornetStatus_t cutensornetStateProjectionMPSInsertTensor(const cutensornetHandle_t handle,
                                                         cutensornetStateProjectionMPS_t tensorNetworkProjection,
                                                         const cutensornetMPSEnvBounds_t* envSpec,
                                                         const cutensornetMPSEnvBounds_t* orthoSpec,
                                                         const int64_t strides[],
                                                         const void *envTensorData,
                                                         cutensornetWorkspaceDescriptor_t workDesc,
                                                         cudaStream_t cudaStream);

/**
 * \brief Destroys the tensor network state MPS projection.
 *
 * \param[in] tensorNetworkProjection Tensor network state MPS projection.
 */
cutensornetStatus_t cutensornetDestroyStateProjectionMPS(cutensornetStateProjectionMPS_t tensorNetworkProjection);

#if defined(__cplusplus)
}
#endif /* __cplusplus */
