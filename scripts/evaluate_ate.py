#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evaluate ATE (Absolute Trajectory Error) for ablation study results
Calculates median ATE from 5 runs for each method
"""
import os
import subprocess
import sys
import json
import argparse
import numpy as np
from pathlib import Path


def evaluate_ate(trajectory_file, groundtruth_file, eval_script):
    """
    Evaluate ATE using evo or custom script

    Args:
        trajectory_file: Estimated trajectory
        groundtruth_file: Ground truth trajectory
        eval_script: Path to evaluation script

    Returns:
        ATE value (RMSE) or None if failed
    """
    try:
        # Use evo if available
        result = subprocess.run(
            ['evo_ape', 'tum', groundtruth_file, trajectory_file,
             '--align', '--silent'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            # Parse evo output
            for line in result.stdout.split('\n'):
                if 'rmse' in line.lower():
                    ate = float(line.split()[-1])
                    return ate
        else:
            # Fallback to custom script
            result = subprocess.run(
                ['python', eval_script, groundtruth_file, trajectory_file],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Parse output (assuming last number is ATE)
                lines = result.stdout.strip().split('\n')
                for line in reversed(lines):
                    try:
                        ate = float(line.split()[-1])
                        return ate
                    except:
                        continue
    except Exception as e:
        print(f"    Error evaluating ATE: {e}")
        return None

    return None


def process_sequence(results_dir, sequence, groundtruth_dir, eval_script):
    """
    Process one sequence: evaluate all methods and runs

    Args:
        results_dir: Root results directory
        sequence: Sequence name
        groundtruth_dir: Ground truth directory
        eval_script: Evaluation script path

    Returns:
        Dictionary with results
    """
    seq_short = sequence.replace('rgbd_dataset_freiburg3_', '')
    groundtruth_file = os.path.join(groundtruth_dir, f"{sequence}.txt")

    if not os.path.exists(groundtruth_file):
        # Try alternative naming
        groundtruth_file = os.path.join(groundtruth_dir, f"{seq_short}.txt")

    if not os.path.exists(groundtruth_file):
        print(f"Warning: Ground truth not found for {sequence}")
        return None

    results = {}

    for method in ['M0', 'M1', 'M2', 'M3']:
        method_dir = os.path.join(results_dir, sequence, method)

        if not os.path.exists(method_dir):
            continue

        ate_values = []

        for run in range(1, 6):
            trajectory_file = os.path.join(method_dir, f"CameraTrajectory_run{run}.txt")

            if not os.path.exists(trajectory_file):
                print(f"  {method} Run{run}: trajectory not found")
                continue

            ate = evaluate_ate(trajectory_file, groundtruth_file, eval_script)

            if ate is not None:
                ate_values.append(ate)
                print(f"  {method} Run{run}: ATE = {ate:.6f}m")
            else:
                print(f"  {method} Run{run}: evaluation failed")

        if ate_values:
            median_ate = float(np.median(ate_values))
            results[method] = {
                'runs': ate_values,
                'median': median_ate,
                'mean': float(np.mean(ate_values)),
                'std': float(np.std(ate_values))
            }

            print(f"  {method} Summary: Median={median_ate:.6f}m, Mean={np.mean(ate_values):.6f}m")
        else:
            print(f"  {method}: No valid results")

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Evaluate ATE for ablation study results'
    )
    parser.add_argument(
        '--results',
        type=str,
        required=True,
        help='Results directory (output from run_ablation_study.sh)'
    )
    parser.add_argument(
        '--groundtruth',
        type=str,
        default='./evaluation/Ground_truth',
        help='Ground truth directory (default: ./evaluation/Ground_truth)'
    )
    parser.add_argument(
        '--eval-script',
        type=str,
        default='./evaluation/evaluate_ate_scale.py',
        help='Evaluation script (default: ./evaluation/evaluate_ate_scale.py)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='ate_results.json',
        help='Output JSON file (default: ate_results.json)'
    )

    args = parser.parse_args()

    # Find sequences
    sequences = []
    for item in os.listdir(args.results):
        item_path = os.path.join(args.results, item)
        if os.path.isdir(item_path) and item.startswith('rgbd_'):
            sequences.append(item)

    sequences.sort()

    if not sequences:
        print(f"Error: No sequences found in {args.results}")
        sys.exit(1)

    print("="*60)
    print("ATE Evaluation for Ablation Study")
    print("="*60)
    print(f"Results dir: {args.results}")
    print(f"Ground truth: {args.groundtruth}")
    print(f"Sequences: {len(sequences)}")
    print("="*60)

    # Process each sequence
    all_results = {}

    for sequence in sequences:
        print(f"\n[{sequence}]")
        results = process_sequence(
            args.results,
            sequence,
            args.groundtruth,
            args.eval_script
        )

        if results:
            all_results[sequence] = results

    # Save results
    with open(args.output, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✓ Results saved to: {args.output}")

    # Print summary table
    print("\n" + "="*60)
    print("Summary Table (Median ATE in meters)")
    print("="*60)
    print(f"{'Sequence':<30} {'M0':>8} {'M1':>8} {'M2':>8} {'M3':>8}")
    print("-"*60)

    for sequence in sorted(all_results.keys()):
        seq_short = sequence.replace('rgbd_dataset_freiburg3_', '')
        row = f"{seq_short:<30}"

        for method in ['M0', 'M1', 'M2', 'M3']:
            if method in all_results[sequence]:
                ate = all_results[sequence][method]['median']
                row += f" {ate:>8.6f}"
            else:
                row += f" {'N/A':>8}"

        print(row)

    print("="*60)


if __name__ == '__main__':
    main()
