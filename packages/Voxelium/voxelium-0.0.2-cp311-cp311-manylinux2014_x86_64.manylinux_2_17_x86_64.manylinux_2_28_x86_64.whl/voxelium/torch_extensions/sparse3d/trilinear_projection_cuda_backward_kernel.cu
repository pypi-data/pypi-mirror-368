#include "torch_extensions/sparse3d/trilinear_projection_cuda_kernels.h"
#include "torch_extensions/sparse3d/trilinear_projection_cuda_utils.cuh"

#define BACKWARD_BLOCK_SIZE 128

template <typename scalar_t, typename accscalar_t, bool do_bias, bool do_grad_rot_matrix, bool return_backprop_weight>
__global__ void trilinear_projection_backward_cuda_kernel(
    const torch::PackedTensorAccessor32<scalar_t, 2, torch::RestrictPtrTraits> grid2d_coord,
    const torch::PackedTensorAccessor64<long, 3, torch::RestrictPtrTraits> grid3d_index,
    const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> weight,
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> bias,
    const torch::PackedTensorAccessor32<scalar_t, 3, torch::RestrictPtrTraits> rot_matrix,
    const torch::PackedTensorAccessor32<scalar_t, 2, torch::RestrictPtrTraits> input,
    const torch::PackedTensorAccessor32<scalar_t, 3, torch::RestrictPtrTraits> grad_output,
    torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> grad_weight,
    torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> grad_bias,
    torch::PackedTensorAccessor32<scalar_t, 2, torch::RestrictPtrTraits> grad_input,
    torch::PackedTensorAccessor32<scalar_t, 3, torch::RestrictPtrTraits> grad_rot_matrix,
    torch::PackedTensorAccessor64<scalar_t, 1, torch::RestrictPtrTraits> backprop_weight,
    const int max_r2,
    const int init_offset,
    const size_t grad_weight_numel,
    const size_t grad_bias_numel,
    const size_t grad_input_numel,
    const size_t grad_rot_matrix_numel,
    const size_t backprop_weight_numel
)
{
    int xs[2], ys[2], zs[2];
    scalar_t r, xp, yp, zp, fx, fy, fz;

    const size_t b = blockIdx.x * blockDim.x + threadIdx.x;
    const size_t i = blockIdx.y * blockDim.y + threadIdx.y;

    if (b < input.size(0) && i < grid2d_coord.size(0))
    {
        scalar_t x(grid2d_coord[i][1]), y(grid2d_coord[i][0]);
        xp = rot_matrix[b][0][0] * x + rot_matrix[b][1][0] * y;
        yp = rot_matrix[b][0][1] * x + rot_matrix[b][1][1] * y;
        zp = rot_matrix[b][0][2] * x + rot_matrix[b][1][2] * y;

        r = xp*xp + yp*yp + zp*zp;
        if (r < max_r2)
        {
            scalar_t conj = _helper_cube_interpolation_coordinates<scalar_t>(
                xp, yp, zp, init_offset, xs, ys, zs, fx, fy, fz
            );

            scalar_t fxs[] = {(scalar_t) 1.0 - fx, fx};
            scalar_t fys[] = {(scalar_t) 1.0 - fy, fy};
            scalar_t fzs[] = {(scalar_t) 1.0 - fz, fz};

            /* 'C' is the current cost,
               a 'voxel' means sum(weight[j]*input[j]),
               'out' is the linear combination of the 8 voxels  */
            scalar_t dC_dout[] = {grad_output[b][i][0], grad_output[b][i][1]};
            dC_dout[1] *= conj; // Make complex conjugate

            // dout_dp means [d(out)/d(xp), d(out)/d(yp), d(out)/d(zp)]
            accscalar_t dout_dp[3][2] = {{0, 0}, {0, 0}, {0, 0}};

            for (int k = 0; k < 8; k++) // over cube vertices
            {
                const long index = grid3d_index[zs[k/4]] [ys[(k/2)%2]] [xs[k%2]];
                const scalar_t interpol_weight = fzs[k/4] * fys[(k/2)%2] * fxs[k%2];

                if (return_backprop_weight)
                    at::native::fastAtomicAdd(
                        backprop_weight.data(),
                        static_cast<uint64_t>(index),
                        backprop_weight_numel,
                        interpol_weight,
                        true
                    );

                for (int c = 0; c < 2; c++) // Over real and imaginary
                {
                    accscalar_t voxel_value(0);
                    const scalar_t dC_dvoxel = dC_dout[c] * interpol_weight;

                    for (int j = 0; j < input.size(1); j ++)
                    {
                        scalar_t wkj = weight[index][j][c];

                        /* voxel = sum(weight[j]*input[j])
                           =>  d(voxel)/d(weight[j]) = input[j]
                               d(voxel)/d(input[j]) = weight[j]  */

                        at::native::fastAtomicAdd(
                            grad_weight.data(),
                            accessor_index_collapse(grad_weight, index, j, c),
                            grad_weight_numel,
                            dC_dvoxel * input[b][j],
                            true
                        );

                        at::native::fastAtomicAdd(
                            grad_input.data(),
                            accessor_index_collapse(grad_input, b, j),
                            grad_input_numel,
                            dC_dvoxel * wkj,
                            true
                        );

                        if (do_grad_rot_matrix)
                            voxel_value += input[b][j] * wkj;
                    }

                    if (do_bias)
                    {
                        at::native::fastAtomicAdd(
                            grad_bias.data(),
                            accessor_index_collapse(grad_bias, index, c),
                            grad_bias_numel,
                            dC_dvoxel,
                            true
                        );
                        if (do_grad_rot_matrix)
                            voxel_value += bias[index][c];
                    }

                    if (do_grad_rot_matrix)
                    {
                        const int ix =  k%2;
                        const int iy = (k/2)%2;
                        const int iz =  k/4;

                        dout_dp[0][c] += (2*ix - 1) * fys[iy] * fzs[iz] * voxel_value;
                        dout_dp[1][c] += fxs[ix] * (2*iy - 1) * fzs[iz] * voxel_value;
                        dout_dp[2][c] += fxs[ix] * fys[iy] * (2*iz - 1) * voxel_value;
                    }
                }
            }

            if (do_grad_rot_matrix)
            {
                for (int k = 0; k < 3; k++)
                {
			        // account for the sign change in (xp,yp,zp)
                    dout_dp[k][0] *= conj;
                    dout_dp[k][1] *= conj;

                    const scalar_t dC_dpk =
                        dC_dout[0] * dout_dp[k][0] +
                        dC_dout[1] * dout_dp[k][1];

                    // p = A x^t  =>  dp[j] / dA[ji] = x[i]
                    at::native::fastAtomicAdd(
                        grad_rot_matrix.data(),
                        accessor_index_collapse(grad_rot_matrix, b, 0, k),
                        grad_rot_matrix_numel,
                        dC_dpk * x,
                        true
                    );
                    at::native::fastAtomicAdd(
                        grad_rot_matrix.data(),
                        accessor_index_collapse(grad_rot_matrix, b, 1, k),
                        grad_rot_matrix_numel,
                        dC_dpk * y,
                        true
                    );
                }
            }
        } // If < max_r
    }
}

