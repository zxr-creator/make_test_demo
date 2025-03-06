#ifndef PROFILER_H
#define PROFILER_H

#ifdef __cplusplus
#include <chrono>
#include <map>
#include <string>
#include <vector>
#include <thread> // For std::thread::hardware_concurrency()

extern unsigned int job_slots;
class Profiler {
    public:
        Profiler(int n = 7, int m = 5) 
            : root_duration(0), 
              root_start_set(false),
              max_levels(n),
              max_items_per_level(m),
              job_slots_value(job_slots) {} // Initialize with arg_job_slots from main.c
    
        void rootStart();
        void rootEnd();
        void operationStart(int level, const std::string& operation_name);
        void operationEnd(int level, const std::string& operation_name);
    
    private:
        std::chrono::time_point<std::chrono::high_resolution_clock> root_start;
        long long root_duration;
        bool root_start_set;
        int max_levels;
        int max_items_per_level;
        unsigned int job_slots_value; // Store the job slots value
        std::map<int, std::map<std::string, long long>> level_name_duration;
        std::map<int, std::map<std::string, std::vector<std::chrono::time_point<std::chrono::high_resolution_clock>>>> level_start_times;
};

extern "C" {
    #endif
    void profiler_root_start();
    void profiler_root_end();
    void profiler_operation_start(int level, const char* operation_name);
    void profiler_operation_end(int level, const char* operation_name);

#ifdef __cplusplus
}
#endif

#endif // PROFILER_H

#include "profiler.h"
#include <iostream>
#include <algorithm>
#include <cstdlib> // For std::getenv and std::atoi

static Profiler profiler; // Singleton instance

void Profiler::rootStart() {
    if (root_start_set) {
        std::cout << "[DEBUG] 错误:root 已开始" << std::endl;
        return;
    }
    root_start = std::chrono::high_resolution_clock::now();
    root_start_set = true;
    std::cout << "[DEBUG] starting profiling" << std::endl;
}

void Profiler::rootEnd() {
    if (!root_start_set) {
        std::cout << "[DEBUG] 错误:root 未开始" << std::endl;
        return;
    }
    if (root_duration != 0) {
        std::cout << "[DEBUG] 错误:root 已结束" << std::endl;
        return;
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    root_duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - root_start).count();

    unsigned int nproc = std::thread::hardware_concurrency();
    if (nproc == 0) {
        nproc = 1; // Fallback to 1 if hardware_concurrency() fails
    }
    
    std::cout << "*******************************************************************************" << std::endl;
    std::cout << "[DEBUG] 总耗时: " << root_duration << " 微秒" << std::endl;
    std::cout << "[DEBUG] Command used: $MAKE_PATH -j" << nproc << " -l" << nproc 
              << " 2>&1 | tee -a \"$LOG_FILE\"" << std::endl;
    std::cout << "[DEBUG] finish profiling" << std::endl;

    int level_count = 1;
    for (const auto& level_pair : level_name_duration) {
        if (level_count > max_levels) break;
        
        int level = level_pair.first;
        const auto& name_duration = level_pair.second;

        std::vector<std::pair<std::string, long long>> sorted_names(name_duration.begin(), name_duration.end());
        std::sort(sorted_names.begin(), sorted_names.end(),
                  [](const auto& a, const auto& b) { return a.second > b.second; });

        std::cout << "\n[DEBUG] Level " << level << " 前 " << max_items_per_level << " 个耗时最多的记录:" << std::endl;
        int count = 0;
        for (const auto& pair : sorted_names) {
            if (count >= max_items_per_level) break;
            double percentage = (pair.second * 100.0) / root_duration;
            std::cout << "[DEBUG]   " << pair.first << ": " << pair.second << " 微秒 (" << percentage << "%)" << std::endl;
            count++;
        }
        level_count++;
    }
}
void Profiler::operationStart(int level, const std::string& operation_name) {
    auto& starts = level_start_times[level][operation_name];
    starts.push_back(std::chrono::high_resolution_clock::now());
}

void Profiler::operationEnd(int level, const std::string& operation_name) {
    auto now = std::chrono::high_resolution_clock::now();
    auto& starts = level_start_times[level][operation_name];
    if (starts.empty()) {
        std::cout << "[DEBUG] 错误：操作 " << operation_name << " 在 level " << level << " 未开始" << std::endl;
        return;
    }
    auto start_time = starts.back();
    starts.pop_back();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(now - start_time).count();
    level_name_duration[level][operation_name] += duration;
}

extern "C" void profiler_root_start() {
    profiler.rootStart();
}

extern "C" void profiler_root_end() {
    profiler.rootEnd();
}

extern "C" void profiler_operation_start(int level, const char* operation_name) {
    profiler.operationStart(level, std::string(operation_name));
}

extern "C" void profiler_operation_end(int level, const char* operation_name) {
    profiler.operationEnd(level, std::string(operation_name));
}