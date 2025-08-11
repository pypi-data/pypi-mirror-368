#include "torch_extensions/sparse3d/trilinear_projection_cpu_kernels.h"
#include "torch_extensions/sparse3d/trilinear_projection_cpu_utils.h"

template <typename scalar_t, bool do_bias, bool do_grad_rot_matrix, bool return_backprop_weight>
void trilinear_projection_backward_cpu_kernel(
    const torch::TensorAccessor<scalar_t, 2> grid2d_coord,
    const torch::TensorAccessor<long, 3> grid3d_index,
    const torch::TensorAccessor<scalar_t, 3> weight,
    const torch::TensorAccessor<scalar_t, 2> bias,
    const torch::TensorAccessor<scalar_t, 3> rot_matrix,
    const torch::TensorAccessor<scalar_t, 2> input,
    const torch::TensorAccessor<scalar_t, 3> grad_output,
    torch::TensorAccessor<scalar_t, 3> grad_weight,
    torch::TensorAccessor<scalar_t, 2> grad_bias,
    torch::TensorAccessor<scalar_t, 2> grad_input,
    torch::TensorAccessor<scalar_t, 3> grad_rot_matrix,
    torch::TensorAccessor<scalar_t, 1> backprop_weight,
    const int max_r2,
    const int init_offset
)
{
    int xs[2], ys[2], zs[2];
    scalar_t r, xp, yp, zp, fx, fy, fz;
    for (long b = 0; b < input.size(0); b ++)
    {
        for (long i = 0; i < grid2d_coord.size(0); i ++)
        {
            scalar_t x(grid2d_coord[i][1]), y(grid2d_coord[i][0]);
            _helper_rotate_coordinates<scalar_t>(
                rot_matrix[b], x, y, xp, yp, zp
            );

            r = xp*xp + yp*yp + zp*zp;
            if (r <= max_r2)
            {
                scalar_t conj = _helper_cube_interpolation_coordinates<scalar_t>(
                    xp, yp, zp, init_offset, xs, ys, zs, fx, fy, fz
                );

                scalar_t fxs[] = {(scalar_t) 1.0 - fx, (scalar_t) fx};
                scalar_t fys[] = {(scalar_t) 1.0 - fy, (scalar_t) fy};
                scalar_t fzs[] = {(scalar_t) 1.0 - fz, (scalar_t) fz};

                /* 'C' is the current cost,
                   a 'voxel' means sum(weight[j]*input[j]),
                   'out' is the linear combination of the 8 voxels  */
                scalar_t dC_dout[] = {grad_output[b][i][0], conj * grad_output[b][i][1]};

                // dout_dp means [d(out)/d(xp), d(out)/d(yp), d(out)/d(zp)]
                scalar_t dout_dp[3][2] = {{0, 0}, {0, 0}, {0, 0}};

                for (int k = 0; k < 8; k++) // over cube vertices
                {
                    const long index = grid3d_index[zs[k/4]] [ys[(k/2)%2]] [xs[k%2]];
                    const scalar_t interpol_weight = fzs[k/4] * fys[(k/2)%2] * fxs[k%2];

                    if (return_backprop_weight)
                        backprop_weight[index] += interpol_weight;

                    for (int c = 0; c < 2; c++) // Over real and imaginary
                    {
                        scalar_t voxel_value(0);
                        const scalar_t dC_dvoxel = dC_dout[c] * interpol_weight;

                        for (int j = 0; j < input.size(1); j ++)
                        {
                            scalar_t wkj = weight[index][j][c];

                            /* voxel = sum(weight[j]*input[j])
                               =>  d(voxel)/d(weight[j]) = input[j]
                                   d(voxel)/d(input[j]) = weight[j]  */

                            grad_weight[index][j][c] += dC_dvoxel * input[b][j];
                            grad_input[b][j] += dC_dvoxel * wkj;

                            if (do_grad_rot_matrix)
                                voxel_value += input[b][j] * wkj;
                        }

                        if (do_bias)
                        {
                            grad_bias[index][c] += dC_dvoxel;
                            if (do_grad_rot_matrix)
                                voxel_value += bias[index][c];
                        }

                        if (do_grad_rot_matrix)
                        {
                            const int ix = k%2;
                            const int iy = (k/2)%2;
                            const int iz = k/4;

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
                        grad_rot_matrix[b][0][k] += dC_dpk * x;
                        grad_rot_matrix[b][1][k] += dC_dpk * y;
                    }
                }
            } // If < max_r
        } // 2D Point
    } // Batch
}


void trilinear_projection_backward_cpu(
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
    CHECK_CPU_INPUT(grid2d_coord)
    CHECK_CPU_INPUT(grid3d_index)
    CHECK_CPU_INPUT(weight)
    CHECK_CPU_INPUT(bias)
    CHECK_CPU_INPUT(rot_matrix)
    CHECK_CPU_INPUT(input)
    CHECK_CPU_INPUT(grad_output)
    CHECK_CPU_INPUT(grad_input)
    CHECK_CPU_INPUT(grad_rot_matrix)
    CHECK_CPU_INPUT(grad_weight)
    CHECK_CPU_INPUT(grad_bias)
    CHECK_CPU_INPUT(backprop_weight)

    std::array<bool, 3> bargs={{do_bias, do_grad_rot_matrix, return_backprop_weight}};
    dispatch_bools<3>{}(
        bargs,
        [&](auto...Bargs) {
            AT_DISPATCH_FLOATING_TYPES(
                input.scalar_type(),
                "trilinear_projection_backward_cpu_kernel",
                [&] {
                    trilinear_projection_backward_cpu_kernel<scalar_t, decltype(Bargs)::value...>(
                        /*grid2d_coord*/ grid2d_coord.accessor<scalar_t, 2>(),
                        /*grid3d_index*/ grid3d_index.accessor<long, 3>(),
                        /*weight*/ weight.accessor<scalar_t, 3>(),
                        /*bias*/ bias.accessor<scalar_t, 2>(),
                        /*rot_matrix*/ rot_matrix.accessor<scalar_t, 3>(),
                        /*input*/ input.accessor<scalar_t, 2>(),
                        /*grad*/ grad_output.accessor<scalar_t, 3>(),
                        /*grad_weight*/ grad_weight.accessor<scalar_t, 3>(),
                        /*grad_bias*/ grad_bias.accessor<scalar_t, 2>(),
                        /*grad_input*/ grad_input.accessor<scalar_t, 2>(),
                        /*grad_rot_matrix*/ grad_rot_matrix.accessor<scalar_t, 3>(),
                        /*backprop_weight*/ backprop_weight.accessor<scalar_t, 1>(),
                        /*max_r2*/ max_r2,
                        /*init_offset*/ init_offset
                    );
                }
            );
        }
    );
}
