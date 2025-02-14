#!/usr/bin/env python3
import argparse
import subprocess
import re
import os

def print_parallel_sequence(args, make_log_path):
    """
    This function re-parses the make debug log and records the parallel execution sequence.
    It writes the sequence to a text file named "make_d_j{jobs}_seq.txt". Each line has:
        time_index  n1 pid_of_n1 n2 pid_of_n2 n3 pid_of_n3 ...
    where the nodes listed are those concurrently running at that moment.
    """
    # Prepare output file name.
    seq_filename = f"make_d_j{args.jobs}_seq.txt"
    
    # Regexes for child addition events:
    live_child_re   = re.compile(r"Live child \S+ \((n\d+)\) PID (\d+)")
    putting_child_re = re.compile(r"Putting child \S+ \((n\d+)\) PID (\d+)")
    # Removal events: including both "Reaping winning child" and "Removing child".
    child_done_re   = re.compile(r"(?:Reaping winning child|Removing child) \S+(?: \((n\d+)\))? PID (\d+)")
    
    # Data structure to track currently running processes.
    current_live = {}   # mapping: pid -> node
    snapshots = []      # list of snapshots: each is (time_index, list of (node, pid))
    time_index = 0      # incremental index for each state change
    
    def record_snapshot():
        nonlocal time_index
        # Create a sorted list by node name for a consistent order.
        snapshot = sorted([(node, pid) for pid, node in current_live.items()], key=lambda x: x[0])
        # Only record if there is at least one running process.
        if snapshot:
            time_index += 1
            snapshots.append((time_index, snapshot))
    
    with open(make_log_path, "r") as f:
        for line in f:
            changed = False
            # (a) Check for child addition events.
            match = live_child_re.search(line)
            if not match:
                match = putting_child_re.search(line)
            if match:
                node, pid = match.groups()
                # If the pid is not already recorded, add it.
                if pid not in current_live:
                    current_live[pid] = node
                    changed = True
            # (b) Check for removal events.
            done_match = child_done_re.search(line)
            if done_match:
                # The node may be present as an optional group.
                _, pid = done_match.groups()
                if pid in current_live:
                    del current_live[pid]
                    changed = True
            if changed:
                record_snapshot()
    
    # Write the snapshots to file.
    with open(seq_filename, "w") as out:
        for idx, snapshot in snapshots:
            # Format: time_index n1 pid n2 pid ...
            line_items = [str(idx)]
            for node, pid in snapshot:
                line_items.append(node)
                line_items.append(pid)
            out.write(" ".join(line_items) + "\n")
    print(f"Parallel execution sequence written to {seq_filename}")

