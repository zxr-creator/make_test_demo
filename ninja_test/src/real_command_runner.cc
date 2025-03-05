// Copyright 2011 Google Inc. All Rights Reserved.
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

#include "build.h"
#include "subprocess.h"

struct RealCommandRunner : public CommandRunner {
  explicit RealCommandRunner(const BuildConfig& config) : config_(config) {}
  size_t CanRunMore() const override;
  bool StartCommand(Edge* edge) override;
  bool WaitForCommand(Result* result) override;
  std::vector<Edge*> GetActiveEdges() override;
  void Abort() override;

  const BuildConfig& config_;
  SubprocessSet subprocs_;
  std::map<const Subprocess*, Edge*> subproc_to_edge_;
};

// 遍历 subproc_to_edge_ 映射，将所有当前正在执行的命令对应的 Edge 收集到一个 std::vector 中并返回
std::vector<Edge*> RealCommandRunner::GetActiveEdges() {
  std::vector<Edge*> edges;
  for (std::map<const Subprocess*, Edge*>::iterator e =
           subproc_to_edge_.begin();
       e != subproc_to_edge_.end(); ++e)
    edges.push_back(e->second);
  return edges;
}

void RealCommandRunner::Abort() {
  subprocs_.Clear();
}

// 配置中设定的最大并行任务数（config_.parallelism）。

// 当前已经在跑或已完成的任务数（subprocs_.running_ 和 subprocs_.finished_）。

// 系统当前的负载情况（通过 GetLoadAverage() 获取）和配置中的最大负载限制（config_.max_load_average）。

// 特殊情况：如果没任务在跑，至少允许跑一个任务。
size_t RealCommandRunner::CanRunMore() const {
  size_t subproc_number =
      subprocs_.running_.size() + subprocs_.finished_.size();

  int64_t capacity = config_.parallelism - subproc_number;

  // 设置了最大负载上限
  if (config_.max_load_average > 0.0f) {
    int load_capacity = config_.max_load_average - GetLoadAverage();
    std::cout << "Load capacity: " << load_capacity << std::endl;
    // 实际的比可用的好
    if (load_capacity < capacity)
      capacity = load_capacity;
  }

  if (capacity < 0) {
    std::cout << "Capacity adjusted to 0 from: " << capacity << std::endl;
    capacity = 0;
  }

  if (capacity == 0 && subprocs_.running_.empty()) {
    // Ensure that we make progress.
    capacity = 1;
    std::cout << "Capacity forced to 1 when running is empty" << std::endl;
  }

  std::cout << "Final capacity: " << capacity << std::endl;
  return capacity;
}

bool RealCommandRunner::StartCommand(Edge* edge) {
  std::string command = edge->EvaluateCommand();
  Subprocess* subproc = subprocs_.Add(command, edge->use_console());
  if (!subproc)
    return false;
  subproc_to_edge_.insert(std::make_pair(subproc, edge));

  return true;
}

bool RealCommandRunner::WaitForCommand(Result* result) {
  Subprocess* subproc;
  while ((subproc = subprocs_.NextFinished()) == NULL) {
    bool interrupted = subprocs_.DoWork();
    if (interrupted)
      return false;
  }

  result->status = subproc->Finish();
  result->output = subproc->GetOutput();

  std::map<const Subprocess*, Edge*>::iterator e =
      subproc_to_edge_.find(subproc);
  result->edge = e->second;
  subproc_to_edge_.erase(e);

  delete subproc;
  return true;
}

CommandRunner* CommandRunner::factory(const BuildConfig& config) {
  return new RealCommandRunner(config);
}
