#ifndef PROFILER_H
#define PROFILER_H

#ifdef __cplusplus
#include <chrono>
#include <map>
#include <string>
#include <vector>
#include <cstring>
// Forward declaration from main.c
extern unsigned int job_slots;

class Profiler {
public:
    Profiler(int n = 7, int m = 5);
    ~Profiler();

    void rootStart();
    void rootEnd();
    void operationStart(int level, const std::string& operation_name);
    void operationEnd(int level, const std::string& operation_name);
    void printProfile(); // Print only from top-level

private:
    void saveToFile();      // Write the current profiler data to temp_file
    void loadFromFile();    // Only read from our own temp_file

    std::chrono::time_point<std::chrono::high_resolution_clock> root_start;
    long long root_duration;
    bool root_start_set;

    int max_levels;
    int max_items_per_level;
    unsigned int job_slots_value;

    // Accumulated durations for each level/operation
    std::map<int, std::map<std::string, long long>> level_name_duration;

    // Active start-times for each level/operation
    std::map<int, std::map<std::string, std::vector<std::chrono::time_point<std::chrono::high_resolution_clock>>>> level_start_times;

    std::string temp_file; // Unique temp file for this process
};

extern "C" {
#endif

void profiler_root_start();
void profiler_root_end();
void profiler_operation_start(int level, const char* operation_name);
void profiler_operation_end(int level, const char* operation_name);
void profiler_print_profile();

#ifdef __cplusplus
}
#endif

#endif // PROFILER_H
