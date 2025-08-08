/*
 * SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: LicenseRef-NvidiaProprietary
 *
 * NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
 * property and proprietary rights in and to this material, related
 * documentation and any modifications thereto. Any use, reproduction,
 * disclosure or distribution of this material and related documentation
 * without an express license agreement from NVIDIA CORPORATION or
 * its affiliates is strictly prohibited.
 */

/** @file custatevec.h
 *  @details cuStateVec API
 */

/**
 * \defgroup overview Overview of cuStateVec key features
 * \{ */

/**
 *  \page state_vector Description of state vectors
 *  In the cuStateVec library, the state vector is always given as a device array and its
 *  data type is specified by a \p cudaDataType_t constant. It's the user's responsibility to manage
 *  memory for the state vector.
 *
 *  This version of cuStateVec library supports 128-bit complex (complex128) and 64-bit complex
 *  (complex64) as datatypes of the state vector. The size of a state vector is represented by the
 *  \p nIndexBits argument which corresponds to the number of qubits in a circuit.
 *  Therefore, the state vector size is expressed as \f$2^{\text{nIndexBits}}\f$.
 *
 *  The type ::custatevecIndex_t is provided to express the state vector index, which is
 *  a typedef of the 64-bit signed integer. It is also used to express the number of state vector
 *  elements.
 */

/**
 *  \page bit_ordering Bit Ordering
 *  In the cuStateVec library, the bit ordering of the state vector index is defined
 *  in little endian order. The 0-th index bit is the least significant bit (LSB).
 *  Most functions accept arguments to specify bit positions as integer arrays. Those bit positions
 *  are specified in little endian order. Values in bit positions are in the range
 *  \f$[0, \text{nIndexBits})\f$.
 *
 *  The cuStateVec library represents bit strings in either of the following two ways:
 *
 *  \li One 32-bit signed integer array for one bit string: \par
 *  Some APIs use a pair of 32-bit signed integer arrays \p bitString and \p bitOrdering arguments
 *  to specify one bit string. The \p bitString argument specifies bit string values as an array of 0s and 1s.
 *  The \p bitOrdering argument specifies the bit positions of the \p bitString array elements
 *  in little endian order. Both arrays are allocated on host memory.
 *  \par
 *  In the following example, "10" is specified as a bit string. Bit string values are mapped to
 *  the 2nd and 3rd index bits and can be used to specify a bit mask, \f$***\cdots *10*\f$.
 *  \code
 *   int32_t bitString[]   = {0, 1}
 *   int32_t bitOrdering[] = {1, 2}
 *  \endcode
 *  \li One 64-bit signed integer array for multiple bit strings: \par
 *  Some APIs introduce a pair of \p bitStrings and \p bitOrdering arguments to represent each bit string using
 *  ::custatevecIndex_t, which is a 64-bit signed integer, to handle multiple bit strings with small memory
 *  footprint. The \p bitOrdering argument is a 32-bit signed integer array and it specifies the bit positions of each
 *  bit string in the \p bitStrings argument in little endian order.
 *  \par
 *  The following example describes the same bit string, as was used in the previous example:
 *  \code
 *    custatevecIndex_t bitStrings[] = {0b10}
 *    int32_t bitOrdering[] = {1, 2}
 *  \endcode
 *  \par
 *  \p bitStrings are allocated on host memory but some APIs allow \p bitStrings to be allocated on device memory
 *  as well. For the detailed requirements, please refer to each API description.
 */

/**
 *  \page data_types Supported data types
 *
 *  By default, computation is executed using the corresponding precision of the state vector,
 *  double float (FP64) for complex128 and single float (FP32) for complex64.
 *
 *  The cuStateVec library also provides the compute type, allowing computation with reduced
 *  precision. Some cuStateVec functions accept the compute type specified by using
 *  ::custatevecComputeType_t.
 *
 *  Below is the table of combinations of state vector and compute types available in the current
 *  version of the cuStateVec library.
 *
 *  State vector / cudaDataType_t | Matrix / cudaDataType_t  | Compute / custatevecComputeType_t
 *  ------------------------------|--------------------------|----------------------------------
 *  Complex 128 / CUDA_C_64F      | Complex 128 / CUDA_C_64F | FP64 / CUSTATEVEC_COMPUTE_64F
 *  Complex 64  / CUDA_C_32F      | Complex 128 / CUDA_C_64F | FP32 / CUSTATEVEC_COMPUTE_32F
 *  Complex 64  / CUDA_C_32F      | Complex 64  / CUDA_C_32F | FP32 / CUSTATEVEC_COMPUTE_32F
 *
 *  \note ::CUSTATEVEC_COMPUTE_TF32 is not available in this version.
 */

/**
 *  \page workspace Workspace
 *  The cuStateVec library internally manages temporary device memory for executing functions,
 *  which is referred to as context workspace.
 *
 *  The context workspace is attached to the cuStateVec context and allocated when a cuStateVec
 *  context is created by calling custatevecCreate(). The default size of the context workspace
 *  is chosen to cover most typical use cases, obtained by calling
 *  custatevecGetDefaultWorkspaceSize().
 *
 *  When the context workspace cannot provide enough amount of temporary memory or when a device 
 *  memory chunk is shared by two or more functions, there are two options for users:
 *    - Users can provide user-managed device memory for the extra workspace.
 *      Functions that need the extra workspace have their sibling functions suffixed by 
 *      ``GetWorkspaceSize()``. If these functions return a nonzero value via the \p extraBufferSizeInBytes 
 *      argument, users are requested to allocate a device memory and supply the pointer to the allocated 
 *      memory to the corresponding function. The extra workspace should be 256-byte aligned, which is 
 *      automatically satisfied by using ``cudaMalloc()`` to allocate device memory. If the size of 
 *      the extra workspace is not enough, ::CUSTATEVEC_STATUS_INSUFFICIENT_WORKSPACE is returned.
 *    - Users also can set a device memory handler. When it is set to the cuStateVec library context,
 *      the library can directly draw memory from the pool on the user’s behalf. In this case, users are not
 *      required to allocate device memory explicitly and a null pointer (zero size) can be specified as the
 *      extra workspace (size) in the function. Please refer to ::custatevecDeviceMemHandler_t and
 *      custatevecSetDeviceMemHandler() for details.
 */

/** \} end of overview */

#pragma once

#define CUSTATEVEC_VER_MAJOR 1 //!< cuStateVec major version.
#define CUSTATEVEC_VER_MINOR 9 //!< cuStateVec minor version.
#define CUSTATEVEC_VER_PATCH 0 //!< cuStateVec patch version.
#define CUSTATEVEC_VERSION (CUSTATEVEC_VER_MAJOR * 1000 + CUSTATEVEC_VER_MINOR * 100 + CUSTATEVEC_VER_PATCH) //!< cuStateVec Version.

#define CUSTATEVEC_ALLOCATOR_NAME_LEN 64

#include <library_types.h>                        // cudaDataType_t
#include <cuda_runtime_api.h>                     // cudaStream_t

#if !defined(CUSTATEVECAPI)
#    if defined(_WIN32)
#        define CUSTATEVECAPI __stdcall //!< cuStateVec calling convention
#    else
#        define CUSTATEVECAPI           //!< cuStateVec calling convention
#    endif
#endif

#if defined(__cplusplus)
#include <cstdint>                                // integer types
#include <cstdio>                                 // FILE

