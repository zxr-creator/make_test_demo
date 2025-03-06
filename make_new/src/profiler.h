#ifndef PROFILER_H
#define PROFILER_H

#ifdef __cplusplus
#include <chrono>
#include <map>
#include <string>
#include <vector>

// Forward declaration from main.c
extern unsigned int job_slots;

class Profiler {
public:
    Profiler(int n = 7, int m = 5) 
        : root_duration(0), 
          root_start_set(false),
          max_levels(n),
          max_items_per_level(m),
          job_slots_value(job_slots) {} // Initialize with job_slots from main.c

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
    unsigned int job_slots_value; // Store the job slots value from -j
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