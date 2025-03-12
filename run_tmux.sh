#!/bin/bash

num_windows=8
client_session="make_test"
server_session="ninja_test"

create_tmux_session() {
    local session_name=$1
    tmux new-session -d -s $session_name

    current_path=$(pwd)

    for ((i = 0; i < num_windows; i++)); do
        tmux new-window -t $session_name:$i
    done
    echo "tmux windows created for $session_name"

    # for ((i = 0; i < num_windows; i++)); do
    #     tmux send-keys -t "$session_name:$i" "zsh" Enter
    #     tmux send-keys -t "$session_name:$i" "conda activate sgl" Enter
    #     tmux send-keys -t "$session_name:$i" "cd ${current_path}" Enter
    #     tmux send-keys -t "$session_name:$i" "export CUDA_VISIBLE_DEVICES=$i" Enter
    # done

    tmux select-window -t "$session_name:0"
}

create_tmux_session $client_session
create_tmux_session $server_session

tmux attach -t $server_session    