#! /bin/bash

# Runs all quadratice placement benchmarks
dir_path="router"
benchmarks_path="$dir_path/benchmarks"
output_path="$dir_path/out"
benchmarks=("bench1")
# benchmarks=("bench1" "bench2" "bench3" "bench4" "bench5")
extra_benchmarks=("fract2" "industry1" "primary1")

for benchmark in "${benchmarks[@]}"; do
    # Run python program
    python3 "$dir_path/router.py" "$benchmarks_path/$benchmark.grid" "$benchmarks_path/$benchmark.nl" "$output_path/$benchmark"
done