def main():
    parser = argparse.ArgumentParser(
        description="Run Make with concurrency, parse logs using live/putting-child events, and annotate DOT file."
    )
    parser.add_argument(
        "--jobs", "-j",
        type=int,
        default=2,
        help="Number of parallel jobs for make (default is 2)."
    )
    parser.add_argument(
        "--no-svg",
        action="store_true",
        help="Skip generating SVG files with dot."
    )
    parser.add_argument(
        "--make-target",
        default="",
        help="Optional make target(s). For example: 'all' or 'clean install'."
    )
    parser.add_argument(
        "--extra-make-args",
        default="",
        help="Extra arguments to pass to make. For example: '--always-make' or 'CFLAGS=-O2'."
    )
    args = parser.parse_args()

    # Define filenames based on the number of jobs.
    make_log_path = f"make_d_j{args.jobs}.txt"
    dependencies_dot = "dependencies.dot"
    updated_dot = f"make_d_j{args.jobs}.dot"

    ####################################################################
    # 0. Clean the build.
    ####################################################################
    print("Running 'make clean' to clean the build...")
    subprocess.run(["make", "clean"], check=False)

    ####################################################################
    # 1. Run `make -d -jN` and capture debug logs.
    ####################################################################
    make_cmd = ["make", "-d", f"-j{args.jobs}"]
    if args.make_target.strip():
        make_cmd.extend(args.make_target.strip().split())
    if args.extra_make_args.strip():
        make_cmd.extend(args.extra_make_args.strip().split())

    print(f"Running: {' '.join(make_cmd)} > {make_log_path}")
    with open(make_log_path, "w") as f_out:
        # Collect stdout and stderr into one log.
        subprocess.run(make_cmd, stdout=f_out, stderr=f_out, check=False)

    ####################################################################
    # 2. Generate the DOT file via `make -Bnd | make2graph`.
    ####################################################################
    print(f"Generating {dependencies_dot} with 'make -Bnd | make2graph'")
    with open(dependencies_dot, "w") as dot_out:
        p1 = subprocess.Popen(["make", "-Bnd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p2 = subprocess.Popen(["make2graph"], stdin=p1.stdout, stdout=dot_out)
        p1.stdout.close()
        p2.communicate()

    if not args.no_svg:
        svg_name = "dependencies.svg"
        print(f"Generating {svg_name} from {dependencies_dot}")
        subprocess.run(["dot", "-Tsvg", dependencies_dot, "-o", svg_name], check=False)

    ####################################################################
    # 3. Parse the make debug log for concurrency tokens.
    #
    # We watch for three kinds of events:
    #   (a) Child addition events: either via
    #         "Live child ..." lines
    #     or  "Putting child ..." lines
    #   (b) Removal events: from lines starting with either
    #         "Reaping winning child ..." or "Removing child ..."
    #   (c) Explicit token release lines: "Released token for child ..."
    #
    # When a child event (a) is seen for a PID not currently live,
    # we assign it a token (using a free token if available, or a new one)
    # and record the token for its node. Once a token is assigned to a node,
    # that mapping remains (even if the token is later freed).
    ####################################################################
    print(f"Parsing concurrency from {make_log_path}")

    # Regexes for child addition events:
    live_child_re   = re.compile(r"Live child \S+ \((n\d+)\) PID (\d+)")
    putting_child_re = re.compile(r"Putting child \S+ \((n\d+)\) PID (\d+)")
    # Removal events: now including both "Reaping winning child" and "Removing child".
    child_done_re   = re.compile(r"(?:Reaping winning child|Removing child) \S+(?: \((n\d+)\))? PID (\d+)")
    # Explicit token release.

    # Data structures.
    current_live = set()    # Set of active PIDs.
    pid_to_token = {}       # Mapping: PID -> token (e.g. "j1")
    pid_to_node = {}        # Mapping: PID -> node (e.g. "n18")
    # Permanent assignment: once a node gets a token, it is recorded.
    node_to_token_assigned = {}

    free_tokens = []        # Tokens that have been freed and are available.
    used_tokens_count = 0   # Count of tokens created.

    with open(make_log_path, "r") as f:
        for line in f:
            # (a) Check for child addition events.
            match = live_child_re.search(line)
            if not match:
                match = putting_child_re.search(line)
            if match:
                node, pid = match.groups()
                if pid not in current_live:
                    current_live.add(pid)
                    # If this PID has not been assigned a token yet, assign one.
                    if pid not in pid_to_token:
                        if free_tokens:
                            token = free_tokens.pop()  # Reuse a token.
                        else:
                            used_tokens_count += 1
                            token = f"j{used_tokens_count}"
                        pid_to_token[pid] = token
                        pid_to_node[pid] = node
                        # Permanently record the token for this node if not already set.
                        if node not in node_to_token_assigned:
                            node_to_token_assigned[node] = token
                continue

            # (b) Check for removal events.
            done_match = child_done_re.search(line)
            if done_match:
                # The node may be present as an optional group.
                node_optional, pid = done_match.groups()
                if pid in current_live:
                    current_live.remove(pid)
                if pid in pid_to_token:
                    token = pid_to_token[pid]
                    free_tokens.append(token)
                    pid_to_token.pop(pid, None)
                if pid in pid_to_node:
                    pid_to_node.pop(pid, None)
                continue

    ####################################################################
    # 4. Update the DOT file (dependencies.dot -> updated_dependencies.dot)
    #
    # For each node in the DOT file, if we recorded a token in
    # node_to_token_assigned, append it to the label.
    # Additionally, if the total number of unique tokens is 8 or less,
    # assign a distinct color to each token.
    ####################################################################
    print(f"node_to_token_assigned:{node_to_token_assigned}")
    print(f"Annotating {dependencies_dot} -> {updated_dot}")

    # If we have 8 or fewer tokens, set up a color map.
    color_map = {
            'j1': 'red',
            'j2': 'green',
            'j3': 'blue',
            'j4': 'yellow',
            'j5': 'cyan',
            'j6': 'magenta',
            'j7': 'orange',
            'j8': 'purple',
    }

    with open(dependencies_dot, "r") as f:
        dot_lines = f.readlines()

    updated_dot_lines = []
    label_node_re = re.compile(r'(n\d+)\[label="([^"]+)"')
    for line in dot_lines:
        match = label_node_re.search(line)
        if match:
            node_id, label_text = match.groups()
            # If this label (node) has an assigned token, update it.
            if label_text in node_to_token_assigned:
                token = node_to_token_assigned[label_text]
                new_label = f'{label_text}_{token}'
                print(f"new_label:{new_label}")
                line = line.replace(f'label="{label_text}"', f'label="{new_label}"')
                # If we have a color mapping for this token, add the color attributes.
                line = re.sub(r'color="[^"]*"', f'color="{color_map[token]}"', line)
        updated_dot_lines.append(line)

    with open(updated_dot, "w") as f:
        f.writelines(updated_dot_lines)

    if not args.no_svg:
        updated_svg = f"make_d_j{args.jobs}.svg"
        print(f"Generating {updated_svg} from {updated_dot}")
        subprocess.run(["dot", "-Tsvg", updated_dot, "-o", updated_svg], check=False)

    # ------------------------------------------------------------------
    # NEW: Print the parallel execution sequence to a txt file.
    # ------------------------------------------------------------------
    print_parallel_sequence(args, make_log_path)

    print("All done.")
    subprocess.run(["make", "clean"], check=False)

if __name__ == "__main__":
    main()
