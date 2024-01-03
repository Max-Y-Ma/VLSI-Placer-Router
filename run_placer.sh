#! /bin/bash

# Runs all quadratice placement benchmarks
dir_path="placer"
benchmarks_path="$dir_path/benchmarks"
output_path="$dir_path/out"
benchmarks=("toy1")
# benchmarks=("fract" "primary1" "struct" "toy1" "toy2")

for benchmark in "${benchmarks[@]}"; do
    # Run python program
    python3 "$dir_path/placer.py" "$benchmarks_path/$benchmark" "$output_path/$benchmark.txt"
done