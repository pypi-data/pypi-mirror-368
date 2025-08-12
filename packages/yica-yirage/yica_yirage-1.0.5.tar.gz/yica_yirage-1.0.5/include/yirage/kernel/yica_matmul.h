// Copyright 2024 CMU
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once

#include <cstdint>
#include <vector>
#include <memory>

namespace yirage {
namespace kernel {

// YICA Matrix Multiplication Operator
class YICAMatMulOp {
public:
    struct Config {
        bool use_hardware_acceleration;
        uint32_t preferred_cim_array;
        std::string data_type;
        bool enable_mixed_precision;
        float alpha;  // scaling factor
        float beta;   // bias factor
        
        Config() : use_hardware_acceleration(true), preferred_cim_array(0),
                  data_type("float32"), enable_mixed_precision(false),
                  alpha(1.0f), beta(0.0f) {}
    };
    
    YICAMatMulOp(const Config& config = Config{});
    ~YICAMatMulOp();
    
    // Forward computation
    bool forward(const void* A, const void* B, void* C,
                uint32_t M, uint32_t N, uint32_t K,
                const std::string& dtype = "float32");
    
    // Batched computation
    bool forward_batched(const std::vector<const void*>& A_batch,
                        const std::vector<const void*>& B_batch,
                        const std::vector<void*>& C_batch,
                        uint32_t batch_size,
                        uint32_t M, uint32_t N, uint32_t K,
                        const std::string& dtype = "float32");
    
    // Performance and profiling
    double get_last_execution_time_ms() const;
    uint64_t get_total_flops() const;
    float get_cim_utilization() const;
    
    // Configuration
    void set_config(const Config& config);
    Config get_config() const;
    
    // Hardware status
    bool is_hardware_available() const;
    std::string get_last_error() const;

private:
    class Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace kernel
} // namespace yirage