#!/usr/bin/env python3
import argparse
import subprocess
import re
import os

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
    updated_dot = "updated_dependencies.dot"

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
    ####################################################################
    print(f"node_to_token_assigned:{node_to_token_assigned}")
    print(f"Annotating {dependencies_dot} -> {updated_dot}")

    with open(dependencies_dot, "r") as f:
        dot_lines = f.readlines()

    updated_dot_lines = []
    label_node_re = re.compile(r'n(\d+)\[label="([^"]+)"')
    for line in dot_lines:
        match = label_node_re.search(line)
        if match:
            node_num, label_text = match.groups()
            # print(f"node_num:{node_num}, label_text:{label_text}")
            if label_text in node_to_token_assigned:
                token = node_to_token_assigned[label_text]
                new_label = f'{label_text}_{token}'
                print(f"new_label:{new_label}")
                line = line.replace(f'label="{label_text}"', f'label="{new_label}"')
        updated_dot_lines.append(line)

    with open(updated_dot, "w") as f:
        f.writelines(updated_dot_lines)

    if not args.no_svg:
        updated_svg = "updated_dependencies.svg"
        print(f"Generating {updated_svg} from {updated_dot}")
        subprocess.run(["dot", "-Tsvg", updated_dot, "-o", updated_svg], check=False)

    print("All done.")

if __name__ == "__main__":
    main()