void trilinear_projection_backward_cuda(
    const torch::Tensor grid2d_coord,
    const torch::Tensor grid3d_index,
    const torch::Tensor weight,
    const torch::Tensor bias,
    const torch::Tensor rot_matrix,
    const torch::Tensor input,
    const torch::Tensor grad_output,
    torch::Tensor grad_weight,
    torch::Tensor grad_bias,
    torch::Tensor grad_input,
    torch::Tensor grad_rot_matrix,
    torch::Tensor backprop_weight,
    const int max_r2,
    const int init_offset,
    const bool do_bias,
    const bool do_grad_rot_matrix,
    const bool return_backprop_weight
)
{
    CHECK_CUDA_INPUT(grid2d_coord)
    CHECK_CUDA_INPUT(grid3d_index)
    CHECK_CUDA_INPUT(weight)
    CHECK_CUDA_INPUT(bias)
    CHECK_CUDA_INPUT(rot_matrix)
    CHECK_CUDA_INPUT(input)
    CHECK_CUDA_INPUT(grad_output)
    CHECK_CUDA_INPUT(grad_input)
    CHECK_CUDA_INPUT(grad_rot_matrix)
    CHECK_CUDA_INPUT(grad_weight)
    CHECK_CUDA_INPUT(grad_bias)
    CHECK_CUDA_INPUT(backprop_weight)

    const int deviceId = input.device().index();
    const cudaStream_t stream = at::cuda::getCurrentCUDAStream(deviceId);
    CUDA_ERRCHK(cudaSetDevice(deviceId));

    const dim3 threads(1, BACKWARD_BLOCK_SIZE);
    const dim3 blocks(
        (input.size(0) + threads.x - 1) / threads.x,
        (grid2d_coord.size(0) + threads.y - 1) / threads.y
    );

    std::array<bool, 3> bargs={{do_bias, do_grad_rot_matrix, return_backprop_weight}};
    dispatch_bools<3>{}(
        bargs,
        [&](auto...Bargs) {
            AT_DISPATCH_FLOATING_TYPES(
                input.scalar_type(),
                "trilinear_projection_backward_cuda_kernel",
                [&] {
                    using accscalar_t = at::acc_type<scalar_t, true>;
                    trilinear_projection_backward_cuda_kernel
                    <scalar_t, accscalar_t, decltype(Bargs)::value...>
                    <<<blocks, threads, 0, stream>>>(
                        /*grid2d_coord*/ grid2d_coord.packed_accessor32<scalar_t, 2, torch::RestrictPtrTraits>(),
                        /*grid3d_index*/ grid3d_index.packed_accessor64<long, 3, torch::RestrictPtrTraits>(),
                        /*weight*/ weight.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(),
                        /*bias*/ bias.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
                        /*rot_matrix*/ rot_matrix.packed_accessor32<scalar_t, 3, torch::RestrictPtrTraits>(),
                        /*input*/ input.packed_accessor32<scalar_t, 2, torch::RestrictPtrTraits>(),
                        /*grad*/ grad_output.packed_accessor32<scalar_t, 3, torch::RestrictPtrTraits>(),
                        /*grad_weight*/ grad_weight.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(),
                        /*grad_bias*/ grad_bias.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
                        /*grad_input*/ grad_input.packed_accessor32<scalar_t, 2, torch::RestrictPtrTraits>(),
                        /*grad_rot_matrix*/ grad_rot_matrix.packed_accessor32
                            <scalar_t, 3, torch::RestrictPtrTraits>(),
                        /*backprop_weight*/ backprop_weight.packed_accessor64<scalar_t, 1, torch::RestrictPtrTraits>(),
                        /*max_r2*/ max_r2,
                        /*init_offset*/ init_offset,
                        /*grad_weight_numel*/ grad_weight.numel(),
                        /*grad_bias_numel*/ grad_bias.numel(),
                        /*grad_input_numel*/ grad_input.numel(),
                        /*grad_rot_matrix_numel*/ grad_rot_matrix.numel(),
                        /*backprop_weight_numel*/ backprop_weight.numel()
                    );
                }
            );
        }
    );

#ifdef DEBUG
    CUDA_ERRCHK(cudaPeekAtLastError());
    CUDA_ERRCHK(cudaDeviceSynchronize());
#endif
}
