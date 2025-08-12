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
#include <functional>

namespace yirage {
namespace kernel {

// Custom kernel parameter
struct CustomKernelParam {
    std::string name;
    std::string type;
    void* data;
    size_t size;
    
    CustomKernelParam(const std::string& n, const std::string& t, void* d, size_t s)
        : name(n), type(t), data(d), size(s) {}
};

// YICA Customized Operation for user-defined kernels
class YICACustomizedOp {
public:
    using KernelFunction = std::function<bool(const std::vector<CustomKernelParam>&)>;
    
    struct Config {
        bool use_hardware_acceleration;
        uint32_t preferred_cim_array;
        std::string kernel_name;
        std::string kernel_source;  // YIS assembly or Triton code
        std::string kernel_language; // "yis", "triton", "cuda"
        bool enable_jit_compilation;
        
        Config() : use_hardware_acceleration(true), preferred_cim_array(0),
                  kernel_language("yis"), enable_jit_compilation(true) {}
    };
    
    YICACustomizedOp(const Config& config = Config{});
    ~YICACustomizedOp();
    
    // Load custom kernel from source
    bool load_kernel_from_source(const std::string& source,
                                const std::string& language = "yis");
    
    // Load custom kernel from file
    bool load_kernel_from_file(const std::string& file_path);
    
    // Register custom kernel function
    bool register_kernel_function(const std::string& name,
                                 const KernelFunction& function);
    
    // Execute custom kernel
    bool execute(const std::vector<CustomKernelParam>& params);
    
    // Execute with automatic parameter inference
    bool execute_auto(const std::vector<void*>& inputs,
                     const std::vector<void*>& outputs,
                     const std::vector<std::vector<uint32_t>>& shapes,
                     const std::string& dtype = "float32");
    
    // Kernel compilation and optimization
    bool compile_kernel();
    bool optimize_kernel();
    
    // Performance metrics
    double get_last_execution_time_ms() const;
    std::string get_kernel_assembly() const;
    
    // Configuration
    void set_config(const Config& config);
    Config get_config() const;
    
    // Debugging and profiling
    void enable_profiling(bool enabled);
    std::vector<std::string> get_profiling_info() const;

private:
    class Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace kernel
} // namespace yirage