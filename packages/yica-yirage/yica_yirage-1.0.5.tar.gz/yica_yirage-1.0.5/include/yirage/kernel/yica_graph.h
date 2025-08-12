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
#include <vector>
#include <memory>
#include <unordered_map>

namespace yirage {
namespace kernel {

// Graph node representing a tensor or operation
struct YICAGraphNode {
    uint32_t node_id;
    std::string node_type;  // "input", "output", "operation"
    std::string operation_name;
    std::vector<uint32_t> input_nodes;
    std::vector<uint32_t> output_nodes;
    std::vector<uint32_t> shape;
    std::string data_type;
    std::unordered_map<std::string, std::string> attributes;
    
    YICAGraphNode() : node_id(0), node_type("unknown"), data_type("float32") {}
};

// Optimization configuration
struct YICAOptimizationConfig {
    bool enable_graph_fusion;
    bool enable_memory_optimization;
    bool enable_compute_optimization;
    bool enable_pipeline_optimization;
    std::string target_backend;  // "yica", "cuda", "cpu"
    uint32_t max_fusion_depth;
    float memory_budget_ratio;
    
    YICAOptimizationConfig() 
        : enable_graph_fusion(true)
        , enable_memory_optimization(true)
        , enable_compute_optimization(true)
        , enable_pipeline_optimization(true)
        , target_backend("yica")
        , max_fusion_depth(5)
        , memory_budget_ratio(0.8f) {}
};

// YICA Graph Manager for computation graph optimization
class YICAGraphManager {
public:
    YICAGraphManager();
    ~YICAGraphManager();
    
    // Graph construction
    uint32_t add_input_node(const std::vector<uint32_t>& shape,
                           const std::string& dtype = "float32",
                           const std::string& name = "");
    
    uint32_t add_operation_node(const std::string& op_name,
                               const std::vector<uint32_t>& input_node_ids,
                               const std::vector<std::vector<uint32_t>>& output_shapes,
                               const std::unordered_map<std::string, std::string>& attrs = {});
    
    bool mark_output_node(uint32_t node_id);
    
    // Graph optimization
    bool optimize_graph(const YICAOptimizationConfig& config = YICAOptimizationConfig{});
    
    // Graph execution
    bool execute_graph(const std::vector<void*>& inputs,
                      std::vector<void*>& outputs);
    
    // Graph analysis
    std::vector<YICAGraphNode> get_all_nodes() const;
    std::vector<uint32_t> get_input_nodes() const;
    std::vector<uint32_t> get_output_nodes() const;
    uint32_t get_node_count() const;
    
    // Graph serialization
    std::string serialize_to_json() const;
    bool deserialize_from_json(const std::string& json_str);
    
    // Performance analysis
    double get_estimated_execution_time_ms() const;
    uint64_t get_estimated_memory_usage() const;
    float get_estimated_cim_utilization() const;
    
    // Debugging and visualization
    std::string generate_dot_graph() const;
    bool save_graph_visualization(const std::string& file_path) const;
    
    // Graph transformations
    bool fuse_operations(const std::vector<uint32_t>& node_ids);
    bool split_operation(uint32_t node_id, const std::vector<std::string>& sub_ops);
    bool replace_subgraph(const std::vector<uint32_t>& old_nodes,
                         const std::vector<YICAGraphNode>& new_nodes);

private:
    class Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace kernel
} // namespace yirage