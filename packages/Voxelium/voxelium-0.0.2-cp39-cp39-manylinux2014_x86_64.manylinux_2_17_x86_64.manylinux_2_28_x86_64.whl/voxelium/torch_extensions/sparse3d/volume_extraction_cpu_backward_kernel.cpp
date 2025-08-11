#include "torch_extensions/sparse3d/volume_extraction_cpu_kernels.h"

template <typename scalar_t, bool do_bias, bool do_input_grad>
void volume_extraction_backward_cpu_kernel(
    const torch::TensorAccessor<long, 3> grid3d_index,
    const torch::TensorAccessor<scalar_t, 3> weight,
    const torch::TensorAccessor<scalar_t, 2> bias,
    const torch::TensorAccessor<scalar_t, 2> input,
    const torch::TensorAccessor<scalar_t, 5> grad_output,
    torch::TensorAccessor<scalar_t, 3> grad_weight,
    torch::TensorAccessor<scalar_t, 2> grad_bias,
    torch::TensorAccessor<scalar_t, 2> grad_input,
    const int offset,
    const int max_r2
)
{
    for (long b = 0; b < grad_output.size(0); b ++)
        for (long z = 0; z < grad_output.size(1); z ++)
            for (long y = 0; y < grad_output.size(2); y ++)
                for (long x = 0; x < grad_output.size(3); x ++)
                {
                    const long zp = z - (grad_output.size(1) - 1) / 2;
                    const long yp = y - (grad_output.size(2) - 1) / 2;
                    const long xp = x;

                    scalar_t r = xp*xp + yp*yp + zp*zp;
                    if (r < max_r2)
                    {
                        const long i = grid3d_index[z+offset][y+offset][x];
                        for (int c = 0; c < 2; c++) // Over real and imaginary
                        {
                            for (int j = 0; j < input.size(1); j ++)
                            {
                                grad_weight[i][j][c] += grad_output[b][z][y][x][c] * input[b][j];
                                if (do_input_grad)
                                    grad_input[b][j] += grad_output[b][z][y][x][c] * weight[i][j][c];
                            }

                            if (do_bias)
                                grad_bias[i][c] += grad_output[b][z][y][x][c];
                        }
                    }
                }
}


void volume_extraction_backward_cpu(
    const torch::Tensor grid3d_index,
    const torch::Tensor weight,
    const torch::Tensor bias,
    const torch::Tensor input,
    const torch::Tensor grad_output,
    torch::Tensor grad_weight,
    torch::Tensor grad_bias,
    torch::Tensor grad_input,
    const int max_r2,
    const bool do_bias,
    const bool do_input_grad
)
{
    CHECK_CPU_INPUT(grid3d_index)
    CHECK_CPU_INPUT(weight)
    CHECK_CPU_INPUT(bias)
    CHECK_CPU_INPUT(input)
    CHECK_CPU_INPUT(grad_output)
    CHECK_CPU_INPUT(grad_weight)
    CHECK_CPU_INPUT(grad_bias)
    CHECK_CPU_INPUT(grad_input)

    const int offset = (grid3d_index.size(0) - grad_output.size(1)) / 2;

    std::array<bool, 2> bargs={{do_bias, do_input_grad}};
    dispatch_bools<2>{}(
        bargs,
        [&](auto...Bargs) {
            AT_DISPATCH_FLOATING_TYPES(
                input.scalar_type(),
                "volume_extraction_backward_cpu_kernel",
                [&] {
                    volume_extraction_backward_cpu_kernel<scalar_t, decltype(Bargs)::value...>(
                        /*grid3d_index*/ grid3d_index.accessor<long, 3>(),
                        /*weight*/ weight.accessor<scalar_t, 3>(),
                        /*bias*/ bias.accessor<scalar_t, 2>(),
                        /*input*/ input.accessor<scalar_t, 2>(),
                        /*grad*/ grad_output.accessor<scalar_t, 5>(),
                        /*grad_weight*/ grad_weight.accessor<scalar_t, 3>(),
                        /*grad_bias*/ grad_bias.accessor<scalar_t, 2>(),
                        /*grad_input*/ grad_input.accessor<scalar_t, 2>(),
                        /*offset*/ offset,
                        /*max_r2*/ max_r2
                    );
                }
            );
        }
    );
}