extern "C" {
#else
#include <stdint.h>                               // integer types
#include <stdio.h>                                // FILE

#endif // defined(__cplusplus)

/**
 * \defgroup datastructures Opaque data structures
 * \{ */

/** 
 * \typedef custatevecIndex_t
 *
 * \brief Type for state vector indexing.
 * \details This type is used to represent the indices of the state vector.
 * As every bit in the state vector index corresponds to one qubit in a circuit,
 * this type is also used to represent bit strings.
 * The bit ordering is in little endian. The 0-th bit is the LSB.
 */
typedef int64_t custatevecIndex_t;


/**
 * \typedef custatevecHandle_t
 * \brief This handle stores necessary information for carrying out state vector calculations.
 * \details This handle holds the cuStateVec library context (device properties, system information,
 * etc.), which is used in all cuStateVec function calls.
 * The handle must be initialized and destroyed using the custatevecCreate() and custatevecDestroy()
 * functions, respectively.
 */
typedef struct custatevecContext* custatevecHandle_t;


/**
 * \typedef custatevecSamplerDescriptor_t
 * \brief This descriptor holds the context of the sampling operation, initialized using custatevecSamplerCreate()
 * and destroyed using custatevecSamplerDestroy(), respectively.
 */

typedef struct custatevecSamplerDescriptor* custatevecSamplerDescriptor_t;


/**
 * \typedef custatevecAccessorDescriptor_t
 * \brief This descriptor holds the context of accessor operation, initialized using custatevecAccessorCreate()
 * and destroyed using custatevecAccessorDestroy(), respectively.
 */

typedef struct custatevecAccessorDescriptor* custatevecAccessorDescriptor_t;


/**
 * \typedef custatevecLoggerCallback_t
 * \brief A callback function pointer type for logging. Use custatevecLoggerSetCallback() to set the callback function.
 * \param[in] logLevel the log level
 * \param[in] functionName the name of the API that logged this message
 * \param[in] message the log message
 */
typedef void(*custatevecLoggerCallback_t)(
        int32_t logLevel,
        const char* functionName,
        const char* message
);

/**
 * \typedef custatevecLoggerCallbackData_t
 * \brief A callback function pointer type for logging, with user data accepted. Use custatevecLoggerSetCallbackData() to set the callback function.
 * \param[in] logLevel the log level
 * \param[in] functionName the name of the API that logged this message
 * \param[in] message the log message
 * \param[in] userData the user-provided data to be used inside the callback function
 */
typedef void(*custatevecLoggerCallbackData_t)(
        int32_t logLevel,
        const char* functionName,
        const char* message,
        void* userData
);

/**
 * \brief The device memory handler structure holds information about the user-provided, \em stream-ordered device memory pool (mempool).
 */
typedef struct { 
  /**
   * A pointer to the user-owned mempool/context object.
   */
  void* ctx;
  /**
   * A function pointer to the user-provided routine for allocating device memory of \p size on \p stream.
   *
   * The allocated memory should be made accessible to the current device (or more
   * precisely, to the current CUDA context bound to the library handle).
   *
   * This interface supports any stream-ordered memory allocator \p ctx. Upon success,
   * the allocated memory can be immediately used on the given stream by any
   * operations enqueued/ordered on the same stream after this call.
   *
   * It is the caller’s responsibility to ensure a proper stream order is established.
   *
   * The allocated memory should be at least 256-byte aligned.
   *
   * \param[in] ctx A pointer to the user-owned mempool object.
   * \param[out] ptr On success, a pointer to the allocated buffer.
   * \param[in] size The amount of memory in bytes to be allocated.
   * \param[in] stream The CUDA stream on which the memory is allocated (and the stream order is established).
   * \return Error status of the invocation. Return 0 on success and any nonzero integer otherwise. This function must not throw if it is a C++ function.
   *
   */
  int (*device_alloc)(void* ctx, void** ptr, size_t size, cudaStream_t stream);
  /**
   * A function pointer to the user-provided routine for deallocating device memory of \p size on \p stream.
   * 
   * This interface supports any stream-ordered memory allocator. Upon success, any 
   * subsequent accesses (of the memory pointed to by the pointer \p ptr) ordered after 
   * this call are undefined behaviors.
   *
   * It is the caller’s responsibility to ensure a proper stream order is established.
   *
   * If the arguments \p ctx and \p size are not the same as those passed to \p device_alloc to 
   * allocate the memory pointed to by \p ptr, the behavior is undefined.
   * 
   * The argument \p stream need not be identical to the one used for allocating \p ptr, as
   * long as the stream order is correctly established. The behavior is undefined if
   * this assumption is not held.
   *
   * \param[in] ctx A pointer to the user-owned mempool object.
   * \param[in] ptr The pointer to the allocated buffer.
   * \param[in] size The size of the allocated memory.
   * \param[in] stream The CUDA stream on which the memory is deallocated (and the stream ordering is established).
   * \return Error status of the invocation. Return 0 on success and any nonzero integer otherwise. This function must not throw if it is a C++ function.
   */
  int (*device_free)(void* ctx, void* ptr, size_t size, cudaStream_t stream); 
  /**
   * The name of the provided mempool.
   */
  char name[CUSTATEVEC_ALLOCATOR_NAME_LEN];
} custatevecDeviceMemHandler_t;

/** \} end of datastructures */


/**
 * \defgroup enumerators Enumerators
 *
 * \{ */

/**
 * \typedef custatevecStatus_t
 * \brief Contains the library status. Each cuStateVec API returns this enumerator.
 */
typedef enum custatevecStatus_t {
    CUSTATEVEC_STATUS_SUCCESS                   = 0, ///< The API call has finished successfully
    CUSTATEVEC_STATUS_NOT_INITIALIZED           = 1, ///< The library handle was not initialized
    CUSTATEVEC_STATUS_ALLOC_FAILED              = 2, ///< Memory allocation in the library was failed
    CUSTATEVEC_STATUS_INVALID_VALUE             = 3, ///< Wrong parameter was passed. For example, a null pointer as input data, or an invalid enum value
    CUSTATEVEC_STATUS_ARCH_MISMATCH             = 4, ///< The device capabilities are not enough for the set of input parameters provided
    CUSTATEVEC_STATUS_EXECUTION_FAILED          = 5, ///< Error during the execution of the device tasks
    CUSTATEVEC_STATUS_INTERNAL_ERROR            = 6, ///< Unknown error occurred in the library
    CUSTATEVEC_STATUS_NOT_SUPPORTED             = 7, ///< API is not supported by the backend
    CUSTATEVEC_STATUS_INSUFFICIENT_WORKSPACE    = 8, ///< Workspace on device is too small to execute
    CUSTATEVEC_STATUS_SAMPLER_NOT_PREPROCESSED  = 9, ///< Sampler was called prior to preprocessing
    CUSTATEVEC_STATUS_NO_DEVICE_ALLOCATOR       = 10, ///< The device memory pool was not set
    CUSTATEVEC_STATUS_DEVICE_ALLOCATOR_ERROR    = 11, ///< Operation with the device memory pool failed
    CUSTATEVEC_STATUS_COMMUNICATOR_ERROR        = 12, ///< Operation with the communicator failed
    CUSTATEVEC_STATUS_LOADING_LIBRARY_FAILED    = 13, ///< Dynamic loading of the shared library failed
    CUSTATEVEC_STATUS_MAX_VALUE                 = 14
} custatevecStatus_t;


/**
 * \typedef custatevecPauli_t
 * \brief Constants to specify Pauli basis:
 *   - \f$\boldsymbol{\sigma}_0 = \mathbf{I} = \left[ \begin{array}{rr} 1 & 0 \\ 0 & 1 \end{array}\right]\f$
 *   - \f$\boldsymbol{\sigma}_x = \left[ \begin{array}{rr} 0 & 1 \\ 1 & 0 \end{array}\right]\f$
 *   - \f$\boldsymbol{\sigma}_y = \left[ \begin{array}{rr} 0 & -i \\ i & 0 \end{array}\right]\f$
 *   - \f$\boldsymbol{\sigma}_z = \left[ \begin{array}{rr} 1 & 0 \\ 0 & -1 \end{array}\right]\f$
 */
typedef enum custatevecPauli_t {
    CUSTATEVEC_PAULI_I = 0, ///< Identity matrix
    CUSTATEVEC_PAULI_X = 1, ///< Pauli X matrix
    CUSTATEVEC_PAULI_Y = 2, ///< Pauli Y matrix
    CUSTATEVEC_PAULI_Z = 3  ///< Pauli Z matrix
} custatevecPauli_t;


/**
 * \typedef custatevecMatrixLayout_t
 * \brief Constants to specify a matrix's memory layout.
 */
typedef enum custatevecMatrixLayout_t {
    CUSTATEVEC_MATRIX_LAYOUT_COL = 0, ///< Matrix stored in the column-major order
    CUSTATEVEC_MATRIX_LAYOUT_ROW = 1  ///< Matrix stored in the row-major order
} custatevecMatrixLayout_t;


/**
 * \typedef custatevecMatrixType_t
 * \brief Constants to specify the matrix type.
 */
typedef enum custatevecMatrixType_t {
    CUSTATEVEC_MATRIX_TYPE_GENERAL   = 0, ///< Non-specific type
    CUSTATEVEC_MATRIX_TYPE_UNITARY   = 1, ///< Unitary matrix
    CUSTATEVEC_MATRIX_TYPE_HERMITIAN = 2  ///< Hermitian matrix
} custatevecMatrixType_t;

/**
 * \typedef custatevecMatrixMapType_t
 * \brief Constants to specify how to assign matrices to batched state vectors.
 */
typedef enum custatevecMatrixMapType_t {
    CUSTATEVEC_MATRIX_MAP_TYPE_BROADCAST      = 0, ///< matrix to be applied is uniform among the all state vectors.
    CUSTATEVEC_MATRIX_MAP_TYPE_MATRIX_INDEXED = 1, ///< each state vector refers to indices to select its matrix.
} custatevecMatrixMapType_t;

/**
 * \typedef custatevecCollapseOp_t
 * \brief Constants to specify collapse operations.
 */
typedef enum custatevecCollapseOp_t {
    CUSTATEVEC_COLLAPSE_NONE               = 0, ///< Do not collapse the statevector
    CUSTATEVEC_COLLAPSE_NORMALIZE_AND_ZERO = 1, ///< Collapse, normalize, and fill zeros in the statevector
    CUSTATEVEC_COLLAPSE_RESET              = 2, ///< Reserved for future use 
} custatevecCollapseOp_t;


/**
 * \typedef custatevecComputeType_t
 * \brief Constants to specify the minimal accuracy for arithmetic operations.
 */
typedef enum custatevecComputeType_t {
    CUSTATEVEC_COMPUTE_DEFAULT = 0,           ///< FP32(float) for Complex64, FP64(double) for Complex128
    CUSTATEVEC_COMPUTE_32F     = (1U << 2U),  ///< FP32(float)
    CUSTATEVEC_COMPUTE_64F     = (1U << 4U),  ///< FP64(double)
    CUSTATEVEC_COMPUTE_TF32    = (1U << 12U)  ///< TF32(tensor-float-32)
} custatevecComputeType_t;


/**
 * \typedef custatevecSamplerOutput_t
 * \brief Constants to specify the order of bit strings in sampling outputs.
 */
typedef enum custatevecSamplerOutput_t {
    CUSTATEVEC_SAMPLER_OUTPUT_RANDNUM_ORDER   = 0,  ///< the same order as the given random numbers
    CUSTATEVEC_SAMPLER_OUTPUT_ASCENDING_ORDER = 1,  ///< reordered in the ascending order
} custatevecSamplerOutput_t;


/**
 * \typedef custatevecDeviceNetworkType_t
 * \brief Constants to specify the device network topology.
 */
typedef enum custatevecDeviceNetworkType_t
{
    CUSTATEVEC_DEVICE_NETWORK_TYPE_SWITCH   = 1, ///< devices are connected via network switch
    CUSTATEVEC_DEVICE_NETWORK_TYPE_FULLMESH = 2, ///< devices are connected by full mesh network
} custatevecDeviceNetworkType_t;

/**
 * \typedef custatevecStateVectorType_t
 *
 * \brief Constants to specify the quantum state.
 */
typedef enum custatevecStateVectorType_t
{
    CUSTATEVEC_STATE_VECTOR_TYPE_ZERO    = 0, ///< create a zero state,
                                              ///< \f$|00\cdots0\rangle\f$.
    CUSTATEVEC_STATE_VECTOR_TYPE_UNIFORM = 1, ///< create an equal superposition of all computational basis,
                                              ///< \f$\frac{1}{\sqrt{2^n}}\left(|00\cdots00\rangle + |00\cdots01\rangle +
                                              ///  \cdots + |11\cdots10\rangle + |11\cdots11\rangle\right)\f$.
    CUSTATEVEC_STATE_VECTOR_TYPE_GHZ     = 2, ///< create a GHZ state,
                                              ///< \f$\frac{1}{\sqrt{2}}\left(|00\cdots0\rangle + |11\cdots1\rangle\right)\f$.
    CUSTATEVEC_STATE_VECTOR_TYPE_W       = 3, ///< create a W state,
                                              ///< \f$\frac{1}{\sqrt{n}}\left(|000\cdots001\rangle + |000\cdots010\rangle +
                                              ///  \cdots + |010\cdots000\rangle + |100\cdots000\rangle\right)\f$.
} custatevecStateVectorType_t;

/**
 * \typedef custatevecMathMode_t
 * \brief Constants to specify the compute precision mode.
 */
typedef enum custatevecMathMode_t {
    CUSTATEVEC_MATH_MODE_DEFAULT                       = 0,         ///< Default
    CUSTATEVEC_MATH_MODE_ALLOW_FP32_EMULATED_BF16X9    = (1U << 0), ///< Enable BF16x9 emulation kernels when applicable
    CUSTATEVEC_MATH_MODE_DISALLOW_FP32_EMULATED_BF16X9 = (1U << 1), ///< Disable BF16x9 emulation kernels
} custatevecMathMode_t;

/** \} end of enumerators */

/**
 * \defgroup management Initialization and management routines
 * \{ */

/**
 * \brief This function initializes the cuStateVec library and creates a handle
 * on the cuStateVec context. It must be called prior to any other cuStateVec
 * API functions. If the device has unsupported compute capability,
 * this function could return ::CUSTATEVEC_STATUS_ARCH_MISMATCH.
 *
 * \param[in]  handle  the pointer to the handle to the cuStateVec context
 */
custatevecStatus_t 
custatevecCreate(custatevecHandle_t* handle);

/**
 * \brief This function releases resources used by the cuStateVec
 * library.
 *
 * \param[in]  handle  the handle to the cuStateVec context
 */
custatevecStatus_t
custatevecDestroy(custatevecHandle_t handle);


/**
 * \brief This function returns the default workspace size defined by the
 * cuStateVec library.
 *
 * \param[in] handle the handle to the cuStateVec context
 * \param[out] workspaceSizeInBytes default workspace size
 *
 * \details This function returns the default size used for the workspace.
 */
custatevecStatus_t
custatevecGetDefaultWorkspaceSize(custatevecHandle_t handle,
                                  size_t*            workspaceSizeInBytes);


/**
 * \brief This function sets the workspace used by the cuStateVec library.
 *
 * \param[in] handle the handle to the cuStateVec context
 * \param[in] workspace device pointer to workspace
 * \param[in] workspaceSizeInBytes workspace size
 *
 * \details This function sets the workspace attached to the handle.
 * The required size of the workspace is obtained by
 * custatevecGetDefaultWorkspaceSize().
 *
 * By setting a larger workspace, users are able to execute functions without
 * allocating the extra workspace in some functions.
 * 
 * If a device memory handler is set, the \p workspace can be set to null and 
 * the workspace is allocated using the user-defined memory pool.
 */
custatevecStatus_t
custatevecSetWorkspace(custatevecHandle_t handle,
                       void*              workspace,
                       size_t             workspaceSizeInBytes);

/** 
 * \brief This function returns the name string for the input error code.
 * If the error code is not recognized, "unrecognized error code" is returned.
 *
 * \param[in] status Error code to convert to string
 */
const char*
custatevecGetErrorName(custatevecStatus_t status);

/**
 * \brief This function returns the description string for an error code. If 
 * the error code is not recognized, "unrecognized error code" is returned.
 
 * \param[in] status Error code to convert to string
 */
const char*
custatevecGetErrorString(custatevecStatus_t status);

/**
 * \brief This function returns the version information of the cuStateVec 
 * library.
 *
 * \param[in] type requested property (`MAJOR_VERSION`, 
 * `MINOR_VERSION`, or `PATCH_LEVEL`).
 * \param[out] value value of the requested property.
 */
custatevecStatus_t
custatevecGetProperty(libraryPropertyType type,
                      int32_t*            value);

/**
 * \brief This function returns the version information of the cuStateVec 
 *  library.
 */
size_t custatevecGetVersion();

/**
 * \brief This function sets the stream to be used by the cuStateVec library
 * to execute its routine.
 *
 * \param[in]  handle    the handle to the cuStateVec context
 * \param[in]  streamId  the stream to be used by the library
 */
custatevecStatus_t
custatevecSetStream(custatevecHandle_t handle,
                    cudaStream_t       streamId);


/**
 * \brief This function gets the cuStateVec library stream used to execute all
 * calls from the cuStateVec library functions.
 *
 * \param[in]  handle    the handle to the cuStateVec context
 * \param[out] streamId  the stream to be used by the library
 */
custatevecStatus_t
custatevecGetStream(custatevecHandle_t handle,
                    cudaStream_t*      streamId);

/**
 * \brief Experimental: This function sets the logging callback function.
 *
 * \param[in]  callback   Pointer to a callback function. See ::custatevecLoggerCallback_t.
 */
custatevecStatus_t
custatevecLoggerSetCallback(custatevecLoggerCallback_t callback);

/**
 * \brief Experimental: This function sets the logging callback function with user data.
 *
 * \param[in]  callback   Pointer to a callback function. See ::custatevecLoggerCallbackData_t.
 * \param[in]  userData   Pointer to user-provided data.
 */
custatevecStatus_t
custatevecLoggerSetCallbackData(custatevecLoggerCallbackData_t callback,
                                void* userData);

/**
 * \brief Experimental: This function sets the logging output file. 
 * \note Once registered using this function call, the provided file handle
 * must not be closed unless the function is called again to switch to a 
 * different file handle.
 *
 * \param[in]  file  Pointer to an open file. File should have write permission.
 */
custatevecStatus_t
custatevecLoggerSetFile(FILE* file);

/**
 * \brief Experimental: This function opens a logging output file in the given 
 * path.
 *
 * \param[in]  logFile  Path of the logging output file.
 */
custatevecStatus_t
custatevecLoggerOpenFile(const char* logFile);

/**
 * \brief Experimental: This function sets the value of the logging level.
 * \details Levels are defined as follows:
 * Level| Summary           | Long Description
 * -----|-------------------|-----------------
 *  "0" | Off               | logging is disabled (default)
 *  "1" | Errors            | only errors will be logged
 *  "2" | Performance Trace | API calls that launch CUDA kernels will log their parameters and important information
 *  "3" | Performance Hints | hints that can potentially improve the application's performance
 *  "4" | Heuristics Trace  | provides general information about the library execution, may contain details about heuristic status
 *  "5" | API Trace         | API Trace - API calls will log their parameter and important information
 * \param[in]  level  Value of the logging level.
 */
custatevecStatus_t
custatevecLoggerSetLevel(int32_t level);

/**
 * \brief Experimental: This function sets the value of the logging mask.
 * Masks are defined as a combination of the following masks:
 * Level| Description       |
 * -----|-------------------|
 *  "0" | Off               |
 *  "1" | Errors            |
 *  "2" | Performance Trace |
 *  "4" | Performance Hints |
 *  "8" | Heuristics Trace  |
 *  "16"| API Trace         |
 * Refer to ::custatevecLoggerCallback_t for the details.
 * \param[in]  mask  Value of the logging mask.
 */
custatevecStatus_t
custatevecLoggerSetMask(int32_t mask);

/**
 * \brief Experimental: This function disables logging for the entire run.
 */
custatevecStatus_t
custatevecLoggerForceDisable();

/**
 * \brief Get the current device memory handler.
 *
 * \param[in] handle Opaque handle holding cuStateVec's library context.
 * \param[out] handler If previously set, the struct pointed to by \p handler is filled in, otherwise ::CUSTATEVEC_STATUS_NO_DEVICE_ALLOCATOR is returned.
 */
custatevecStatus_t custatevecGetDeviceMemHandler(custatevecHandle_t            handle, 
                                                 custatevecDeviceMemHandler_t* handler); 
 
/**
 * \brief Set the current device memory handler.
 *
 * Once set, when cuStateVec needs device memory in various API calls it will allocate from the user-provided memory pool
 * and deallocate at completion. See custatevecDeviceMemHandler_t and APIs that require extra workspace for further detail.
 *
 * The internal stream order is established using the user-provided stream set via custatevecSetStream().
 *
 * If \p handler argument is set to nullptr, the library handle will detach its existing memory handler.
 *
 * \warning It is <em> undefined behavior </em> for the following scenarios:
 *   - the library handle is bound to a memory handler and subsequently to another handler
 *   - the library handle outlives the attached memory pool
 *   - the memory pool is not <em> stream-ordered </em>
 *
 * \param[in] handle Opaque handle holding cuStateVec's library context.
 * \param[in] handler the device memory handler that encapsulates the user's mempool. The struct content is copied internally.
 */
custatevecStatus_t custatevecSetDeviceMemHandler(custatevecHandle_t                  handle, 
                                                 const custatevecDeviceMemHandler_t* handler); 

/**
 * \brief Set the compute precision mode.
 *
 * This function enables to choose the compute precision mode as defined by custatevecMathMode_t.
 * The default math mode is ::CUSTATEVEC_MATH_MODE_DEFAULT.
 * 
 * \param[in] handle Opaque handle holding cuStateVec's library context.
 * \param[in] mode Compute precision mode.
 */
custatevecStatus_t custatevecSetMathMode(custatevecHandle_t handle,
                                         custatevecMathMode_t mode);

/**
 * \brief Get the current compute precision mode.
 *
 * This function gets the compute precision mode set to custatevecHandle_t.
 * 
 * \param[in] handle Opaque handle holding cuStateVec's library context.
 * \param[out] mode Compute precision mode.
 */
custatevecStatus_t custatevecGetMathMode(custatevecHandle_t handle,
                                         custatevecMathMode_t* mode);

/** \} end of management*/

/**
 * \defgroup singlegpuapi Single GPU API
 *
 * \{ */

/*
 * Sum of squared absolute values of state vector elements
 */

/**
 * \brief Calculates the sum of squared absolute values on a given Z product basis.
 * 
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sv state vector
 * \param[in] svDataType data type of state vector
 * \param[in] nIndexBits the number of index bits
 * \param[out] abs2sum0 pointer to a host or device variable to store the sum of squared absolute values for parity == 0
 * \param[out] abs2sum1 pointer to a host or device variable to store the sum of squared absolute values for parity == 1
 * \param[in] basisBits pointer to a host array of Z-basis index bits
 * \param[in] nBasisBits the number of basisBits
 *
 * \details This function calculates sums of squared absolute values on a given Z product basis.
 * If a null pointer is specified to \p abs2sum0 or \p abs2sum1, the sum for the corresponding
 * value is not calculated.
 * Since the sum of (\p abs2sum0 + \p abs2sum1) is identical to the norm of the state vector,
 * one can calculate the probability where parity == 0 as (\p abs2sum0 / (\p abs2sum0 + \p abs2sum1)).
 */

custatevecStatus_t
custatevecAbs2SumOnZBasis(custatevecHandle_t  handle,
                          const void*         sv,
                          cudaDataType_t      svDataType,
                          const uint32_t      nIndexBits,
                          double*             abs2sum0,
                          double*             abs2sum1,
                          const int32_t*      basisBits,
                          const uint32_t      nBasisBits);


/**
 * \brief Calculate abs2sum array for a given set of index bits
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sv state vector
 * \param[in] svDataType data type of state vector
 * \param[in] nIndexBits the number of index bits
 * \param[out] abs2sum pointer to a host or device array of sums of squared absolute values
 * \param[in] bitOrdering pointer to a host array of index bit ordering
 * \param[in] bitOrderingLen the length of bitOrdering
 * \param[in] maskBitString pointer to a host array for a bit string to specify mask
 * \param[in] maskOrdering  pointer to a host array for the mask ordering
 * \param[in] maskLen the length of mask
 *
 * \details Calculates an array of sums of squared absolute values of state vector elements.
 * The abs2sum array can be on host or device. The index bit ordering abs2sum array is specified
 * by the \p bitOrdering and \p bitOrderingLen arguments. Unspecified bits are folded (summed up).
 *
 * The \p maskBitString, \p maskOrdering and \p maskLen arguments set bit mask in the state
 * vector index.  The abs2sum array is calculated by using state vector elements whose indices 
 * match the mask bit string. If the \p maskLen argument is 0, null pointers can be specified to the
 * \p maskBitString and \p maskOrdering arguments, and all state vector elements are used
 * for calculation.
 *
 * By definition, bit positions in \p bitOrdering and \p maskOrdering arguments should not overlap.
 *
 * The empty \p bitOrdering can be specified to calculate the norm of state vector. In this case,
 * 0 is passed to the \p bitOrderingLen argument and the \p bitOrdering argument can be a null pointer.
 *
 * \note Since the size of abs2sum array is proportional to \f$ 2^{bitOrderingLen} \f$ ,
 * the max length of \p bitOrdering depends on the amount of available memory and \p maskLen.
 */

custatevecStatus_t
custatevecAbs2SumArray(custatevecHandle_t handle,
                       const void*        sv,
                       cudaDataType_t     svDataType,
                       const uint32_t     nIndexBits,
                       double*            abs2sum,
                       const int32_t*     bitOrdering,
                       const uint32_t     bitOrderingLen,
                       const int32_t*     maskBitString,
                       const int32_t*     maskOrdering,
                       const uint32_t     maskLen);


/**
 * \brief Collapse state vector on a given Z product basis.
 * 
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType data type of state vector
 * \param[in] nIndexBits the number of index bits
 * \param[in] parity parity, 0 or 1
 * \param[in] basisBits pointer to a host array of Z-basis index bits
 * \param[in] nBasisBits the number of Z basis bits
 * \param[in] norm normalization factor
 *
 * \details This function collapses state vector on a given Z product basis.
 * The state elements that match the parity argument are scaled by a factor
 * specified in the \p norm argument. Other elements are set to zero.
 */

custatevecStatus_t
custatevecCollapseOnZBasis(custatevecHandle_t handle,
                           void*              sv,
                           cudaDataType_t     svDataType,
                           const uint32_t     nIndexBits,
                           const int32_t      parity,
                           const int32_t*     basisBits,
                           const uint32_t     nBasisBits,
                           double             norm);


/**
 * \brief Collapse state vector to the state specified by a given bit string.
 * 
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType data type of state vector
 * \param[in] nIndexBits the number of index bits
 * \param[in] bitString pointer to a host array of bit string
 * \param[in] bitOrdering pointer to a host array of bit string ordering
 * \param[in] bitStringLen length of bit string
 * \param[in] norm normalization constant
 *
 * \details This function collapses state vector to the state specified by a given bit string.
 * The state vector elements specified by the \p bitString, \p bitOrdering and \p bitStringLen arguments are
 * normalized by the \p norm argument. Other elements are set to zero.
 *
 * At least one basis bit should be specified, otherwise this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 */

custatevecStatus_t
custatevecCollapseByBitString(custatevecHandle_t handle,
                              void*              sv,
                              cudaDataType_t     svDataType,
                              const uint32_t     nIndexBits,
                              const int32_t*     bitString,
                              const int32_t*     bitOrdering,
                              const uint32_t     bitStringLen,
                              double             norm);



/*
 * Measurement
 */

/**
 * \brief Measurement on a given Z-product basis
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType data type of state vector
 * \param[in] nIndexBits the number of index bits
 * \param[out] parity parity, 0 or 1
 * \param[in] basisBits pointer to a host array of Z basis bits
 * \param[in] nBasisBits the number of Z basis bits
 * \param[in] randnum random number, [0, 1).
 * \param[in] collapse Collapse operation
 *
 * \details This function does measurement on a given Z product basis.
 * The measurement result is the parity of the specified Z product basis.
 * At least one basis bit should be specified, otherwise this function fails.
 *
 * If ::CUSTATEVEC_COLLAPSE_NONE is specified for the collapse argument,
 * this function only returns the measurement result without collapsing the state vector.
 * If ::CUSTATEVEC_COLLAPSE_NORMALIZE_AND_ZERO is specified,
 * this function collapses the state vector as custatevecCollapseOnZBasis() does.
 *
 * If a random number is not in [0, 1), this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 * At least one basis bit should be specified, otherwise this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 */

custatevecStatus_t
custatevecMeasureOnZBasis(custatevecHandle_t          handle,
                          void*                       sv,
                          cudaDataType_t              svDataType,
                          const uint32_t              nIndexBits,
                          int32_t*                    parity,
                          const int32_t*              basisBits,
                          const uint32_t              nBasisBits,
                          const double                randnum,
                          enum custatevecCollapseOp_t collapse);



/**
 * \brief Batched single qubit measurement
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits
 * \param[out] bitString pointer to a host array of measured bit string
 * \param[in] bitOrdering pointer to a host array of bit string ordering
 * \param[in] bitStringLen length of bitString
 * \param[in] randnum random number, [0, 1).
 * \param[in] collapse  Collapse operation
 *
 * \details This function does batched single qubit measurement and returns a bit string.
 * The \p bitOrdering argument specifies index bits to be measured.  The measurement
 * result is stored in \p bitString in the ordering specified by the \p bitOrdering argument.
 *
 * If ::CUSTATEVEC_COLLAPSE_NONE is specified for the \p collapse argument, this function
 * only returns the measured bit string without collapsing the state vector.
 * When ::CUSTATEVEC_COLLAPSE_NORMALIZE_AND_ZERO is specified, this function
 * collapses the state vector as custatevecCollapseByBitString() does.
 *
 * If a random number is not in [0, 1), this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 * At least one basis bit should be specified, otherwise this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 * 
 * \note This API is for measuring a single state vector. For measuring batched state vectors, please use
 * custatevecMeasureBatched(), whose arguments are passed in a different convention.
 */
custatevecStatus_t
custatevecBatchMeasure(custatevecHandle_t          handle,
                       void*                       sv,
                       cudaDataType_t              svDataType,
                       const uint32_t              nIndexBits,
                       int32_t*                    bitString,
                       const int32_t*              bitOrdering,
                       const uint32_t              bitStringLen,
                       const double                randnum,
                       enum custatevecCollapseOp_t collapse);


/**
 * \brief Batched single qubit measurement for partial vector
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv partial state vector
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits
 * \param[out] bitString pointer to a host array of measured bit string
 * \param[in] bitOrdering pointer to a host array of bit string ordering
 * \param[in] bitStringLen length of bitString
 * \param[in] randnum random number, [0, 1).
 * \param[in] collapse  Collapse operation
 * \param[in] offset partial sum of squared absolute values
 * \param[in] abs2sum sum of squared absolute values for the entire state vector
 *
 * \details This function does batched single qubit measurement and returns a bit string.
 * The \p bitOrdering argument specifies index bits to be measured.  The measurement
 * result is stored in \p bitString in the ordering specified by the \p bitOrdering argument.
 *
 * If ::CUSTATEVEC_COLLAPSE_NONE is specified for the collapse argument, this function
 * only returns the measured bit string without collapsing the state vector.
 * When ::CUSTATEVEC_COLLAPSE_NORMALIZE_AND_ZERO is specified, this function
 * collapses the state vector as custatevecCollapseByBitString() does.
 *
 * This function assumes that \p sv is partial state vector and drops some most significant bits.
 * Prefix sums for lower indices and the entire state vector must be provided as \p offset and \p abs2sum, respectively.
 * When \p offset == \p abs2sum == 0, this function behaves in the same way as custatevecBatchMeasure().
 *
 * If a random number is not in [0, 1), this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 * At least one basis bit should be specified, otherwise this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 */

custatevecStatus_t
custatevecBatchMeasureWithOffset(custatevecHandle_t          handle,
                                 void*                       sv,
                                 cudaDataType_t              svDataType,
                                 const uint32_t              nIndexBits,
                                 int32_t*                    bitString,
                                 const int32_t*              bitOrdering,
                                 const uint32_t              bitStringLen,
                                 const double                randnum,
                                 enum custatevecCollapseOp_t collapse,
                                 const double                offset,
                                 const double                abs2sum);


/*
 *  Gate application
 */

/**
 * \brief Apply the exponential of a multi-qubit Pauli operator.
 * 
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of bits in the state vector index
 * \param[in] theta theta
 * \param[in] paulis host pointer to custatevecPauli_t array
 * \param[in] targets pointer to a host array of target bits
 * \param[in] nTargets the number of target bits
 * \param[in] controls pointer to a host array of control bits
 * \param[in] controlBitValues pointer to a host array of control bit values
 * \param[in] nControls the number of control bits
 *
 * \details Apply exponential of a tensor product of Pauli bases
 * specified by bases, \f$ e^{i \theta P} \f$, where \f$P\f$ is the product of Pauli bases.
 * The \p paulis, \p targets, and \p nTargets arguments specify Pauli bases and their bit
 * positions in the state vector index.
 *
 * At least one target and a corresponding Pauli basis should be specified.
 *
 * The \p controls and \p nControls arguments specifies the control bit positions
 * in the state vector index.
 *
 * The \p controlBitValues argument specifies bit values of control bits. The ordering
 * of \p controlBitValues is specified by the \p controls argument. If a null pointer is
 * specified to this argument, all control bit values are set to 1.
 */

custatevecStatus_t
custatevecApplyPauliRotation(custatevecHandle_t       handle,
                             void*                    sv,
                             cudaDataType_t           svDataType,
                             const uint32_t           nIndexBits,
                             double                   theta,
                             const custatevecPauli_t* paulis,
                             const int32_t*           targets,
                             const uint32_t           nTargets,
                             const int32_t*           controls,
                             const int32_t*           controlBitValues,
                             const uint32_t           nControls);


/**
 * \brief This function gets the required workspace size for custatevecApplyMatrix().
 *
 * \param[in] handle the handle to the cuStateVec context
 * \param[in] svDataType Data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[in] matrix host or device pointer to a matrix
 * \param[in] matrixDataType data type of matrix
 * \param[in] layout enumerator specifying the memory layout of matrix
 * \param[in] adjoint apply adjoint of matrix
 * \param[in] nTargets the number of target bits
 * \param[in] nControls the number of control bits
 * \param[in] computeType computeType of matrix multiplication
 * \param[out] extraWorkspaceSizeInBytes  workspace size
 *
 * \details This function returns the required extra workspace size to execute
 * custatevecApplyMatrix().
 * \p extraWorkspaceSizeInBytes will be set to 0 if no extra buffer is required
 * for a given set of arguments.
 */
custatevecStatus_t
custatevecApplyMatrixGetWorkspaceSize(custatevecHandle_t       handle,
                                      cudaDataType_t           svDataType,
                                      const uint32_t           nIndexBits,
                                      const void*              matrix,
                                      cudaDataType_t           matrixDataType,
                                      custatevecMatrixLayout_t layout,
                                      const int32_t            adjoint,
                                      const uint32_t           nTargets,
                                      const uint32_t           nControls,
                                      custatevecComputeType_t  computeType,
                                      size_t*                  extraWorkspaceSizeInBytes);

/**
 * \brief Apply gate matrix
 * 
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[in] matrix host or device pointer to a square matrix
 * \param[in] matrixDataType data type of matrix
 * \param[in] layout enumerator specifying the memory layout of matrix
 * \param[in] adjoint apply adjoint of matrix
 * \param[in] targets pointer to a host array of target bits
 * \param[in] nTargets the number of target bits
 * \param[in] controls pointer to a host array of control bits
 * \param[in] controlBitValues pointer to a host array of control bit values
 * \param[in] nControls the number of control bits
 * \param[in] computeType computeType of matrix multiplication
 * \param[in] extraWorkspace extra workspace
 * \param[in] extraWorkspaceSizeInBytes extra workspace size
 *
 * \details Apply gate matrix to a state vector.
 * The state vector size is \f$2^\text{nIndexBits}\f$.
 *
 * The matrix argument is a host or device pointer of a 2-dimensional array for a square matrix.
 * The size of matrix is (\f$2^\text{nTargets} \times 2^\text{nTargets}\f$ ) and the value type is specified by the
 * \p matrixDataType argument. The \p layout argument specifies the matrix layout which can be in either
 * row-major or column-major order.
 * The \p targets and \p controls arguments specify target and control bit positions in the state vector
 * index.
 *
 * The \p controlBitValues argument specifies bit values of control bits. The ordering
 * of \p controlBitValues is specified by the \p controls argument. If a null pointer is
 * specified to this argument, all control bit values are set to 1.
 *
 * By definition, bit positions in \p targets and \p controls arguments should not overlap.
 *
 * This function may return ::CUSTATEVEC_STATUS_INSUFFICIENT_WORKSPACE for large \p nTargets.
 * In such cases, the \p extraWorkspace and \p extraWorkspaceSizeInBytes arguments should be specified
 * to provide extra workspace.  The size of required extra workspace is obtained by
 * calling custatevecApplyMatrixGetWorkspaceSize().
 * A null pointer can be passed to the \p extraWorkspace argument if no extra workspace is
 * required.
 * Also, if a device memory handler is set, the \p extraWorkspace can be set to null, 
 * and the \p extraWorkspaceSizeInBytes can be set to 0.
 */

custatevecStatus_t
custatevecApplyMatrix(custatevecHandle_t          handle,
                      void*                       sv,
                      cudaDataType_t              svDataType,
                      const uint32_t              nIndexBits,
                      const void*                 matrix,
                      cudaDataType_t              matrixDataType,
                      custatevecMatrixLayout_t    layout,
                      const int32_t               adjoint,
                      const int32_t*              targets,
                      const uint32_t              nTargets,
                      const int32_t*              controls,
                      const int32_t*              controlBitValues,
                      const uint32_t              nControls,
                      custatevecComputeType_t     computeType,
                      void*                       extraWorkspace,
                      size_t                      extraWorkspaceSizeInBytes);


/*
 * Expectation
 */

/**
 * \brief This function gets the required workspace size for custatevecComputeExpectation().
 *
 * \param[in] handle the handle to the cuStateVec context
 * \param[in] svDataType Data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[in] matrix host or device pointer to a matrix
 * \param[in] matrixDataType data type of matrix
 * \param[in] layout enumerator specifying the memory layout of matrix
 * \param[in] nBasisBits the number of target bits
 * \param[in] computeType computeType of matrix multiplication
 * \param[out] extraWorkspaceSizeInBytes size of the extra workspace
 *
 * \details This function returns the size of the extra workspace required to execute
 * custatevecComputeExpectation().
 * \p extraWorkspaceSizeInBytes will be set to 0 if no extra buffer is required.
 */

custatevecStatus_t
custatevecComputeExpectationGetWorkspaceSize(custatevecHandle_t       handle,
                                             cudaDataType_t           svDataType,
                                             const uint32_t           nIndexBits,
                                             const void*              matrix,
                                             cudaDataType_t           matrixDataType,
                                             custatevecMatrixLayout_t layout,
                                             const uint32_t           nBasisBits,
                                             custatevecComputeType_t  computeType,
                                             size_t*                  extraWorkspaceSizeInBytes);

/**
 * \brief Compute expectation of matrix observable.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sv state vector
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[out] expectationValue host pointer to a variable to store an expectation value
 * \param[in] expectationDataType data type of expect
 * \param[out] residualNorm result of matrix type test
 * \param[in] matrix observable as matrix
 * \param[in] matrixDataType data type of matrix
 * \param[in] layout matrix memory layout
 * \param[in] basisBits pointer to a host array of basis index bits
 * \param[in] nBasisBits the number of basis bits
 * \param[in] computeType computeType of matrix multiplication
 * \param[in] extraWorkspace pointer to an extra workspace
 * \param[in] extraWorkspaceSizeInBytes the size of extra workspace
 *
 * \details This function calculates expectation for a given matrix observable.
 * The acceptable values for the \p expectationDataType argument are CUDA_R_64F and CUDA_C_64F.
 *
 * The \p basisBits and \p nBasisBits arguments specify the basis to calculate expectation.  For the
 * \p computeType argument, the same combinations for custatevecApplyMatrix() are
 * available.
 *
 * This function may return ::CUSTATEVEC_STATUS_INSUFFICIENT_WORKSPACE for large \p nBasisBits.
 * In such cases, the \p extraWorkspace and \p extraWorkspaceSizeInBytes arguments should be specified
 * to provide extra workspace. The size of required extra workspace is obtained by
 * calling custatevecComputeExpectationGetWorkspaceSize().
 * A null pointer can be passed to the \p extraWorkspace argument if no extra workspace is
 * required.
 * Also, if a device memory handler is set, the \p extraWorkspace can be set to null, 
 * and the \p extraWorkspaceSizeInBytes can be set to 0.
 *
 * \note The \p residualNorm argument is not available in this version.
 * If a matrix given by the matrix argument may not be a Hermitian matrix,
 * please specify CUDA_C_64F to the \p expectationDataType argument and check the imaginary part of
 * the calculated expectation value.
 *
 * \note For Blackwell architecture, the input state vector has to be 128-byte aligned.
 * Otherwise, this function may return ::CUSTATEVEC_STATUS_INVALID_VALUE.
 */

custatevecStatus_t
custatevecComputeExpectation(custatevecHandle_t       handle,
                             const void*              sv,
                             cudaDataType_t           svDataType,
                             const uint32_t           nIndexBits,
                             void*                    expectationValue,
                             cudaDataType_t           expectationDataType,
                             double*                  residualNorm,
                             const void*              matrix,
                             cudaDataType_t           matrixDataType,
                             custatevecMatrixLayout_t layout,
                             const int32_t*           basisBits,
                             const uint32_t           nBasisBits,
                             custatevecComputeType_t  computeType,
                             void*                    extraWorkspace,
                             size_t                   extraWorkspaceSizeInBytes);


/*
 * Sampler
 */

/**
 * \brief Create sampler descriptor.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sv pointer to state vector
 * \param[in] svDataType data type of state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[out] sampler pointer to a new sampler descriptor
 * \param[in] nMaxShots the max number of shots used for this sampler context
 * \param[out] extraWorkspaceSizeInBytes workspace size
 *
 * \details This function creates a sampler descriptor.
 * If an extra workspace is required, its size is set to \p extraWorkspaceSizeInBytes.
 */

custatevecStatus_t 
custatevecSamplerCreate(custatevecHandle_t             handle,
                        const void*                    sv,
                        cudaDataType_t                 svDataType,
                        const uint32_t                 nIndexBits,
                        custatevecSamplerDescriptor_t* sampler,
                        uint32_t                       nMaxShots,
                        size_t*                        extraWorkspaceSizeInBytes);


/**
 * \brief This function releases resources used by the sampler.
 *
 * \param[in] sampler the sampler descriptor
 */
custatevecStatus_t
custatevecSamplerDestroy(custatevecSamplerDescriptor_t sampler);


/**
 * \brief Preprocess the state vector for preparation of sampling.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sampler the sampler descriptor
 * \param[in] extraWorkspace extra workspace
 * \param[in] extraWorkspaceSizeInBytes size of the extra workspace
 *
 * \details This function prepares internal states of the sampler descriptor.
 * If a device memory handler is set, the \p extraWorkspace can be set to null, 
 * and the \p extraWorkspaceSizeInBytes can be set to 0.
 * Otherwise, a pointer passed to the \p extraWorkspace argument is associated to the sampler handle
 * and should be kept during its life time.
 * The size of \p extraWorkspace is obtained when custatevecSamplerCreate() is called.
 */

custatevecStatus_t
custatevecSamplerPreprocess(custatevecHandle_t             handle,
                            custatevecSamplerDescriptor_t  sampler,
                            void*                          extraWorkspace,
                            const size_t                   extraWorkspaceSizeInBytes);


/**
 * \brief Get the squared norm of the state vector.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sampler the sampler descriptor
 * \param[out] norm the norm of the state vector
 *
 * \details This function returns the squared norm of the state vector.
 * An intended use case is sampling with multiple devices.
 * This API should be called after custatevecSamplerPreprocess().
 * Otherwise, the behavior of this function is undefined.
 */

custatevecStatus_t
custatevecSamplerGetSquaredNorm(custatevecHandle_t            handle,
                                custatevecSamplerDescriptor_t sampler,
                                double*                       norm);


/**
 * \brief Apply the partial norm and norm to the state vector to the sample descriptor.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sampler the sampler descriptor
 * \param[in] subSVOrd sub state vector ordinal
 * \param[in] nSubSVs the number of sub state vectors
 * \param[in] offset cumulative sum offset for the sub state vector
 * \param[in] norm norm for all sub vectors
 *
 * \details This function applies offsets assuming the given state vector is a sub state vector.
 * An intended use case is sampling with distributed state vectors.
 * The \p nSubSVs argument should be a power of 2 and \p subSVOrd should be less than \p nSubSVs.
 * Otherwise, this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 */

custatevecStatus_t
custatevecSamplerApplySubSVOffset(custatevecHandle_t            handle,
                                  custatevecSamplerDescriptor_t sampler,
                                  int32_t                       subSVOrd,
                                  uint32_t                      nSubSVs,
                                  double                        offset,
                                  double                        norm);

/**
 * \brief Sample bit strings from the state vector.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sampler the sampler descriptor
 * \param[out] bitStrings pointer to a host array to store sampled bit strings
 * \param[in] bitOrdering pointer to a host array of bit ordering for sampling
 * \param[in] bitStringLen the number of bits in bitOrdering
 * \param[in] randnums pointer to an array of random numbers
 * \param[in] nShots the number of shots
 * \param[in] output the order of sampled bit strings
 *
 * \details This function does sampling.
 * The \p bitOrdering and \p bitStringLen arguments specify bits to be sampled.
 * Sampled bit strings are represented as an array of ::custatevecIndex_t and
 * are stored to the host memory buffer that the \p bitStrings argument points to.
 *
 * The \p randnums argument is an array of user-generated random numbers whose length is \p nShots.
 * The range of random numbers should be in [0, 1).  A random number given by the \p randnums
 * argument is clipped to [0, 1) if its range is not in [0, 1).
 *
 * The \p output argument specifies the order of sampled bit strings:
 *   - If ::CUSTATEVEC_SAMPLER_OUTPUT_RANDNUM_ORDER is specified,
 * the order of sampled bit strings is the same as that in the \p randnums argument.
 *   - If ::CUSTATEVEC_SAMPLER_OUTPUT_ASCENDING_ORDER is specified, bit strings are returned in the ascending order.
 * 
 * If you don't need a particular order, choose ::CUSTATEVEC_SAMPLER_OUTPUT_RANDNUM_ORDER by default. (It may offer slightly better performance.)
 *
 * This API should be called after custatevecSamplerPreprocess().
 * Otherwise, the behavior of this function is undefined.
 * By calling custatevecSamplerApplySubSVOffset() prior to this function, it is possible to sample bits 
 * corresponding to the ordinal of sub state vector.  
 */

custatevecStatus_t 
custatevecSamplerSample(custatevecHandle_t             handle,
                        custatevecSamplerDescriptor_t  sampler,
                        custatevecIndex_t*             bitStrings,
                        const int32_t*                 bitOrdering,
                        const uint32_t                 bitStringLen,
                        const double*                  randnums,
                        const uint32_t                 nShots,
                        enum custatevecSamplerOutput_t output);



/*
 *  Beta2
 */


/**
 * \brief Get the extra workspace size required by custatevecApplyGeneralizedPermutationMatrix().
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[in] permutation host or device pointer to a permutation table
 * \param[in] diagonals host or device pointer to diagonal elements
 * \param[in] diagonalsDataType data type of diagonals
 * \param[in] targets pointer to a host array of target bits
 * \param[in] nTargets the number of target bits
 * \param[in] nControls the number of control bits
 * \param[out] extraWorkspaceSizeInBytes extra workspace size
 *
 * \details This function gets the size of extra workspace size required to execute
 * custatevecApplyGeneralizedPermutationMatrix().
 * \p extraWorkspaceSizeInBytes will be set to 0 if no extra buffer is required
 * for a given set of arguments.
 */

custatevecStatus_t
custatevecApplyGeneralizedPermutationMatrixGetWorkspaceSize(custatevecHandle_t        handle,
                                                            cudaDataType_t            svDataType,
                                                            const uint32_t            nIndexBits,
                                                            const custatevecIndex_t*  permutation,
                                                            const void*               diagonals,
                                                            cudaDataType_t            diagonalsDataType,
                                                            const int32_t*            targets,
                                                            const uint32_t            nTargets,
                                                            const uint32_t            nControls,
                                                            size_t*                   extraWorkspaceSizeInBytes);


/**
 * \brief Apply generalized permutation matrix.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[in] permutation host or device pointer to a permutation table
 * \param[in] diagonals host or device pointer to diagonal elements
 * \param[in] diagonalsDataType data type of diagonals
 * \param[in] adjoint apply adjoint of generalized permutation matrix
 * \param[in] targets pointer to a host array of target bits
 * \param[in] nTargets the number of target bits
 * \param[in] controls pointer to a host array of control bits
 * \param[in] controlBitValues pointer to a host array of control bit values
 * \param[in] nControls the number of control bits
 * \param[in] extraWorkspace extra workspace
 * \param[in] extraWorkspaceSizeInBytes extra workspace size
 *
 * \details This function applies the generalized permutation matrix.
 *
 * The generalized permutation matrix, \f$A\f$, is expressed as \f$A = DP\f$,
 * where \f$D\f$ and \f$P\f$ are diagonal and permutation matrices, respectively.
 *
 * The permutation matrix, \f$P\f$, is specified as a permutation table which is an array of
 * ::custatevecIndex_t and passed to the \p permutation argument.
 *
 * The diagonal matrix, \f$D\f$, is specified as an array of diagonal elements.
 * The length of both arrays is \f$ 2^{{\text nTargets}} \f$.
 * The \p diagonalsDataType argument specifies the type of diagonal elements.
 *
 * Below is the table of combinations of \p svDataType and \p diagonalsDataType arguments available in
 * this version.
 *
 *  \p svDataType  | \p diagonalsDataType
 *  ---------------|---------------------
 *  CUDA_C_64F     | CUDA_C_64F
 *  CUDA_C_32F     | CUDA_C_64F
 *  CUDA_C_32F     | CUDA_C_32F
 *
 * This function can also be used to only apply either the diagonal or the permutation matrix.
 * By passing a null pointer to the \p permutation argument, \f$P\f$ is treated as an identity matrix,
 * thus, only the diagonal matrix \f$D\f$ is applied. Likewise, if a null pointer is passed to the \p diagonals
 * argument, \f$D\f$ is treated as an identity matrix, and only the permutation matrix \f$P\f$ is applied.
 *
 * The permutation argument should hold integers in [0, \f$ 2^{nTargets} \f$).  An integer should appear
 * only once, otherwise the behavior of this function is undefined.
 *
 * The \p permutation and \p diagonals arguments should not be null at the same time.
 * In this case, this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 *
 * This function may return ::CUSTATEVEC_STATUS_INSUFFICIENT_WORKSPACE for large \p nTargets or
 * \p nIndexBits.  In such cases, the \p extraWorkspace and \p extraWorkspaceSizeInBytes arguments should be
 * specified to provide extra workspace.  The size of required extra workspace is obtained by
 * calling custatevecApplyGeneralizedPermutationMatrixGetWorkspaceSize().
 *
 * A null pointer can be passed to the \p extraWorkspace argument if no extra workspace is
 * required.
 * Also, if a device memory handler is set, the \p extraWorkspace can be set to null, 
 * and the \p extraWorkspaceSizeInBytes can be set to 0.
 *
 * \note In this version, custatevecApplyGeneralizedPermutationMatrix() does not return error if an
 * invalid \p permutation argument is specified.
 */

custatevecStatus_t
custatevecApplyGeneralizedPermutationMatrix(custatevecHandle_t       handle,
                                            void*                    sv,
                                            cudaDataType_t           svDataType,
                                            const uint32_t           nIndexBits,
                                            custatevecIndex_t*       permutation,
                                            const void*              diagonals,
                                            cudaDataType_t           diagonalsDataType,
                                            const int32_t            adjoint,
                                            const int32_t*           targets,
                                            const uint32_t           nTargets,
                                            const int32_t*           controls,
                                            const int32_t*           controlBitValues,
                                            const uint32_t           nControls,
                                            void*                    extraWorkspace,
                                            size_t                   extraWorkspaceSizeInBytes);


/**
 * \brief Calculate expectation values for a batch of (multi-qubit) Pauli operators.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sv state vector
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[out] expectationValues pointer to a host array to store expectation values
 * \param[in] pauliOperatorsArray pointer to a host array of Pauli operator arrays
 * \param[in] nPauliOperatorArrays the number of Pauli operator arrays
 * \param[in] basisBitsArray host array of basis bit arrays
 * \param[in] nBasisBitsArray host array of the number of basis bits
 *
 * This function calculates multiple expectation values for given sequences of
 * Pauli operators by a single call.
 *
 * A single Pauli operator sequence, pauliOperators, is represented by using an array
 * of ::custatevecPauli_t. The basis bits on which these Pauli operators are acting are
 * represented by an array of index bit positions. If no Pauli operator is specified
 * for an index bit, the identity operator (::CUSTATEVEC_PAULI_I) is implicitly assumed.
 *
 * The length of pauliOperators and basisBits are the same and specified by nBasisBits.
 *
 * The number of Pauli operator sequences is specified by the \p nPauliOperatorArrays argument.
 *
 * Multiple sequences of Pauli operators are represented in the form of arrays of arrays
 * in the following manners:
 *   - The \p pauliOperatorsArray argument is an array for arrays of ::custatevecPauli_t.
 *   - The \p basisBitsArray is an array of the arrays of basis bit positions.
 *   - The \p nBasisBitsArray argument holds an array of the length of Pauli operator sequences and
 *     basis bit arrays.
 *
 * Calculated expectation values are stored in a host buffer specified by the \p expectationValues
 * argument of length \p nPauliOpeartorsArrays.
 *
 * This function returns ::CUSTATEVEC_STATUS_INVALID_VALUE if basis bits specified
 * for a Pauli operator sequence has duplicates and/or out of the range of [0, \p nIndexBits).
 *
 * This function accepts empty Pauli operator sequence to get the norm of the state vector.
 */

custatevecStatus_t
custatevecComputeExpectationsOnPauliBasis(custatevecHandle_t        handle,
                                          const void*               sv,
                                          cudaDataType_t            svDataType,
                                          const uint32_t            nIndexBits,
                                          double*                   expectationValues,
                                          const custatevecPauli_t** pauliOperatorsArray,
                                          const uint32_t            nPauliOperatorArrays,
                                          const int32_t**           basisBitsArray,
                                          const uint32_t*           nBasisBitsArray);


/**
 * \brief Create accessor to copy elements between the state vector and an external buffer.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sv state vector
 * \param[in] svDataType Data type of state vector
 * \param[in] nIndexBits the number of index bits of state vector
 * \param[in] accessor pointer to an accessor descriptor
 * \param[in] bitOrdering pointer to a host array to specify the basis bits of the external buffer
 * \param[in] bitOrderingLen the length of bitOrdering
 * \param[in] maskBitString pointer to a host array to specify the mask values to limit access
 * \param[in] maskOrdering pointer to a host array for the mask ordering
 * \param[in] maskLen the length of mask
 * \param[out] extraWorkspaceSizeInBytes the required size of extra workspace
 *
 * Accessor copies state vector elements between the state vector and external buffers.
 * During the copy, the ordering of state vector elements are rearranged according to the bit
 * ordering specified by the \p bitOrdering argument.
 *
 * The state vector is assumed to have the default ordering: the LSB is the 0th index bit and the
 * (N-1)th index bit is the MSB for an N index bit system.  The bit ordering of the external
 * buffer is specified by the \p bitOrdering argument.
 * When 3 is given to the \p nIndexBits argument and [1, 2, 0] to the \p bitOrdering argument,
 * the state vector index bits are permuted to specified bit positions.  Thus, the state vector
 * index is rearranged and mapped to the external buffer index as [0, 4, 1, 5, 2, 6, 3, 7].
 *
 * The \p maskBitString, \p maskOrdering and \p maskLen arguments specify the bit mask for the state
 * vector index being accessed.
 * If the \p maskLen argument is 0, the \p maskBitString and/or \p maskOrdering arguments can be null.
 *
 * All bit positions [0, \p nIndexBits), should appear exactly once, either in the \p bitOrdering or the
 * \p maskOrdering arguments.
 * If a bit position does not appear in these arguments and/or there are overlaps of bit positions,
 * this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 *
 * The extra workspace improves performance if the accessor is called multiple times with 
 * small external buffers placed on device.
 * A null pointer can be specified to the \p extraWorkspaceSizeInBytes if the extra workspace is not
 * necessary.
 */
custatevecStatus_t
custatevecAccessorCreate(custatevecHandle_t              handle,
                         void*                           sv,
                         cudaDataType_t                  svDataType,
                         const uint32_t                  nIndexBits,
                         custatevecAccessorDescriptor_t* accessor,
                         const int32_t*                  bitOrdering,
                         const uint32_t                  bitOrderingLen,
                         const int32_t*                  maskBitString,
                         const int32_t*                  maskOrdering,
                         const uint32_t                  maskLen,
                         size_t*                         extraWorkspaceSizeInBytes);


/**
 * \brief Create accessor for the constant state vector
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] sv state vector
 * \param[in] svDataType Data type of state vector
 * \param[in] nIndexBits the number of index bits of state vector
 * \param[in] accessor pointer to an accessor descriptor
 * \param[in] bitOrdering pointer to a host array to specify the basis bits of the external buffer
 * \param[in] bitOrderingLen the length of bitOrdering
 * \param[in] maskBitString pointer to a host array to specify the mask values to limit access
 * \param[in] maskOrdering pointer to a host array for the mask ordering
 * \param[in] maskLen the length of mask
 * \param[out] extraWorkspaceSizeInBytes the required size of extra workspace
 *
 * This function is the same as custatevecAccessorCreate(), but only accepts the constant
 * state vector.
 */

custatevecStatus_t
custatevecAccessorCreateView(custatevecHandle_t              handle,
                             const void*                     sv,
                             cudaDataType_t                  svDataType,
                             const uint32_t                  nIndexBits,
                             custatevecAccessorDescriptor_t* accessor,
                             const int32_t*                  bitOrdering,
                             const uint32_t                  bitOrderingLen,
                             const int32_t*                  maskBitString,
                             const int32_t*                  maskOrdering,
                             const uint32_t                  maskLen,
                             size_t*                         extraWorkspaceSizeInBytes);


/**
 * \brief This function releases resources used by the accessor.
 *
 * \param[in] accessor the accessor descriptor
 */
custatevecStatus_t
custatevecAccessorDestroy(custatevecAccessorDescriptor_t accessor);


/**
 * \brief Set the external workspace to the accessor
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] accessor the accessor descriptor
 * \param[in] extraWorkspace extra workspace
 * \param[in] extraWorkspaceSizeInBytes extra workspace size
 *
 * This function sets the extra workspace to the accessor.
 * The required size for extra workspace can be obtained by custatevecAccessorCreate() or custatevecAccessorCreateView().
 * if a device memory handler is set, the \p extraWorkspace can be set to null, 
 * and the \p extraWorkspaceSizeInBytes can be set to 0.
 */

custatevecStatus_t
custatevecAccessorSetExtraWorkspace(custatevecHandle_t              handle,
                                    custatevecAccessorDescriptor_t  accessor,
                                    void*                           extraWorkspace,
                                    size_t                          extraWorkspaceSizeInBytes);


/**
 * \brief Copy state vector elements to an external buffer
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] accessor the accessor descriptor
 * \param[out] externalBuffer pointer to  a host or device buffer to receive copied elements
 * \param[in] begin index in the permuted bit ordering for the first elements being copied to the state vector
 * \param[in] end index in the permuted bit ordering for the last elements being copied to the state vector (non-inclusive)
 *
 * This function copies state vector elements to an external buffer specified by
 * the \p externalBuffer argument.  During the copy, the index bit is permuted as specified by
 * the \p bitOrdering argument in custatevecAccessorCreate() or custatevecAccessorCreateView().
 *
 * The \p begin and \p end arguments specify the range of state vector elements being copied.
 * Both arguments have the bit ordering specified by the \p bitOrdering argument.
 */

custatevecStatus_t
custatevecAccessorGet(custatevecHandle_t              handle,
                      custatevecAccessorDescriptor_t  accessor,
                      void*                           externalBuffer,
                      const custatevecIndex_t         begin,
                      const custatevecIndex_t         end);

/**
 * \brief Set state vector elements from an external buffer
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] accessor the accessor descriptor
 * \param[in] externalBuffer pointer to a host or device buffer of complex values being copied to the state vector
 * \param[in] begin index in the permuted bit ordering for the first elements being copied from the state vector
 * \param[in] end index in the permuted bit ordering for the last elements being copied from the state vector (non-inclusive)
 *
 * This function sets complex numbers to the state vector by using an external buffer specified by
 * the \p externalBuffer argument.  During the copy, the index bit is permuted as specified by
 * the \p bitOrdering argument in custatevecAccessorCreate().
 *
 * The \p begin and \p end arguments specify the range of state vector elements being set
 * to the state vector. Both arguments have the bit ordering specified by the \p bitOrdering
 * argument.
 *
 * If a read-only accessor created by calling custatevecAccessorCreateView() is provided, this
 * function returns ::CUSTATEVEC_STATUS_NOT_SUPPORTED.
 */

custatevecStatus_t
custatevecAccessorSet(custatevecHandle_t              handle,
                      custatevecAccessorDescriptor_t  accessor,
                      const void*                     externalBuffer,
                      const custatevecIndex_t         begin,
                      const custatevecIndex_t         end);

/**
 * \brief Swap index bits and reorder state vector elements in one device
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType Data type of state vector
 * \param[in] nIndexBits the number of index bits of state vector
 * \param[in] bitSwaps pointer to a host array of swapping bit index pairs
 * \param[in] nBitSwaps the number of bit swaps
 * \param[in] maskBitString pointer to a host array to mask output
 * \param[in] maskOrdering  pointer to a host array to specify the ordering of maskBitString
 * \param[in] maskLen the length of mask
 * 
 * This function updates the bit ordering of the state vector by swapping the pairs of bit positions.
 * 
 * The state vector is assumed to have the default ordering: the LSB is the 0th index bit and the
 * (N-1)th index bit is the MSB for an N index bit system. 
 * The \p bitSwaps argument specifies the swapped bit index pairs, whose values must be in the range
 * [0, \p nIndexBits).
 *
 * The \p maskBitString, \p maskOrdering and \p maskLen arguments specify the bit mask for the state
 * vector index being permuted.
 * If the \p maskLen argument is 0, the \p maskBitString and/or \p maskOrdering arguments can be null.
 * 
 * A bit position can be included in both \p bitSwaps and \p maskOrdering.
 * When a masked bit is swapped, state vector elements whose original indices match the mask bit string 
 * are written to the permuted indices while other elements are not copied.
 */

custatevecStatus_t
custatevecSwapIndexBits(custatevecHandle_t handle,
                        void*              sv,
                        cudaDataType_t     svDataType,
                        const uint32_t     nIndexBits,
                        const int2*        bitSwaps,
                        const uint32_t     nBitSwaps,
                        const int32_t*     maskBitString,
                        const int32_t*     maskOrdering,
                        const uint32_t     maskLen);

/*
 * Matrix type test
 */

/**
 * \brief Get extra workspace size for custatevecTestMatrixType()
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[in] matrixType matrix type
 * \param[in] matrix host or device pointer to a matrix
 * \param[in] matrixDataType data type of matrix
 * \param[in] layout enumerator specifying the memory layout of matrix
 * \param[in] nTargets the number of target bits, up to 15
 * \param[in] adjoint flag to control whether the adjoint of matrix is tested
 * \param[in] computeType compute type
 * \param[out] extraWorkspaceSizeInBytes workspace size
 *
 * \details This function gets the size of an extra workspace required to execute
 * custatevecTestMatrixType().
 * \p extraWorkspaceSizeInBytes will be set to 0 if no extra buffer is required.
 */

custatevecStatus_t
custatevecTestMatrixTypeGetWorkspaceSize(custatevecHandle_t       handle,
                                         custatevecMatrixType_t   matrixType,
                                         const void*              matrix,
                                         cudaDataType_t           matrixDataType,
                                         custatevecMatrixLayout_t layout,
                                         const uint32_t           nTargets,
                                         const int32_t            adjoint,
                                         custatevecComputeType_t  computeType,
                                         size_t*                  extraWorkspaceSizeInBytes);

/**
 * \brief Test the deviation of a given matrix from a Hermitian (or Unitary) matrix.
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[out] residualNorm host pointer, to store the deviation from certain matrix type
 * \param[in] matrixType matrix type
 * \param[in] matrix host or device pointer to a matrix
 * \param[in] matrixDataType data type of matrix
 * \param[in] layout enumerator specifying the memory layout of matrix
 * \param[in] nTargets the number of target bits, up to 15
 * \param[in] adjoint flag to control whether the adjoint of matrix is tested
 * \param[in] computeType compute type
 * \param[in] extraWorkspace extra workspace
 * \param[in] extraWorkspaceSizeInBytes extra workspace size
 *
 * \details This function tests if the type of a given matrix matches the type given by
 * the \p matrixType argument.
 *
 * For tests for the unitary type, \f$ R = (AA^{\dagger} - I) \f$ is calculated where \f$ A \f$ is the given matrix.
 * The sum of absolute values of \f$ R \f$ matrix elements is returned.
 *
 * For tests for the Hermitian type, \f$ R = (M - M^{\dagger}) / 2 \f$ is calculated. The sum of squared
 * absolute values of \f$ R \f$ matrix elements is returned.
 *
 * This function may return ::CUSTATEVEC_STATUS_INSUFFICIENT_WORKSPACE for large \p nTargets.
 * In such cases, the \p extraWorkspace and \p extraWorkspaceSizeInBytes arguments should be specified
 * to provide extra workspace.
 * The required size of an extra workspace is obtained by calling custatevecTestMatrixTypeGetWorkspaceSize().
 * A null pointer can be passed to the \p extraWorkspace argument if no extra workspace is required.
 * Also, if a device memory handler is set, the \p extraWorkspace can be set to null, 
 * and the \p extraWorkspaceSizeInBytes can be set to 0.
 * 
 * \note The \p nTargets argument must be no more than 15 in this version.
 * For larger \p nTargets, this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 */

custatevecStatus_t
custatevecTestMatrixType(custatevecHandle_t       handle,
                         double*                  residualNorm,
                         custatevecMatrixType_t   matrixType,
                         const void*              matrix,
                         cudaDataType_t           matrixDataType,
                         custatevecMatrixLayout_t layout,
                         const uint32_t           nTargets,
                         const int32_t            adjoint,
                         custatevecComputeType_t  computeType,
                         void*                    extraWorkspace,
                         size_t                   extraWorkspaceSizeInBytes);

/**
 * \brief Initialize the state vector to a certain form.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] sv state vector
 * \param[in] svDataType data type of state vector
 * \param[in] nIndexBits the number of index bits
 * \param[in] svType the target quantum state
 */
custatevecStatus_t
custatevecInitializeStateVector(custatevecHandle_t          handle,
                                void*                       sv,
                                cudaDataType_t              svDataType,
                                const uint32_t              nIndexBits,
                                custatevecStateVectorType_t svType);

/** \} singlegpuapi */

/**
 * \defgroup multigpuapi Multi GPU API
 *
 * \{ */

/**
 * \brief Swap index bits and reorder state vector elements for multiple sub state vectors
 *        distributed to multiple devices
 *
 * \param[in] handles pointer to a host array of custatevecHandle_t
 * \param[in] nHandles the number of handles specified in the handles argument
 * \param[in,out] subSVs pointer to an array of sub state vectors
 * \param[in] svDataType the data type of the state vector specified by the subSVs argument
 * \param[in] nGlobalIndexBits the number of global index bits of distributed state vector
 * \param[in] nLocalIndexBits the number of local index bits in sub state vector
 * \param[in] indexBitSwaps pointer to a host array of index bit pairs being swapped
 * \param[in] nIndexBitSwaps the number of index bit swaps
 * \param[in] maskBitString pointer to a host array to mask output
 * \param[in] maskOrdering  pointer to a host array to specify the ordering of maskBitString
 * \param[in] maskLen the length of mask
 * \param[in] deviceNetworkType the device network topology
 *
 * This function updates the bit ordering of the state vector distributed in multiple devices
 * by swapping the pairs of bit positions.
 *
 * This function assumes the state vector is split into multiple sub state vectors and distributed
 * to multiple devices to represent a (\p nGlobalIndexBits + \p nLocalIndexBits) qubit system.
 *
 * The \p handles argument should receive cuStateVec handles created for all devices where sub
 * state vectors are allocated. If two or more cuStateVec handles created for the same device are
 * given, this function will return an error, ::CUSTATEVEC_STATUS_INVALID_VALUE.
 * The \p handles argument should contain a handle created on the current device, as all operations
 * in this function will be ordered on the stream of the current device's handle.
 * Otherwise, this function returns an error, ::CUSTATEVEC_STATUS_INVALID_VALUE.
 *
 * Sub state vectors are specified by the \p subSVs argument as an array of device pointers.
 * All sub state vectors are assumed to hold the same number of index bits specified by the \p
 * nLocalIndexBits. Thus, each sub state vectors holds (1 << \p nLocalIndexBits) state vector
 * elements. The global index bits is identical to the index of sub state vectors.  The number
 * of sub state vectors is given as (1 << \p nGlobalIndexBits). The max value of
 * \p nGlobalIndexBits is 5, which corresponds to 32 sub state vectors.
 *
 * The index bit of the distributed state vector has the default ordering: The index bits of the
 * sub state vector are mapped from the 0th index bit to the (\p nLocalIndexBits-1)-th index bit.
 * The global index bits are mapped from the (\p nLocalIndexBits)-th bit to the
 * (\p nGlobalIndexBits + \p nLocalIndexBits - 1)-th bit.
 *
 * The \p indexBitSwaps argument specifies the index bit pairs being swapped. Each index bit pair
 * can be a pair of two global index bits or a pair of a global and a local index bit.
 * A pair of two local index bits is not accepted. Please use custatevecSwapIndexBits()
 * for swapping local index bits.
 *
 * The \p maskBitString, \p maskOrdering and \p maskLen arguments specify the bit string mask that
 * limits the state vector elements swapped during the call.
 * Bits in \p maskOrdering can overlap index bits specified in the \p indexBitSwaps argument.
 * In such cases, the mask bit string is applied for the bit positions before index bit swaps.
 * If the \p maskLen argument is 0, the \p maskBitString and/or \p maskOrdering arguments can be
 * null.
 *
 * The \p deviceNetworkType argument specifies the device network topology to optimize the data
 * transfer sequence. The following two network topologies are assumed:
 * - Switch network: devices connected via NVLink with an NVSwitch (ex. DGX A100 and DGX-2) or
 *   PCIe device network with a single PCIe switch
 * - Full mesh network: all devices are connected by full mesh connections
 *   (ex. DGX Station V100/A100)
 *
 * \note **Important notice**
 * This function assumes \em bidirectional GPUDirect P2P is supported and enabled by
 * ``cudaDeviceEnablePeerAccess()`` between all devices where sub state vectors are allocated.
 * If GPUDirect P2P is not enabled, the call to ``custatevecMultiDeviceSwapIndexBits()`` that
 * accesses otherwise inaccessible device memory allocated in other GPUs would result in a
 * segmentation fault.
 *
 * \note
 * For the best performance, please use \f$2^n\f$ number of devices and allocate one sub state vector
 * in each device. This function allows the use of non-\f$2^n\f$ number of devices, to allocate two or
 * more sub state vectors on a device, or to allocate all sub state vectors on a single device
 * to cover various hardware configurations. However, the performance is always the best when
 * a single sub state vector is allocated on each \f$2^n\f$ number of devices.
 *
 * \note
 * The copy on each participating device is enqueued on the CUDA stream bound to the corresponding
 * handle via custatevecSetStream().
 * All CUDA calls before the call of this function are correctly ordered if these calls are issued
 * on the streams set to \p handles. This function is asynchronously executed. Please use
 * `cudaStreamSynchronize()` (for synchronization) or `cudaStreamWaitEvent()` (for establishing
 * the stream order) with the stream set to the handle of the current device.
 */

custatevecStatus_t
custatevecMultiDeviceSwapIndexBits(custatevecHandle_t*                 handles,
                                   const uint32_t                      nHandles,
                                   void**                              subSVs,
                                   const cudaDataType_t                svDataType,
                                   const uint32_t                      nGlobalIndexBits,
                                   const uint32_t                      nLocalIndexBits,
                                   const int2*                         indexBitSwaps,
                                   const uint32_t                      nIndexBitSwaps,
                                   const int32_t*                      maskBitString,
                                   const int32_t*                      maskOrdering,
                                   const uint32_t                      maskLen,
                                   const custatevecDeviceNetworkType_t deviceNetworkType);

/** \} multigpuapi */

/**
 * \defgroup distributed_swap_index_bits_api Distributed swap index bits API
 *
 * \{ */

/*
 * custatevecCommunicator
 */

/**
 * \typedef custatevecCommunicatorDescriptor_t
 * \brief This descriptor manages inter-process communications,
 * initialized by using custatevecCommunicatorCreate() and
 * destroyed by using custatevecCommunicatorDestroy().
 */
typedef struct custatevecCommunicator_t* custatevecCommunicatorDescriptor_t;

/**
 * \typedef custatevecCommunicatorType_t
 * \brief Constant to specify the communicator used in inter-process communications. 
 */
typedef enum custatevecCommunicatorType_t
{
    CUSTATEVEC_COMMUNICATOR_TYPE_EXTERNAL = 0, //!< An user-provided communicator will be used for inter-process communications.
    CUSTATEVEC_COMMUNICATOR_TYPE_OPENMPI  = 1, //!< Open MPI will be used for inter-process communications.
    CUSTATEVEC_COMMUNICATOR_TYPE_MPICH    = 2, //!< MPICH will be used for inter-process communications.
} custatevecCommunicatorType_t;

/**
 * \typedef custatevecDataTransferType_t
 * \brief Constant to specify the data transfer direction in point-to-point communication. 
 */
typedef enum custatevecDataTransferType_t {
    CUSTATEVEC_DATA_TRANSFER_TYPE_NONE = 0, //!< Data transfer worker will not send or receive any data.
    CUSTATEVEC_DATA_TRANSFER_TYPE_SEND = 1, //!< Data transfer worker will send data.
    CUSTATEVEC_DATA_TRANSFER_TYPE_RECV = 2, //!< Data transfer worker will receive data.
    CUSTATEVEC_DATA_TRANSFER_TYPE_SEND_RECV = CUSTATEVEC_DATA_TRANSFER_TYPE_SEND | CUSTATEVEC_DATA_TRANSFER_TYPE_RECV,
} custatevecDataTransferType_t;


#define CUSTATEVEC_MAX_SEGMENT_MASK_SIZE (48)

/**
 * \typedef custatevecSVSwapParameters_t
 * \brief This struct holds necessary information to execute data transfers between a pair of devices.
 */
typedef struct custatevecSVSwapParameters_t
{
    int32_t                       swapBatchIndex;   //!< swapBatchIndex specified by an argument of custatevecDistIndexBitSwapSchedulerGetParameters()
    int32_t                       orgSubSVIndex;    //!< origin subSV index specified by an argument of custatevecDistIndexBitSwapSchedulerGetParameters()
    int32_t                       dstSubSVIndex;    //!< destination subSV index
    int32_t                       orgSegmentMaskString[CUSTATEVEC_MAX_SEGMENT_MASK_SIZE];  //!< segment mask string in the origin
    int32_t                       dstSegmentMaskString[CUSTATEVEC_MAX_SEGMENT_MASK_SIZE];  //!< segment mask string in the destination
    int32_t                       segmentMaskOrdering[CUSTATEVEC_MAX_SEGMENT_MASK_SIZE];   //!< mask ordering for segment mask strings
    uint32_t                      segmentMaskLen;   //!< segment mask length
    uint32_t                      nSegmentBits;     //!< the number of index bits in the segment
    custatevecDataTransferType_t  dataTransferType; //!< the type of this data transfer
    custatevecIndex_t             transferSize;     //!< the number of elements being transferred, <tt>transferSize = 1 << (nSegmentBits - segmentMaskLen)</tt>.
} custatevecSVSwapParameters_t;

/**
 * \typedef custatevecDistIndexBitSwapSchedulerDescriptor_t
 * \brief This descriptor holds the context of scheduler for distributed index bit swaps, initialized using 
 * custatevecDistIndexBitSwapSchedulerCreate() and destroyed using custatevecDistIndexBitSwapSchedulerDestroy(),
 * respectively.
 */
typedef struct custatevecDistIndexBitSwapScheduler_t* custatevecDistIndexBitSwapSchedulerDescriptor_t;

/**
 * \typedef custatevecSVSwapWorkerDescriptor_t
 * \brief This descriptor holds the context of data transfer worker for distributed index bit swaps, initialized using 
 * custatevecSVSwapWorkerCreate() and destroyed using custatevecSVSwapWorkerDestroy(), respectively.
 */
typedef struct custatevecSVSwapWorker_t* custatevecSVSwapWorkerDescriptor_t;


/*
 *  custatevecCommunicator
 */

/**
 * \brief Create communicator.
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[out] communicator a pointer to the communicator
 * \param[in] communicatorType the communicator type
 * \param[in] soname the shared object name
 *
 * This function creates a communicator instance.
 *
 * The type of the communicator is specified by the \p communicatorType argument.
 * By specifying ::CUSTATEVEC_COMMUNICATOR_TYPE_OPENMPI or ::CUSTATEVEC_COMMUNICATOR_TYPE_MPICH
 * this function creates a communicator instance that internally uses Open MPI or MPICH,
 * respectively.
 * By specifying ::CUSTATEVEC_COMMUNICATOR_TYPE_EXTERNAL, this function loads
 * a custom plugin that wraps an MPI library. The source code for the custom
 * plugin is downloadable from [NVIDIA/cuQuantum](https://github.com/NVIDIA/cuQuantum).
 *
 * The \p soname argument specifies the name of the shared library that will be
 * used by the communicator instance.
 *
 * This function uses \p dlopen() to load the specified shared library. If Open MPI or
 * MPICH library is directly linked to an application and
 * ::CUSTATEVEC_COMMUNICATOR_TYPE_OPENMPI or ::CUSTATEVEC_COMMUNICATOR_TYPE_MPICH is
 * specified to the \p communicatorType argument, the \p soname argument should be
 * set to NULL. Thus, function symbols are resolved by searching the functions
 * loaded to the application at startup time.
 */


custatevecStatus_t
custatevecCommunicatorCreate(
        custatevecHandle_t                  handle,
        custatevecCommunicatorDescriptor_t* communicator,
        custatevecCommunicatorType_t        communicatorType,
        const char*                         soname);


/**
 * \brief This function releases communicator.
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[in] communicator the communicator descriptor
 */

custatevecStatus_t
custatevecCommunicatorDestroy(
        custatevecHandle_t                 handle,
        custatevecCommunicatorDescriptor_t communicator);


/*
 *  custatevecDistIndexBitSwapScheduler
 */

/**
 * \brief Create distributed index bit swap scheduler.
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[out] scheduler a pointer to a batch swap scheduler 
 * \param[in] nGlobalIndexBits the number of global index bits
 * \param[in] nLocalIndexBits the number of local index bits
 *
 * This function creates a distributed index bit swap scheduler descriptor.
 *
 * The local index bits are from the 0th index bit to the (\p nLocalIndexBits-1)-th index bit.
 * The global index bits are mapped from the (\p nLocalIndexBits)-th bit to the
 * (\p nGlobalIndexBits + \p nLocalIndexBits - 1)-th bit.
 */

custatevecStatus_t
custatevecDistIndexBitSwapSchedulerCreate(
        custatevecHandle_t                               handle,
        custatevecDistIndexBitSwapSchedulerDescriptor_t* scheduler,
        const uint32_t                                   nGlobalIndexBits,
        const uint32_t                                   nLocalIndexBits);


/**
 * \brief This function releases distributed index bit swap scheduler.
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[in] scheduler a pointer to the batch swap scheduler to destroy
 */

custatevecStatus_t
custatevecDistIndexBitSwapSchedulerDestroy(
        custatevecHandle_t                              handle,
        custatevecDistIndexBitSwapSchedulerDescriptor_t scheduler);

/**
 * \brief Set index bit swaps to distributed index bit swap scheduler.
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[in] scheduler a pointer to batch swap scheduler descriptor
 * \param[in] indexBitSwaps pointer to a host array of index bit pairs being swapped
 * \param[in] nIndexBitSwaps the number of index bit swaps
 * \param[in] maskBitString pointer to a host array to mask output
 * \param[in] maskOrdering  pointer to a host array to specify the ordering of maskBitString
 * \param[in] maskLen the length of mask
 * \param[out] nSwapBatches the number of batched data transfers
 *
 * This function sets index bit swaps to the distributed index bit swap scheduler and 
 * computes the number of necessary batched data transfers for the given index bit swaps.
 *
 * The index bit of the distributed state vector has the default ordering: The index bits of the
 * sub state vector are mapped from the 0th index bit to the (\p nLocalIndexBits-1)-th index bit.
 * The global index bits are mapped from the (\p nLocalIndexBits)-th bit to the
 * (\p nGlobalIndexBits + \p nLocalIndexBits - 1)-th bit.
 *
 * The \p indexBitSwaps argument specifies the index bit pairs being swapped. Each index bit pair
 * can be a pair of two global index bits or a pair of a global and a local index bit.
 * A pair of two local index bits is not accepted. Please use custatevecSwapIndexBits()
 * for swapping local index bits.
 *
 * The \p maskBitString, \p maskOrdering and \p maskLen arguments specify the bit string mask that
 * limits the state vector elements swapped during the call.
 * Bits in \p maskOrdering can overlap index bits specified in the \p indexBitSwaps argument.
 * In such cases, the mask bit string is applied for the bit positions before index bit swaps.
 * If the \p maskLen argument is 0, the \p maskBitString and/or \p maskOrdering arguments can be
 * null.
 *
 * The returned value by the \p nSwapBatches argument represents the number of loops
 * required to complete index bit swaps and is used in later stages.
 */

custatevecStatus_t
custatevecDistIndexBitSwapSchedulerSetIndexBitSwaps(
        custatevecHandle_t                              handle,
        custatevecDistIndexBitSwapSchedulerDescriptor_t scheduler,
        const int2*                                     indexBitSwaps,
        const uint32_t                                  nIndexBitSwaps,
        const int32_t*                                  maskBitString,
        const int32_t*                                  maskOrdering,
        const uint32_t                                  maskLen,
        uint32_t*                                       nSwapBatches);


/**
 * \brief Get parameters to be set to the state vector swap worker
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[in] scheduler a pointer to batch swap scheduler descriptor
 * \param[in] swapBatchIndex swap batch index for state vector swap parameters
 * \param[in] orgSubSVIndex the index of the origin sub state vector to swap state vector segments
 * \param[out] parameters a pointer to data transfer parameters
 *
 * This function computes parameters used for data transfers between sub state vectors.
 * The value of the \p swapBatchIndex argument should be in range of [0, \p nSwapBatches) where
 * \p nSwapBatches is the number of loops obtained by the call to
 * custatevecDistIndexBitSwapSchedulerSetIndexBitSwaps().
 *
 * The \p parameters argument returns the computed parameters for data transfer, which is set
 * to \p custatevecSVSwapWorker by the call to custatevecSVSwapWorkerSetParameters().
 */

custatevecStatus_t
custatevecDistIndexBitSwapSchedulerGetParameters(
        custatevecHandle_t                              handle,
        custatevecDistIndexBitSwapSchedulerDescriptor_t scheduler,
        const int32_t                                   swapBatchIndex,
        const int32_t                                   orgSubSVIndex,
        custatevecSVSwapParameters_t*                   parameters);


/*
 *  custatevecSVSwapWorker
 */

/**
 * \brief Create state vector swap worker.
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[out] svSwapWorker state vector swap worker
 * \param[in] communicator a pointer to the MPI communicator
 * \param[in] orgSubSV a pointer to a sub state vector
 * \param[in] orgSubSVIndex the index of the sub state vector specified by the orgSubSV argument
 * \param[in] orgEvent the event for synchronization with the peer worker
 * \param[in] svDataType data type used by the state vector representation
 * \param[in] stream a stream that is used to locally execute kernels during data transfers
 * \param[out] extraWorkspaceSizeInBytes the size of the extra workspace needed
 * \param[out] minTransferWorkspaceSizeInBytes the minimum-required size of the transfer workspace
 *
 * This function creates a ::custatevecSVSwapWorkerDescriptor_t that swaps/sends/receives state vector
 * elements between multiple sub state vectors. The communicator specified as the \p communicator argument
 * is used for inter-process communication, thus state vector elements are transferred between sub state
 * vectors distributed to multiple processes and nodes.
 *
 * The created descriptor works on the device where the handle is created. The origin sub state vector
 * specified by the \p orgSubSV argument should be allocated on the same device. The same applies to
 * the event and the stream specified by the \p orgEvent and \p stream arguments respectively.
 *
 * There are two workspaces, extra workspace and data transfer workspace. The extra workspace has constant
 * size and is used to keep the internal state of the descriptor. The data transfer workspace is used to
 * stage state vector elements being transferred. Its minimum size is given by the
 * \p minTransferWorkspaceSizeInBytes argument. Depending on the system, increasing the size of data
 * transfer workspace can improve performance.
 *
 * If SVSwapWorker is used in a single process, the \p communicator argument can be set to null.
 * In this case, the internal CUDA calls are serialized on the stream specified by the \p stream argument.
 *
 * If sub state vectors are distributed to multiple processes, the event should be created with the
 * \p cudaEventInterprocess flag.
 * Please refer to the [CUDA Toolkit documentation](https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__EVENT.html)
 * for the details.
 */

custatevecStatus_t
custatevecSVSwapWorkerCreate(
        custatevecHandle_t                  handle,
        custatevecSVSwapWorkerDescriptor_t* svSwapWorker,
        custatevecCommunicatorDescriptor_t  communicator,
        void*                               orgSubSV,
        int32_t                             orgSubSVIndex,
        cudaEvent_t                         orgEvent,
        cudaDataType_t                      svDataType,
        cudaStream_t                        stream,
        size_t*                             extraWorkspaceSizeInBytes,
        size_t*                             minTransferWorkspaceSizeInBytes);

/**
 * \brief Create state vector swap worker with semaphore.
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[out] svSwapWorker state vector swap worker
 * \param[in] communicator a pointer to the MPI communicator
 * \param[in] orgSubSV a pointer to a sub state vector
 * \param[in] orgSubSVIndex the index of the sub state vector specified by the orgSubSV argument
 * \param[in] orgSemaphore a pointer to a device memory chunk that used for synchronization with the peer worker
 * \param[in] svDataType data type used by the state vector representation
 * \param[in] stream a stream that is used to locally execute kernels during data transfers
 * \param[out] extraWorkspaceSizeInBytes the size of the extra workspace needed
 * \param[out] minTransferWorkspaceSizeInBytes the minimum-required size of the transfer workspace
 *
 * This function creates a ::custatevecSVSwapWorkerDescriptor_t that swaps/sends/receives state vector
 * elements between multiple sub state vectors. This function is an alternative version of custatevecSVSwapWorkerCreate
 * that uses semaphore for synchronization instead of CUDA IPC event.
 * The communicator specified as the \p communicator argument
 * is used for inter-process communication, thus state vector elements are transferred between sub state
 * vectors distributed to multiple processes and nodes.
 *
 * The created descriptor works on the device where the handle is created. The origin sub state vector
 * specified by the \p orgSubSV argument should be allocated on the same device. The same applies to
 * the device memory and the stream specified by the \p orgSemaphore and \p stream arguments respectively.
 *
 * The \p orgSemaphore argument should be a pointer to a device memory chunk whose size is 4 bytes or larger.
 *  As the semaphore is used for synchronization between processes, the allocation should be shared among processes
 * by using \p cudaIpcGetMemHandle() and \p cudaIpcOpenMemHandle() in CUDA Runtime API,
 * or \p cuMemExportToShareableHandle() and \p cuMemImportFromSharableHandle() in CUDA Driver API.
 *
 * There are two workspaces, extra workspace and data transfer workspace. The extra workspace has constant
 * size and is used to keep the internal state of the descriptor. The data transfer workspace is used to
 * stage state vector elements being transferred. Its minimum size is given by the
 * \p minTransferWorkspaceSizeInBytes argument. Depending on the system, increasing the size of data
 * transfer workspace can improve performance.
 *
 * SVSwapWorker can be used in a single process.  For this case, the \p communicator argument
 * can be set to NULL. The internal CUDA calls are serialized on the stream given as the \p stream argument.
 * If NULL is passed to the \p communicator argument, the \p orgSemaphore argument should be set to NULL.
 *
 * The \p orgSemaphore can be set to nullptr to disable synchronization between SVSwapWorker instances.
 */

custatevecStatus_t
custatevecSVSwapWorkerCreateWithSemaphore(
        custatevecHandle_t                  handle,
        custatevecSVSwapWorkerDescriptor_t* svSwapWorker,
        custatevecCommunicatorDescriptor_t  communicator,
        void*                               orgSubSV,
        int32_t                             orgSubSVIndex,
        void*                               orgSemaphore,
        cudaDataType_t                      svDataType,
        cudaStream_t                        stream,
        size_t*                             extraWorkspaceSizeInBytes,
        size_t*                             minTransferWorkspaceSizeInBytes);


/**
 * \brief This function releases the state vector swap worker.
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[in] svSwapWorker state vector swap worker
 */
custatevecStatus_t
custatevecSVSwapWorkerDestroy(
        custatevecHandle_t                 handle,
        custatevecSVSwapWorkerDescriptor_t svSwapWorker);

/**
 * \brief Set extra workspace.
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[in] svSwapWorker state vector swap worker
 * \param[in] extraWorkspace pointer to the user-owned workspace
 * \param[in] extraWorkspaceSizeInBytes size of the user-provided workspace
 *
 * This function sets the extra workspace to the state vector swap worker.
 * The required size for extra workspace can be obtained by custatevecSVSwapWorkerCreate().
 *
 * The extra workspace should be set before calling custatevecSVSwapWorkerSetParameters().
 */
custatevecStatus_t
custatevecSVSwapWorkerSetExtraWorkspace(
        custatevecHandle_t                 handle,
        custatevecSVSwapWorkerDescriptor_t svSwapWorker,
        void*                              extraWorkspace,
        size_t                             extraWorkspaceSizeInBytes);

/**
 * \brief Set transfer workspace.
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[in] svSwapWorker state vector swap worker
 * \param[in] transferWorkspace pointer to the user-owned workspace
 * \param[in] transferWorkspaceSizeInBytes size of the user-provided workspace
 *
 * This function sets the transfer workspace to the state vector swap worker instance.
 * The minimum size for transfer workspace can be obtained by custatevecSVSwapWorkerCreate().
 *
 * Depending on the system hardware configuration, larger size of the transfer workspace can improve
 * the performance. The size specified by the \p transferWorkspaceSizeInBytes should a power of two number
 * and should be equal to or larger than the value of the \p minTransferWorkspaceSizeInBytes returned
 * by the call to \p custatevecSVSwapWorkerCreate().
 */

custatevecStatus_t
custatevecSVSwapWorkerSetTransferWorkspace(
        custatevecHandle_t                 handle,
        custatevecSVSwapWorkerDescriptor_t svSwapWorker,
        void*                              transferWorkspace,
        size_t                             transferWorkspaceSizeInBytes);

/**
 * \brief Set sub state vector pointers accessible via GPUDirect P2P with CUDA IPC events
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[in] svSwapWorker state vector swap worker
 * \param[in] dstSubSVsP2P an array of pointers to sub state vectors that are accessed by GPUDirect P2P
 * \param[in] dstSubSVIndicesP2P the sub state vector indices of sub state vector pointers specified by the dstSubSVsP2P argument
 * \param[in] dstEvents events used to create peer workers
 * \param[in] nDstSubSVsP2P the number of sub state vector pointers specified by the dstSubSVsP2P argument
 *
 * This function sets sub state vector pointers that are accessible by GPUDirect P2P from the device where the
 * state vector swap worker works. The sub state vector pointers should be specified together with the sub state
 * vector indices and events which are passed to custatevecSVSwapWorkerCreate() to create peer SV swap
 * worker instances.
 *
 * If sub state vectors are allocated in different processes, the sub state vector pointers should be shared
 * among processes by using \p cudaIpcGetMemHandle() and \p cudaIpcOpenMemHandle() in CUDA Runtime API,
 * or \p cuMemExportToShareableHandle() and \p cuMemImportFromSharableHandle() in CUDA Driver API.
 * Correspondingly CUDA events in the \p dstEvents argument should be retribed by CUDA IPC.
 */

custatevecStatus_t
custatevecSVSwapWorkerSetSubSVsP2P(
        custatevecHandle_t                 handle,
        custatevecSVSwapWorkerDescriptor_t svSwapWorker,
        void**                             dstSubSVsP2P,
        const int32_t*                     dstSubSVIndicesP2P,
        cudaEvent_t*                       dstEvents,
        const uint32_t                     nDstSubSVsP2P);



/**
 * \brief Set sub state vector pointers accessible via GPUDirect P2P with semaphores
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[in] svSwapWorker state vector swap worker
 * \param[in] dstSubSVsP2P an array of pointers to sub state vectors that are accessed by GPUDirect P2P
 * \param[in] dstSubSVIndicesP2P the sub state vector indices of sub state vector pointers specified by the dstSubSVsP2P argument
 * \param[in] dstSemaphores semaphores used to create peer workers
 * \param[in] nDstSubSVsP2P the number of sub state vector pointers specified by the dstSubSVsP2P argument
 *
 * This function sets sub state vector pointers that are accessible by GPUDirect P2P from the device where the
 * state vector swap worker works. The sub state vector pointers should be specified together with the sub state
 * vector indices and semaphores which are passed to custatevecSVSwapWorkerCreateWithSemaphore() to
 * create peer SV swap worker instances.
 *
 * If sub state vectors are allocated in different processes, the sub state vector pointers and the semaphore should
 * be imported from other processes by using \p cudaIpcGetMemHandle() and \p cudaIpcOpenMemHandle() in CUDA Runtime API,
 * or \p cuMemExportToShareableHandle() and \p cuMemImportFromSharableHandle() in CUDA Driver API.
 *
 * If the \p orgSemaphore argument is set to NULL when calling  \p custatevecSVSwapWorkerCreateWithSemaphore(),
 * the \p dstSemaphores argument should be set to NULL.
 */

custatevecStatus_t
custatevecSVSwapWorkerSetSubSVsP2PWithSemaphores(
        custatevecHandle_t                 handle,
        custatevecSVSwapWorkerDescriptor_t svSwapWorker,
        void**                             dstSubSVsP2P,
        const int32_t*                     dstSubSVIndicesP2P,
        void**                             dstSemaphores,
        const uint32_t                     nDstSubSVsP2P);


/**
 * \brief Set state vector swap parameters.
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[in] svSwapWorker state vector swap worker
 * \param[in] parameters data transfer parameters
 * \param[in] peer the peer process identifier of the data transfer
 *
 * This function sets the parameters to swap state vector elements. The value of the \p parameters
 * argument is retrieved by calling
 * custatevecDistIndexBitSwapSchedulerGetParameters().
 *
 * The \p peer argument specifies the rank of the peer process that holds the destination
 * sub state vector. The sub state vector index of the destination sub state vector is
 * obtained from the \p dstSubSVIndex member defined in custatevecSVSwapParameters_t.
 *
 * If all the sub state vectors are accessible by GPUDirect P2P and a null pointer is passed
 * to the \p communicator argument when calling custatevecSVSwapWorkerCreate(),
 * the \p peer argument is ignored.
 */
custatevecStatus_t
custatevecSVSwapWorkerSetParameters(
        custatevecHandle_t                  handle,
        custatevecSVSwapWorkerDescriptor_t  svSwapWorker,
        const custatevecSVSwapParameters_t* parameters,
        int                                 peer);

/**
 * \brief Execute the data transfer.
 *
 * \param[in] handle the handle to cuStateVec library
 * \param[in] svSwapWorker state vector swap worker
 * \param[in] begin the index to start transfer
 * \param[in] end the index to end transfer
 *
 * This function executes the transfer of state vector elements.
 * The number of elements being transferred is obtained from the \p transferSize
 * member in custatevecSVSwapParameters_t.
 * The \p begin and \p end arguments specify the range, [\p begin, \p end), for
 * elements being transferred.
 */
custatevecStatus_t
custatevecSVSwapWorkerExecute(
        custatevecHandle_t                 handle,
        custatevecSVSwapWorkerDescriptor_t svSwapWorker,
        custatevecIndex_t                  begin,
        custatevecIndex_t                  end);

/** \} distributed_swap_index_bits_api */

/**
 * \defgroup batched_simulation_api  Batched Simulation API
 *
 * \{ */

/**
 * \brief This function gets the required workspace size for custatevecApplyMatrixBatched().
 *
 * \param[in] handle the handle to the cuStateVec context
 * \param[in] svDataType Data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[in] nSVs the number of state vectors
 * \param[in] svStride distance of two consecutive state vectors
 * \param[in] mapType enumerator specifying the way to assign matrices
 * \param[in] matrixIndices pointer to a host or device array of matrix indices
 * \param[in] matrices pointer to allocated matrices in one contiguous memory chunk on host or device
 * \param[in] matrixDataType data type of matrix
 * \param[in] layout enumerator specifying the memory layout of matrix
 * \param[in] adjoint apply adjoint of matrix
 * \param[in] nMatrices the number of matrices
 * \param[in] nTargets the number of target bits
 * \param[in] nControls the number of control bits
 * \param[in] computeType computeType of matrix multiplication
 * \param[out] extraWorkspaceSizeInBytes  workspace size
 *
 *
 * \details This function returns the required extra workspace size to execute
 * custatevecApplyMatrixBatched().
 * \p extraWorkspaceSizeInBytes will be set to 0 if no extra buffer is required
 * for a given set of arguments.
 */
custatevecStatus_t
custatevecApplyMatrixBatchedGetWorkspaceSize(custatevecHandle_t         handle,
                                             cudaDataType_t             svDataType,
                                             const uint32_t             nIndexBits,
                                             const uint32_t             nSVs,
                                             const custatevecIndex_t    svStride,
                                             custatevecMatrixMapType_t  mapType,
                                             const int32_t*             matrixIndices,
                                             const void*                matrices,
                                             cudaDataType_t             matrixDataType,
                                             custatevecMatrixLayout_t   layout,
                                             const int32_t              adjoint,
                                             const uint32_t             nMatrices,
                                             const uint32_t             nTargets,
                                             const uint32_t             nControls,
                                             custatevecComputeType_t    computeType,
                                             size_t*                    extraWorkspaceSizeInBytes);

/**
 * \brief This function applies one gate matrix to each one of a set of batched state vectors.
 * 
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] batchedSv batched state vector allocated in one continuous memory chunk on device
 * \param[in] svDataType data type of the state vectors
 * \param[in] nIndexBits the number of index bits of the state vectors
 * \param[in] nSVs the number of state vectors
 * \param[in] svStride distance of two consecutive state vectors
 * \param[in] mapType enumerator specifying the way to assign matrices
 * \param[in] matrixIndices pointer to a host or device array of matrix indices
 * \param[in] matrices pointer to allocated matrices in one contiguous memory chunk on host or device
 * \param[in] matrixDataType data type of matrices
 * \param[in] layout enumerator specifying the memory layout of matrix
 * \param[in] adjoint apply adjoint of matrix
 * \param[in] nMatrices the number of matrices
 * \param[in] targets pointer to a host array of target bits
 * \param[in] nTargets the number of target bits
 * \param[in] controls pointer to a host array of control bits
 * \param[in] controlBitValues pointer to a host array of control bit values
 * \param[in] nControls the number of control bits
 * \param[in] computeType computeType of matrix multiplication
 * \param[in] extraWorkspace extra workspace
 * \param[in] extraWorkspaceSizeInBytes extra workspace size
 *
 * \details This function applies one gate matrix for each of batched state vectors given by the \p batchedSv argument.
 * Batched state vectors are allocated in single device memory chunk with the stride specified by the \p svStride argument.
 * Each state vector size is \f$2^\text{nIndexBits}\f$ and the number of state vectors is specified by the \p nSVs argument.
 *
 * The \p mapType argument specifies the way to assign matrices to the state vectors, and the \p matrixIndices argument 
 * specifies the matrix indices for the state vectors. When \p mapType is ::CUSTATEVEC_MATRIX_MAP_TYPE_MATRIX_INDEXED,
 * the \f$\text{matrixIndices[}i\text{]}\f$-th matrix will be assigned to the \f$i\f$-th state vector.
 * \p matrixIndices should contain \p nSVs integers when \p mapType is ::CUSTATEVEC_MATRIX_MAP_TYPE_MATRIX_INDEXED and 
 * it can be a null pointer when \p mapType is ::CUSTATEVEC_MATRIX_MAP_TYPE_BROADCAST.
 * 
 * The \p matrices argument is a host or device pointer of a 2-dimensional array for a square matrix.
 * The size of matrices is (\f$\text{nMatrices} \times 2^\text{nTargets} \times 2^\text{nTargets}\f$ ) and the value 
 * type is specified by the \p matrixDataType argument. The \p layout argument specifies the matrix layout which can be
 * in either row-major or column-major order.
 * The \p targets and \p controls arguments specify target and control bit positions in the state vector
 * index. In this API, these bit positions are uniform for all the batched state vectors.
 *
 * The \p controlBitValues argument specifies bit values of control bits. The ordering
 * of \p controlBitValues is specified by the \p controls argument. If a null pointer is
 * specified to this argument, all control bit values are set to 1.
 *
 * By definition, bit positions in \p targets and \p controls arguments should not overlap.
 *
 * This function may return ::CUSTATEVEC_STATUS_INSUFFICIENT_WORKSPACE for large \p nTargets.
 * In such cases, the \p extraWorkspace and \p extraWorkspaceSizeInBytes arguments should be specified
 * to provide extra workspace.  The size of required extra workspace is obtained by
 * calling custatevecApplyMatrixBatchedGetWorkspaceSize().
 * A null pointer can be passed to the \p extraWorkspace argument if no extra workspace is
 * required.
 * Also, if a device memory handler is set, the \p extraWorkspace can be set to null, 
 * and the \p extraWorkspaceSizeInBytes can be set to 0.
 *
 * \note In this version, this API does not return any errors even if the \p matrixIndices argument
 * contains invalid matrix indices. However, when applicable an error message would be printed to stdout.
 *
 * \note For Blackwell architecture, each of batched state vectors has to be 128-byte aligned.
 * Otherwise, this function may return ::CUSTATEVEC_STATUS_INVALID_VALUE.
 */
custatevecStatus_t
custatevecApplyMatrixBatched(custatevecHandle_t         handle,
                             void*                      batchedSv,
                             cudaDataType_t             svDataType,
                             const uint32_t             nIndexBits,
                             const uint32_t             nSVs,
                             custatevecIndex_t          svStride,
                             custatevecMatrixMapType_t  mapType,
                             const int32_t*             matrixIndices,
                             const void*                matrices,
                             cudaDataType_t             matrixDataType,
                             custatevecMatrixLayout_t   layout,
                             const int32_t              adjoint,
                             const uint32_t             nMatrices,
                             const int32_t*             targets,
                             const uint32_t             nTargets,
                             const int32_t*             controls,
                             const int32_t*             controlBitValues,
                             const uint32_t             nControls,
                             custatevecComputeType_t    computeType,
                             void*                      extraWorkspace,
                             size_t                     extraWorkspaceSizeInBytes);

/**
 * \brief Calculate batched abs2sum array for a given set of index bits
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] batchedSv batch of state vectors
 * \param[in] svDataType data type of state vector
 * \param[in] nIndexBits the number of index bits
 * \param[in] nSVs the number of state vectors in a batch
 * \param[in] svStride the stride of state vector
 * \param[out] abs2sumArrays pointer to a host or device array of sums of squared absolute values
 * \param[in] abs2sumArrayStride the distance between consequence abs2sumArrays
 * \param[in] bitOrdering pointer to a host array of index bit ordering
 * \param[in] bitOrderingLen the length of bitOrdering
 * \param[in] maskBitStrings pointer to a host or device array of mask bit strings
 * \param[in] maskOrdering  pointer to a host array for the mask ordering
 * \param[in] maskLen the length of mask
 *
 * \details The batched version of custatevecAbs2SumArray() that calculates a batch of arrays that
 * holds sums of squared absolute values from batched state vectors.
 *
 * State vectors are placed on a single contiguous device memory chunk.  The \p svStride argument
 * specifies the distance between two adjacent state vectors.  Thus, \p svStride should be
 * equal to or larger than the state vector size.
 *
 * The computed sums of squared absolute values are output to the \p abs2sumArrays which is
 * a contiguous memory chunk.  The \p abs2sumArrayStride specifies the distance between
 * adjacent two abs2sum arrays.  The batched abs2sum arrays can be on host or device.
 *  The index bit ordering the abs2sum array in the batch is specified by the \p bitOrdering and
 * \p bitOrderingLen arguments. Unspecified bits are folded (summed up).
 *
 * The \p maskBitStrings, \p maskOrdering and \p maskLen arguments specify bit mask to for the
 * index bits of batched state vectors.  The abs2sum array is calculated by using state vector
 * elements  whose indices match the specified mask bit strings.
 * The \p maskBitStrings argument specifies an array of mask values as integer bit masks that are
 * applied for the state vector index.
 *
 * If the \p maskLen argument is 0, null pointers can be specified to the
 * \p maskBitStrings and \p maskOrdering arguments.  In this case, all state vector elements are
 * used without masks to compute the squared sum of absolute values.
 *
 * By definition, bit positions in \p bitOrdering and \p maskOrdering arguments should not overlap.
 *
 * The empty \p bitOrdering can be specified to calculate the norm of state vector. In this case,
 * 0 is passed to the \p bitOrderingLen argument and the \p bitOrdering argument can be a null pointer.
 *
 * \note In this version, this API does not return any errors even if the \p maskBitStrings argument
 * contains invalid bit strings. However, when applicable an error message would be printed to stdout.
 */
custatevecStatus_t
custatevecAbs2SumArrayBatched(custatevecHandle_t       handle,
                              const void*              batchedSv,
                              cudaDataType_t           svDataType,
                              const uint32_t           nIndexBits,
                              const uint32_t           nSVs,
                              const custatevecIndex_t  svStride,
                              double*                  abs2sumArrays,
                              const custatevecIndex_t  abs2sumArrayStride,
                              const int32_t*           bitOrdering,
                              const uint32_t           bitOrderingLen,
                              const custatevecIndex_t* maskBitStrings,
                              const int32_t*           maskOrdering,
                              const uint32_t           maskLen);

/**
 * \brief This function gets the required workspace size for custatevecCollapseByBitStringBatched().
 *
 * \param[in] handle the handle to the cuStateVec context
 * \param[in] nSVs the number of batched state vectors
 * \param[in] bitStrings pointer to an array of bit strings, on either host or device
 * \param[in] norms pointer to an array of normalization constants, on either host or device
 * \param[out] extraWorkspaceSizeInBytes  workspace size
 *
 * \details This function returns the required extra workspace size to execute
 * custatevecCollapseByBitStringBatched().
 * \p extraWorkspaceSizeInBytes will be set to 0 if no extra buffer is required.
 *
 * \note The \p bitStrings and \p norms arrays are of the same size \p nSVs and can reside on either
 * the host or the device, but their locations must remain the same when invoking
 * custatevecCollapseByBitStringBatched(), or the computed workspace size may become invalid and lead
 * to undefined behavior.
 */

custatevecStatus_t
custatevecCollapseByBitStringBatchedGetWorkspaceSize(custatevecHandle_t       handle,
                                                     const uint32_t           nSVs,
                                                     const custatevecIndex_t* bitStrings,
                                                     const double*            norms,
                                                     size_t*                  extraWorkspaceSizeInBytes);

/**
 * \brief Collapse the batched state vectors to the state specified by a given bit string.
 * 
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] batchedSv batched state vector allocated in one continuous memory chunk on device
 * \param[in] svDataType data type of the state vectors
 * \param[in] nIndexBits the number of index bits of the state vectors
 * \param[in] nSVs the number of batched state vectors
 * \param[in] svStride distance of two consecutive state vectors
 * \param[in] bitStrings pointer to an array of bit strings, on either host or device
 * \param[in] bitOrdering pointer to a host array of bit string ordering
 * \param[in] bitStringLen length of bit string
 * \param[in] norms pointer to an array of normalization constants on either host or device
 * \param[in] extraWorkspace extra workspace
 * \param[in] extraWorkspaceSizeInBytes size of the extra workspace
 *
 * \details This function collapses all of the state vectors in a batch to the state specified by a given bit string.
 * Batched state vectors are allocated in single device memory chunk with the stride specified by the \p svStride argument.
 * Each state vector size is \f$2^\text{nIndexBits}\f$ and the number of state vectors is specified by the \p nSVs argument.
 *
 * The i-th state vector's elements, as specified by the i-th \p bitStrings element and the \p bitOrdering and
 * \p bitStringLen arguments, are normalized by the i-th \p norms element. Other state vector elements are set to zero.
 *
 * At least one basis bit should be specified, otherwise this function returns ::CUSTATEVEC_STATUS_INVALID_VALUE.
 *
 * Note that \p bitOrdering and \p bitStringLen are applicable to all state vectors in the batch, while the \p bitStrings
 * and \p norms arrays are of the same size \p nSVs and can reside on either the host or the device.
 *
 * The \p bitStrings argument should hold integers in [0, \f$ 2^\text{bitStringLen} \f$).
 *
 * \note In this version, custatevecCollapseByBitStringBatched() does not return error if an invalid \p bitStrings
 * or \p norms argument is specified. However, when applicable an error message would be printed to stdout.
 *
 * This function may return ::CUSTATEVEC_STATUS_INSUFFICIENT_WORKSPACE for large \p nSVs and/or \p nIndexBits.
 * In such cases, the \p extraWorkspace and \p extraWorkspaceSizeInBytes arguments should be specified
 * to provide extra workspace.  The size of required extra workspace is obtained by
 * calling custatevecCollapseByBitStringBatchedGetWorkspaceSize().
 * A null pointer can be passed to the \p extraWorkspace argument if no extra workspace is
 * required.
 * Also, if a device memory handler is set, the \p extraWorkspace can be set to null, 
 * and the \p extraWorkspaceSizeInBytes can be set to 0.
 *
 * \note Unlike the non-batched version (custatevecCollapseByBitString()), in this batched version \p bitStrings
 * are stored as an array with element type ::custatevecIndex_t; that is, each element is an integer representing
 * a bit string in the binary form. This usage is in line with the custatevecSamplerSample() API.
 * See the \ref bit_ordering "Bit Ordering" section for further detail.
 *
 * \note The \p bitStrings and \p norms arrays are of the same size \p nSVs and can reside on either
 * the host or the device, but their locations must remain the same when invoking
 * custatevecCollapseByBitStringBatchedGetWorkspaceSize(), or the computed workspace size may become
 * invalid and lead to undefined behavior.
 */

custatevecStatus_t
custatevecCollapseByBitStringBatched(custatevecHandle_t       handle,
                                     void*                    batchedSv,
                                     cudaDataType_t           svDataType,
                                     const uint32_t           nIndexBits,
                                     const uint32_t           nSVs,
                                     const custatevecIndex_t  svStride,
                                     const custatevecIndex_t* bitStrings,
                                     const int32_t*           bitOrdering,
                                     const uint32_t           bitStringLen,
                                     const double*            norms,
                                     void*                    extraWorkspace,
                                     size_t                   extraWorkspaceSizeInBytes);

/**
 * \brief Single qubit measurements for batched state vectors
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] batchedSv batched state vectors
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits
 * \param[in] nSVs the number of state vectors in the batched state vector
 * \param[in] svStride the distance between state vectors in the batch
 * \param[out] bitStrings pointer to a host or device array of measured bit strings
 * \param[in] bitOrdering pointer to a host array of bit string ordering
 * \param[in] bitStringLen length of bitString
 * \param[in] randnums pointer to a host or device array of random numbers.
 * \param[in] collapse  Collapse operation
 *
 * \details This function measures bit strings of batched state vectors.
 * The \p bitOrdering and \p bitStringLen arguments specify an integer array
 * of index bit positions to be measured.  The measurement results are returned to
 * \p bitStrings which is a 64-bit integer array of 64-bit integer bit masks.
 *
 * Ex. When \p bitOrdering = {3, 1} is specified, this function measures two index bits.
 * The 0-th bit in \p bitStrings elements represents the measurement outcomes of the
 * index bit 3, and the 1st bit represents those of the 1st index bit.
 *
 * Batched state vectors are given in a single contiguous memory chunk where state vectors
 * are placed at the distance specified by \p svStride.  The \p svStride is expressed in
 * the number of elements.
 *
 * The \p randnums stores random numbers used for measurements.  The number of random numbers
 * is identical to \p nSVs, and values should be in [0, 1).  Any random number not in this range, the value is clipped to [0, 1).
 *
 * If ::CUSTATEVEC_COLLAPSE_NONE is specified for the \p collapse argument, this function
 * only returns the measured bit strings without collapsing the state vector.
 * When ::CUSTATEVEC_COLLAPSE_NORMALIZE_AND_ZERO is specified, this function
 * collapses state vectors.  After collapse of state vectors, the norms of all state vectors will be 1.
 * 
 * \note This API is for measuring batched state vectors. For measuring a single state vector,
 * custatevecBatchMeasure() is also available, whose arguments are passed in a different convention.
 */
custatevecStatus_t
custatevecMeasureBatched(custatevecHandle_t          handle,
                         void*                       batchedSv,
                         cudaDataType_t              svDataType,
                         const uint32_t              nIndexBits,
                         const uint32_t              nSVs,
                         const custatevecIndex_t     svStride,
                         custatevecIndex_t*          bitStrings,
                         const int32_t*              bitOrdering,
                         const uint32_t              bitStringLen,
                         const double*               randnums,
                         enum custatevecCollapseOp_t collapse);

/**
 * \brief This function gets the required workspace size for custatevecComputeExpectationBatched().
 *
 * \param[in] handle the handle to the cuStateVec context
 * \param[in] svDataType Data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[in] nSVs the number of state vectors
 * \param[in] svStride distance of two consecutive state vectors
 * \param[in] matrices pointer to allocated matrices in one contiguous memory chunk on host or device
 * \param[in] matrixDataType data type of matrices
 * \param[in] layout enumerator specifying the memory layout of matrix
 * \param[in] nMatrices the number of matrices
 * \param[in] nBasisBits the number of basis bits
 * \param[in] computeType computeType of matrix multiplication
 * \param[out] extraWorkspaceSizeInBytes size of the extra workspace
 *
 * \details This function returns the size of the extra workspace required to execute
 * custatevecComputeExpectationBatched().
 * \p extraWorkspaceSizeInBytes will be set to 0 if no extra buffer is required.
 */

custatevecStatus_t
custatevecComputeExpectationBatchedGetWorkspaceSize(custatevecHandle_t       handle,
                                                    cudaDataType_t           svDataType,
                                                    const uint32_t           nIndexBits,
                                                    const uint32_t           nSVs,
                                                    const custatevecIndex_t  svStride,
                                                    const void*              matrices,
                                                    cudaDataType_t           matrixDataType,
                                                    custatevecMatrixLayout_t layout,
                                                    const uint32_t           nMatrices,
                                                    const uint32_t           nBasisBits,
                                                    custatevecComputeType_t  computeType,
                                                    size_t*                  extraWorkspaceSizeInBytes);

/**
 * \brief Compute the expectation values of matrix observables for each of the batched state vectors.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] batchedSv batched state vector allocated in one continuous memory chunk on device
 * \param[in] svDataType data type of the state vector
 * \param[in] nIndexBits the number of index bits of the state vector
 * \param[in] nSVs the number of state vectors
 * \param[in] svStride distance of two consecutive state vectors
 * \param[out] expectationValues pointer to a host or device array to store expectation values
 * \param[in] matrices pointer to allocated matrices in one contiguous memory chunk on host or device
 * \param[in] matrixDataType data type of matrices
 * \param[in] layout matrix memory layout
 * \param[in] nMatrices the number of matrices
 * \param[in] basisBits pointer to a host array of basis index bits
 * \param[in] nBasisBits the number of basis bits
 * \param[in] computeType computeType of matrix multiplication
 * \param[in] extraWorkspace pointer to an extra workspace
 * \param[in] extraWorkspaceSizeInBytes the size of extra workspace
 *
 * \details This function computes expectation values for given matrix observables to each one of batched state
 * vectors given by the \p batchedSv argument. Batched state vectors are allocated in single device memory chunk
 * with the stride specified by the \p svStride argument. Each state vector size is \f$2^\text{nIndexBits}\f$ and
 * the number of state vectors is specified by the \p nSVs argument.
 *
 * The \p expectationValues argument points to single memory chunk to output the expectation values.
 * This API returns values in double precision (complex128) regardless of input data types.
 * The output array size is (\f$\text{nMatrices} \times \text{nSVs}\f$ ) and its leading dimension is \p nMatrices.
 *
 * The \p matrices argument is a host or device pointer of a 2-dimensional array for a square matrix.
 * The size of matrices is (\f$\text{nMatrices} \times 2^\text{nBasisBits} \times 2^\text{nBasisBits}\f$ ) and the value 
 * type is specified by the \p matrixDataType argument. The \p layout argument specifies the matrix layout which can be
 * in either row-major or column-major order.

 * The \p basisBits and \p nBasisBits arguments specify the basis to calculate expectation.
 * For the \p computeType argument, the same combinations for custatevecComputeExpectation() are
 * available.
 *
 * This function may return ::CUSTATEVEC_STATUS_INSUFFICIENT_WORKSPACE for large \p nBasisBits.
 * In such cases, the \p extraWorkspace and \p extraWorkspaceSizeInBytes arguments should be specified
 * to provide extra workspace. The size of required extra workspace is obtained by
 * calling custatevecComputeExpectationBatchedGetWorkspaceSize().
 * A null pointer can be passed to the \p extraWorkspace argument if no extra workspace is
 * required.
 * Also, if a device memory handler is set, the \p extraWorkspace can be set to null, 
 * and the \p extraWorkspaceSizeInBytes can be set to 0.
 */

custatevecStatus_t
custatevecComputeExpectationBatched(custatevecHandle_t       handle,
                                    const void*              batchedSv,
                                    cudaDataType_t           svDataType,
                                    const uint32_t           nIndexBits,
                                    const uint32_t           nSVs,
                                    custatevecIndex_t        svStride,
                                    double2*                 expectationValues,
                                    const void*              matrices,
                                    cudaDataType_t           matrixDataType,
                                    custatevecMatrixLayout_t layout,
                                    const uint32_t           nMatrices,
                                    const int32_t*           basisBits,
                                    const uint32_t           nBasisBits,
                                    custatevecComputeType_t  computeType,
                                    void*                    extraWorkspace,
                                    size_t                   extraWorkspaceSizeInBytes);

/** \} batched_simulation_api */

/**
 * \defgroup host_state_vector_api  Host State Vector API
 *
 * \{ */

/**
 * \typedef custatevecSubSVMigratorDescriptor_t
 * \brief This descriptor holds the context of the migrator operation, initialized using
 * custatevecSubSVMigratorCreate() and destroyed using custatevecSubSVMigratorDestroy(), respectively.
 */
typedef struct custatevecSubSVMigratorDescriptor* custatevecSubSVMigratorDescriptor_t;

/**
 * \brief Create sub state vector migrator descriptor.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[out] migrator pointer to a new migrator descriptor
 * \param[in] deviceSlots pointer to sub state vectors on device
 * \param[in] svDataType data type of state vector
 * \param[in] nDeviceSlots the number of sub state vectors in deviceSlots
 * \param[in] nLocalIndexBits the number of index bits of sub state vectors
 *
 * \details This function creates a sub state vector migrator descriptor.
 * Sub state vectors specified by the \p deviceSlots argument are allocated in one contiguous memory array
 * and its size should be at least (\f$\text{nDeviceSlots} \times 2^\text{nLocalIndexBits}\f$).
 */
custatevecStatus_t
custatevecSubSVMigratorCreate(custatevecHandle_t handle,
                              custatevecSubSVMigratorDescriptor_t* migrator,
                              void* deviceSlots,
                              cudaDataType_t svDataType,
                              int nDeviceSlots,
                              int nLocalIndexBits);

/**
 * \brief Destroy sub state vector migrator descriptor.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in,out] migrator the migrator descriptor
 *
 * \details This function releases a sub state vector migrator descriptor.
 */
custatevecStatus_t
custatevecSubSVMigratorDestroy(custatevecHandle_t handle,
                               custatevecSubSVMigratorDescriptor_t migrator);

/**
 * \brief Sub state vector migration.
 *
 * \param[in] handle the handle to the cuStateVec library
 * \param[in] migrator the migrator descriptor
 * \param[in] deviceSlotIndex the index to specify sub state vector to migrate
 * \param[in] srcSubSV a pointer to a sub state vector that is migrated to deviceSlots
 * \param[out] dstSubSV a pointer to a sub state vector that is migrated from deviceSlots
 * \param[in] begin the index to start migration
 * \param[in] end the index to end migration
 *
 * \details This function performs a sub state vector migration.
 * The \p deviceSlotIndex argument specifies the index of the sub state vector to be transferred, and
 * the \p srcSubSV and \p dstSubSV arguments specify sub state vectors to be transferred from/to the sub state vector on device.
 * In the current version, \p srcSubSV and \p dstSubSV must be arrays allocated on host memory and accessible from the device.
 * If either \p srcSubSV or \p dstSubSV is a null pointer, the corresponding data transfer will be skipped.
 * The \p begin and \p end arguments specify the range, [\p begin, \p end), for elements being transferred.
 */
custatevecStatus_t
custatevecSubSVMigratorMigrate(custatevecHandle_t handle,
                               custatevecSubSVMigratorDescriptor_t migrator,
                               int deviceSlotIndex,
                               const void* srcSubSV,
                               void* dstSubSV,
                               custatevecIndex_t begin,
                               custatevecIndex_t end);

/** \} host_state_vector_api */

#if defined(__cplusplus)
} // extern "C"
#endif // defined(__cplusplus)
