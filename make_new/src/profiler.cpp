#include "profiler.h"
#include <iostream>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <cstdio>    // for unlink()
#include <unistd.h>  // for getpid()

static Profiler profiler; // Singleton

extern unsigned int job_slots;

Profiler::Profiler(int n, int m)
    : root_duration(0),
      root_start_set(false),
      max_levels(n),
      max_items_per_level(m),
      job_slots_value(job_slots)
{
    // Generate a unique temp file name based on the current PID
    std::ostringstream oss;
    oss << "/tmp/make_profiler_" << getpid() << ".tmp";
    temp_file = oss.str();
}

Profiler::~Profiler() {
    // If root was started and ended, save data to the temp file
    // (so that we can potentially load it if the parent needs it).
    if (root_start_set && root_duration != 0) {
        saveToFile();
    }
}

void Profiler::rootStart() {
    if (root_start_set) {
        std::cout << "[DEBUG] 错误:root 已开始" << std::endl;
        return;
    }

    // Clear old data for a fresh run
    root_duration = 0;
    level_name_duration.clear();
    level_start_times.clear();
    job_slots_value = job_slots;

    // Also remove any stale temp file from a previous run by this same PID
    if (unlink(temp_file.c_str()) == 0) {
        std::cout << "[DEBUG] Removed stale temp file " << temp_file << std::endl;
    }

    root_start = std::chrono::high_resolution_clock::now();
    root_start_set = true;

    const char* makelevel = getenv("MAKELEVEL");
    if (makelevel && strcmp(makelevel, "0") != 0) {
        // Subprocess: don't print
        return;
    }
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
    root_duration =
        std::chrono::duration_cast<std::chrono::microseconds>(end_time - root_start).count();
}

void Profiler::operationStart(int level, const std::string& operation_name) {
    level_start_times[level][operation_name].push_back(std::chrono::high_resolution_clock::now());
}

void Profiler::operationEnd(int level, const std::string& operation_name) {
    auto now = std::chrono::high_resolution_clock::now();
    auto& starts = level_start_times[level][operation_name];
    if (starts.empty()) {
        std::cout << "[DEBUG] 错误：操作 " << operation_name
                  << " 在 level " << level << " 未开始" << std::endl;
        return;
    }
    auto start_time = starts.back();
    starts.pop_back();
    auto duration =
        std::chrono::duration_cast<std::chrono::microseconds>(now - start_time).count();
    level_name_duration[level][operation_name] += duration;
}

void Profiler::saveToFile() {
    // Write the current PID's data into its temp_file
    std::ofstream out(temp_file);
    if (!out) {
        std::cerr << "[DEBUG] 错误: 无法写入临时文件 " << temp_file << std::endl;
        return;
    }
    out << root_duration << "\n";
    for (const auto& level_pair : level_name_duration) {
        int level = level_pair.first;
        for (const auto& op_pair : level_pair.second) {
            out << level << " " << op_pair.first << " " << op_pair.second << "\n";
        }
    }
    out.close();
}

void Profiler::loadFromFile() {
    // Only read from *this* PID's temp_file, not all in /tmp
    std::ifstream in(temp_file);
    if (!in) {
        // Possibly no file if sub-make hasn't saved one yet
        std::cout << "[DEBUG] No temp file to load: " << temp_file << std::endl;
        return;
    }

    // Sum durations from the file in case multiple sub-operations wrote to it
    long long file_duration;
    in >> file_duration;
    root_duration += file_duration;

    int level;
    std::string op_name;
    long long duration;
    while (in >> level) {
        // read until the next space, then parse op_name, then parse duration
        in.get(); // skip one space
        std::getline(in, op_name, ' ');
        in >> duration;
        level_name_duration[level][op_name] += duration;
    }
    in.close();

    // Now remove the file so it doesn't get reused next time
    unlink(temp_file.c_str());
}

void Profiler::printProfile() {
    if (!root_start_set || root_duration == 0) {
        std::cout << "[DEBUG] 错误: 剖析尚未完成" << std::endl;
        return;
    }

    // Only print from top-level MAKE
    const char* makelevel = getenv("MAKELEVEL");
    if (makelevel && strcmp(makelevel, "0") != 0) {
        return;
    }

    // Here, if you want to incorporate sub-process data from the same PID's file,
    // load it. If sub-process is a different PID, you can decide how/if to unify them.
    loadFromFile();

    unsigned int nproc = job_slots_value ? job_slots_value : 1;
    std::cout << "[DEBUG] 总耗时: " << root_duration << " 微秒" << std::endl;
    std::cout << "[DEBUG] Command used: $MAKE_PATH -j" << nproc
              << " -l" << nproc << " 2>&1 | tee -a \"$LOG_FILE\"" << std::endl;
    std::cout << "[DEBUG] finish profiling" << std::endl;

    // Sort and print top items for each level
    for (const auto& level_pair : level_name_duration) {
        int level = level_pair.first;
        const auto& name_duration = level_pair.second;

        // Sort descending
        std::vector<std::pair<std::string, long long>> sorted_names(
            name_duration.begin(), name_duration.end());
        std::sort(sorted_names.begin(), sorted_names.end(),
                  [](auto &a, auto &b) { return a.second > b.second; });

        std::cout << "\n[DEBUG] Level " << level
                  << " 前 " << max_items_per_level
                  << " 个耗时最多的记录:" << std::endl;
        int count = 0;
        for (const auto& pair : sorted_names) {
            if (count >= max_items_per_level) break;
            double pct = (pair.second * 100.0) / root_duration;
            std::cout << "[DEBUG]   " << pair.first << ": "
                      << pair.second << " 微秒 (" << pct << "%)" << std::endl;
            ++count;
        }
    }
}

// Extern "C" wrappers
extern "C" void profiler_root_start() { profiler.rootStart(); }
extern "C" void profiler_root_end()   { profiler.rootEnd(); }
extern "C" void profiler_operation_start(int level, const char* name) {
    profiler.operationStart(level, std::string(name));
}
extern "C" void profiler_operation_end(int level, const char* name) {
    profiler.operationEnd(level, std::string(name));
}
extern "C" void profiler_print_profile() { profiler.printProfile(); }
