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
#include <string>
#include <memory>

namespace yirage {
namespace kernel {

// Element-wise operation types
enum class ElementOpType : int32_t {
    ADD = 0,
    SUB = 1,
    MUL = 2,
    DIV = 3,
    MAX = 4,
    MIN = 5,
    RELU = 6,
    GELU = 7,
    SIGMOID = 8,
    TANH = 9
};

// YICA Element-wise Operations
class YICAElementOpsOp {
public:
    struct Config {
        bool use_hardware_acceleration;
        uint32_t preferred_cim_array;
        std::string data_type;
        bool enable_vectorization;
        uint32_t vector_width;
        
        Config() : use_hardware_acceleration(true), preferred_cim_array(0),
                  data_type("float32"), enable_vectorization(true),
                  vector_width(16) {}
    };
    
    YICAElementOpsOp(const Config& config = Config{});
    ~YICAElementOpsOp();
    
    // Binary operations
    bool forward_binary(const void* A, const void* B, void* C,
                       ElementOpType op_type,
                       uint64_t num_elements,
                       const std::string& dtype = "float32");
    
    // Unary operations
    bool forward_unary(const void* A, void* C,
                      ElementOpType op_type,
                      uint64_t num_elements,
                      const std::string& dtype = "float32");
    
    // Scalar operations
    bool forward_scalar(const void* A, void* C,
                       ElementOpType op_type,
                       float scalar_value,
                       uint64_t num_elements,
                       const std::string& dtype = "float32");
    
    // Performance metrics
    double get_last_execution_time_ms() const;
    float get_throughput_gops() const;
    
    // Configuration
    void set_config(const Config& config);
    Config get_config() const;

private:
    class Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace kernel
} // namespace yirage