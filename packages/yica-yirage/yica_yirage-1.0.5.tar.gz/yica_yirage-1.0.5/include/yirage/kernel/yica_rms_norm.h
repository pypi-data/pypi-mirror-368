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

// YICA RMS Normalization Operation
class YICARMSNormOp {
public:
    struct Config {
        bool use_hardware_acceleration;
        uint32_t preferred_cim_array;
        std::string data_type;
        float epsilon;
        bool fuse_weight_multiplication;
        
        Config() : use_hardware_acceleration(true), preferred_cim_array(0),
                  data_type("float32"), epsilon(1e-6f),
                  fuse_weight_multiplication(true) {}
    };
    
    YICARMSNormOp(const Config& config = Config{});
    ~YICARMSNormOp();
    
    // Forward computation
    bool forward(const void* input, void* output,
                const void* weight,  // optional, can be nullptr
                const std::vector<uint32_t>& input_shape,
                const std::vector<uint32_t>& normalized_shape,
                const std::string& dtype = "float32");
    
    // Backward computation (for training)
    bool backward(const void* grad_output, const void* input, const void* weight,
                 void* grad_input, void* grad_weight,
                 const std::vector<uint32_t>& input_shape,
                 const std::vector<uint32_t>& normalized_shape,
                 const std::string& dtype = "float32");
    
    // Performance metrics
    double get_last_execution_time_ms() const;
    float get_memory_bandwidth_utilization() const;
    
    // Configuration
    void set_config(const Config& config);
    Config get_config() const;

private:
    class Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace kernel
} // namespace yirage