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

// YICA Chunk Operation for tensor splitting and concatenation
class YICAChunkOp {
public:
    struct Config {
        bool use_hardware_acceleration;
        uint32_t preferred_cim_array;
        std::string data_type;
        bool enable_zero_copy;
        uint32_t chunk_alignment;
        
        Config() : use_hardware_acceleration(true), preferred_cim_array(0),
                  data_type("float32"), enable_zero_copy(true),
                  chunk_alignment(64) {}
    };
    
    YICAChunkOp(const Config& config = Config{});
    ~YICAChunkOp();
    
    // Split tensor into chunks
    bool split(const void* input, std::vector<void*>& outputs,
              const std::vector<uint32_t>& input_shape,
              uint32_t split_dim,
              const std::vector<uint32_t>& chunk_sizes,
              const std::string& dtype = "float32");
    
    // Concatenate chunks into tensor
    bool concatenate(const std::vector<const void*>& inputs, void* output,
                    const std::vector<std::vector<uint32_t>>& input_shapes,
                    uint32_t concat_dim,
                    const std::string& dtype = "float32");
    
    // Chunk-wise operations
    bool chunk_wise_operation(const std::vector<const void*>& inputs,
                             std::vector<void*>& outputs,
                             const std::string& operation_type,
                             const std::vector<std::vector<uint32_t>>& shapes,
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