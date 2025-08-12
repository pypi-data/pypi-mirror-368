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

// Reduction operation types
enum class ReductionOpType : int32_t {
    SUM = 0,
    MEAN = 1,
    MAX = 2,
    MIN = 3,
    PROD = 4,
    VAR = 5,
    STD = 6,
    L1_NORM = 7,
    L2_NORM = 8
};

// YICA Reduction Operations
class YICAReductionOp {
public:
    struct Config {
        bool use_hardware_acceleration;
        uint32_t preferred_cim_array;
        std::string data_type;
        bool enable_tree_reduction;
        uint32_t reduction_block_size;
        
        Config() : use_hardware_acceleration(true), preferred_cim_array(0),
                  data_type("float32"), enable_tree_reduction(true),
                  reduction_block_size(1024) {}
    };
    
    YICAReductionOp(const Config& config = Config{});
    ~YICAReductionOp();
    
    // Reduction along specified dimensions
    bool forward(const void* input, void* output,
                ReductionOpType op_type,
                const std::vector<uint32_t>& input_shape,
                const std::vector<int32_t>& reduction_dims,
                bool keep_dims = false,
                const std::string& dtype = "float32");
    
    // Full tensor reduction
    bool forward_full(const void* input, void* output,
                     ReductionOpType op_type,
                     uint64_t num_elements,
                     const std::string& dtype = "float32");
    
    // Performance metrics
    double get_last_execution_time_ms() const;
    float get_reduction_efficiency() const;
    
    // Configuration
    void set_config(const Config& config);
    Config get_config() const;

private:
    class Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace kernel
} // namespace yirage