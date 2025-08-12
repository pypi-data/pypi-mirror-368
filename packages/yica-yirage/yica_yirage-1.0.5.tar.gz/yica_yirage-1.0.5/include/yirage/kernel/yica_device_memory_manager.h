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
#include <memory>
#include <string>

namespace yirage {
namespace kernel {

// Memory levels for YICA architecture
enum class MemoryLevel : int32_t {
    REGISTER_FILE = 0,
    SPM = 1,
    DRAM = 2
};

// Memory configuration
struct YICAMemoryConfig {
    uint64_t spm_size_per_die;
    uint64_t dram_size;
    uint32_t num_cim_arrays;
    bool enable_prefetching;
    float fragmentation_threshold;
    bool enable_spm_caching;
    uint32_t spm_cache_associativity;
    std::string spm_replacement_policy;
    
    YICAMemoryConfig() 
        : spm_size_per_die(128 * 1024 * 1024)  // 128MB default
        , dram_size(1024 * 1024 * 1024)        // 1GB default
        , num_cim_arrays(4)
        , enable_prefetching(true)
        , fragmentation_threshold(0.1f)
        , enable_spm_caching(true)
        , spm_cache_associativity(8)
        , spm_replacement_policy("LRU") {}
};

// Device memory manager for YICA
class YICADeviceMemoryManager {
public:
    YICADeviceMemoryManager(int device_id, int num_devices, const YICAMemoryConfig& config);
    ~YICADeviceMemoryManager();
    
    // Memory allocation
    void* allocate_memory(size_t size, MemoryLevel level, size_t alignment = 64);
    bool free_memory(void* ptr, MemoryLevel level);
    
    // Memory management
    bool reallocate_memory(void* old_ptr, size_t new_size, MemoryLevel level);
    size_t get_allocated_size(void* ptr, MemoryLevel level) const;
    
    // Memory statistics
    size_t get_total_memory(MemoryLevel level) const;
    size_t get_free_memory(MemoryLevel level) const;
    size_t get_used_memory(MemoryLevel level) const;
    float get_fragmentation_ratio(MemoryLevel level) const;
    
    // Memory operations
    bool copy_memory(void* dst, const void* src, size_t size, 
                    MemoryLevel dst_level, MemoryLevel src_level);
    bool set_memory(void* ptr, int value, size_t size, MemoryLevel level);
    void compact_memory(MemoryLevel level);
    
    // Device management
    static YICADeviceMemoryManager* get_instance();
    static void set_device_id(int device_id);
    
    // Configuration
    int get_device_id() const;
    int get_num_devices() const;
    const YICAMemoryConfig& get_config() const;

private:
    class Impl;
    std::unique_ptr<Impl> pimpl_;
    
    // Singleton support
    static YICADeviceMemoryManager* instance_;
    static int current_device_id_;
};

} // namespace kernel
} // namespace yirage