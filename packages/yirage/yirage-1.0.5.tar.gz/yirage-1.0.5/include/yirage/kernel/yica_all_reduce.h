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

namespace yirage {
namespace kernel {

// All-reduce operation types
enum class AllReduceOpType : int32_t {
    SUM = 0,
    MEAN = 1,
    MAX = 2,
    MIN = 3,
    PROD = 4
};

// YICA All-Reduce Operation for distributed computing
class YICAAllReduceOp {
public:
    struct Config {
        bool use_hardware_acceleration;
        uint32_t preferred_cim_array;
        std::string data_type;
        std::string communication_backend;  // "nccl", "yccl", "mpi"
        uint32_t ring_buffer_size;
        
        Config() : use_hardware_acceleration(true), preferred_cim_array(0),
                  data_type("float32"), communication_backend("yccl"),
                  ring_buffer_size(1024 * 1024) {}
    };
    
    YICAAllReduceOp(const Config& config = Config{});
    ~YICAAllReduceOp();
    
    // All-reduce operation
    bool forward(void* data, uint64_t num_elements,
                AllReduceOpType op_type,
                const std::string& dtype = "float32");
    
    // Asynchronous all-reduce
    bool forward_async(void* data, uint64_t num_elements,
                      AllReduceOpType op_type,
                      const std::string& dtype = "float32");
    
    // Wait for asynchronous operation
    bool wait();
    
    // Performance metrics
    double get_last_execution_time_ms() const;
    float get_communication_bandwidth_mbps() const;
    
    // Configuration
    void set_config(const Config& config);
    Config get_config() const;
    
    // Distributed setup
    bool initialize_distributed(int rank, int world_size);
    void finalize_distributed();

private:
    class Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace kernel
} // namespace yirage