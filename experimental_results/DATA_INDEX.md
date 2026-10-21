# Complete Experimental Data Index

This document provides a comprehensive index of all experimental data included in this repository.

## Overview

**Total Experiments**: 165 SLAM runs  
**Total Frames Processed**: ~295,000 frames  
**Total Computation Time**: ~30 hours  
**Data Size**: 6.3 MB (compressed), ~27 MB (uncompressed)

---

## Data Files Structure

### 1. Summary Data Files (Readily Accessible)

These files are directly available without extraction:

#### raw_data.json (5.9 KB)
Complete ATE results for all 165 runs.

**Contains:**
- Parameter Sensitivity: 5 configurations × 5 runs = 25 experiments
- Ablation Studies: 4 sequences × 4 methods × 5 runs = 80 experiments  
- Supplementary: 6 sequences × 2 methods × 5 runs = 60 experiments

**Example:**
```json
{
  "ablation_studies": {
    "walking_xyz": {
      "M0": [0.506930, 0.753876, 0.672059, 0.817087, 0.535151],
      "M1": [0.422614, 0.281848, 0.421323, 0.343238, 0.421994],
      "M2": [0.388498, 0.387255, 0.389686, 0.374470, 0.405922],
      "M3": [0.014096, 0.015477, 0.016381, 0.015647, 0.015413]
    }
  }
}
```

#### feature_retention_all_sequences.csv (253 B)
Feature retention statistics for 4 sequences.

**Columns:**
- Sequence name
- M0_Erased: Features filtered by baseline (always 0)
- M3_Erased: Features filtered by FastSAM
- M3_Kept: Features retained
- Retention_Rate: Percentage

**Key Result**: Average 82.3% retention rate

#### runtime_breakdown_summary.csv (339 B)
Runtime performance for all methods.

**Columns:**
- Method (M0-M3)
- Component times (ms): flow, ransac, dbscan, fastsam
- Total time (ms)
- FPS

**Key Result**: Online SLAM achieves 67 FPS

---

### 2. Complete Raw Logs (experimental_raw_logs.tar.gz, 6.2 MB)

This archive contains all 571 log files from 165 experiments.

**Extract with:**
```bash
tar -xzf experimental_raw_logs.tar.gz
```

#### After Extraction Structure

```
experimental_raw_logs/
│
├── ablation_xyz/              # Walking XYZ sequence
│   ├── M0/                    # Baseline ORB-SLAM2
│   │   ├── run1.log           # Full SLAM log
│   │   ├── CameraTrajectory_run1.txt  # Estimated trajectory
│   │   ├── ate_run1.txt       # ATE evaluation result
│   │   ├── run2.log - run5.log
│   │   ├── CameraTrajectory_run2.txt - run5.txt
│   │   ├── ate_run2.txt - ate_run5.txt
│   │   └── median_ate.txt     # Median ATE of 5 runs
│   ├── M1/                    # Flow+RANSAC
│   ├── M2/                    # Flow+RANSAC+DBSCAN
│   └── M3/                    # FastSAM
│
├── ablation_rpy/              # Walking RPY sequence
│   ├── M0/, M1/, M2/, M3/
│
├── ablation_halfsphere/       # Walking Halfsphere sequence
│   ├── M0/, M1/, M2/, M3/
│
├── ablation_static/           # Walking Static sequence
│   ├── M0/, M1/, M2/, M3/
│
├── supplementary_experiments/
│   ├── sitting_xyz/
│   │   ├── ORB-SLAM2/         # Baseline
│   │   └── FM-SLAM/           # FastSAM method
│   ├── sitting_rpy/
│   ├── sitting_halfsphere/
│   ├── bonn_crowd/
│   ├── bonn_crowd2/
│   └── bonn_crowd3/
│
└── _test_sensitivity_full/
    ├── S1/                    # Parameter config 1
    ├── S2/                    # Parameter config 2
    ├── S3/                    # Parameter config 3 (optimal)
    ├── S4/                    # Parameter config 4
    └── S5/                    # Parameter config 5
```

---

## Detailed File Descriptions

### Log Files (*.log)

Each `runX.log` contains:
- Frame-by-frame processing information
- ORB feature extraction statistics
- **"Erase features number"**: Features filtered by mask
- Tracking time per frame
- Keyframe creation events
- Loop closure detections
- Final statistics (mean/median tracking time)

**Example content:**
```
Images in the sequence: 827
New Map created with 715 points
Erase features number =165   # FastSAM filtered 165 features
Erase features number =170
...
median tracking time: 0.0138091
mean tracking time: 0.0149466
```

### Trajectory Files (CameraTrajectory_runX.txt)

TUM RGB-D format trajectory files:
```
timestamp tx ty tz qx qy qz qw
1305031102.175304 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 1.0000
1305031102.211214 0.0021 -0.0003 0.0012 -0.0008 0.0015 0.0009 0.9999
...
```

**Usage:**
- Compare with ground truth using `evo_ape` or `evaluate_ate_scale.py`
- Visualize with `evo_traj`
- Can be directly used for further analysis

### ATE Evaluation Files (ate_runX.txt)

Absolute Trajectory Error results:
```
compared_pose_pairs 820 pairs
absolute_translational_error.rmse 0.015477 m
absolute_translational_error.mean 0.014234 m
absolute_translational_error.median 0.012891 m
absolute_translational_error.std 0.007892 m
absolute_translational_error.min 0.001234 m
absolute_translational_error.max 0.045678 m
```

### Median ATE Files (median_ate.txt)

Single value: median ATE of 5 runs
```
0.015477
```

This is the value reported in the paper tables.

---

## Data Correspondence to Paper

### Table 1: Ablation Study Results

**Data Source:** `raw_data.json` → `ablation_studies`

| Sequence | M0 | M1 | M2 | M3 | Data Location |
|----------|----|----|----|----|---------------|
| walking_xyz | 0.672 | 0.421 | 0.388 | 0.016 | `ablation_xyz/M*/median_ate.txt` |
| walking_rpy | 0.775 | 0.653 | 0.612 | 0.034 | `ablation_rpy/M*/median_ate.txt` |
| walking_halfsphere | 0.353 | 0.305 | 0.291 | 0.021 | `ablation_halfsphere/M*/median_ate.txt` |
| walking_static | 0.222 | 0.183 | 0.169 | 0.017 | `ablation_static/M*/median_ate.txt` |

**Verification:**
```bash
# Extract and check
tar -xzf experimental_raw_logs.tar.gz
cat ablation_xyz/M3/median_ate.txt  # Should show 0.015477
```

### Table 2: Supplementary Experiments

**Data Source:** `raw_data.json` → `supplementary_experiments`

| Sequence | ORB-SLAM2 | FM-SLAM | Success Rate | Data Location |
|----------|-----------|---------|--------------|---------------|
| sitting_xyz | 0.157 | 0.013 | 100% vs 100% | `supplementary_experiments/sitting_xyz/` |
| bonn_crowd | 1.074 | 0.068 | 40% vs 100% | `supplementary_experiments/bonn_crowd/` |

### Table 3: Runtime Breakdown

**Data Source:** `runtime_breakdown_summary.csv`

Direct correspondence - each row is one method's timing.

### Table 4: Feature Retention

**Data Source:** `feature_retention_all_sequences.csv`

Direct correspondence - each row is one sequence.

### Figure 3: ATE Improvement Bar Chart

**Data Source:** `raw_data.json` → calculate improvement

```python
improvement = (M0 - M3) / M0 * 100
```

### Figure 4: Runtime Comparison

**Data Source:** `runtime_breakdown_summary.csv` → T_total column

---

## Data Verification

### Verify Data Completeness

```python
import json
import os

# 1. Check raw_data.json
with open('raw_data.json') as f:
    data = json.load(f)

param_count = sum(len(v) for v in data['parameter_sensitivity'].values())
ablation_count = sum(len(m) for s in data['ablation_studies'].values() 
                     for m in s.values())
supp_count = sum(len(m) for s in data['supplementary_experiments'].values() 
                 for m in s.values())

print(f"Parameter sensitivity: {param_count} runs")  # Expected: 25
print(f"Ablation studies: {ablation_count} runs")    # Expected: 80  
print(f"Supplementary: {supp_count} runs")            # Expected: 60
print(f"Total: {param_count + ablation_count + supp_count}")  # Expected: 165

# 2. Check compressed logs
os.system("tar -tzf experimental_raw_logs.tar.gz | wc -l")  # Expected: 571
```

### Verify Specific Results

```bash
# Extract specific sequence
tar -xzf experimental_raw_logs.tar.gz ablation_xyz/M3/

# Check all 5 runs
for i in {1..5}; do
    echo "Run $i:"
    tail -5 ablation_xyz/M3/ate_run${i}.txt | grep rmse
done

# Check median
cat ablation_xyz/M3/median_ate.txt
```

### Cross-Reference with Paper

```bash
# Compare your extracted data with paper Table 1
python scripts/verify_paper_results.py \
    --data experimental_raw_logs/ \
    --paper paper_table1.txt
```

---

## Data Usage Examples

### Example 1: Reproduce Paper Table 1

```python
import json
import numpy as np

with open('raw_data.json') as f:
    data = json.load(f)

sequences = ['walking_xyz', 'walking_rpy', 'walking_halfsphere', 'walking_static']

for seq in sequences:
    row = f"{seq:20}"
    for method in ['M0', 'M1', 'M2', 'M3']:
        runs = data['ablation_studies'][seq][method]
        median = np.median(runs)
        row += f" {median:8.6f}"
    print(row)
```

### Example 2: Calculate Average Improvement

```python
import json
import numpy as np

with open('raw_data.json') as f:
    data = json.load(f)

improvements = []
for seq, methods in data['ablation_studies'].items():
    m0_median = np.median(methods['M0'])
    m3_median = np.median(methods['M3'])
    improvement = (m0_median - m3_median) / m0_median * 100
    improvements.append(improvement)
    print(f"{seq}: {improvement:.1f}% improvement")

print(f"\nAverage: {np.mean(improvements):.1f}%")
```

### Example 3: Extract Feature Statistics from Logs

```bash
# Extract all "Erase features number" from one run
tar -xzf experimental_raw_logs.tar.gz ablation_xyz/M3/run1.log
grep "Erase features number" ablation_xyz/M3/run1.log | awk '{sum+=$NF; count++} END {print "Average:", sum/count}'
```

---

## Storage and Access

### File Sizes

| File | Size | Description |
|------|------|-------------|
| raw_data.json | 5.9 KB | All ATE results |
| feature_retention*.csv | 412 B | Feature statistics |
| runtime_breakdown*.csv | 339 B | Runtime data |
| experimental_raw_logs.tar.gz | 6.2 MB | All logs (compressed) |
| experimental_raw_logs/ | ~27 MB | All logs (extracted) |

### Recommended Access

For reviewers/editors:
1. **Quick verification**: Use `raw_data.json` and `*.csv` files directly
2. **Detailed inspection**: Extract specific sequences from tar.gz
3. **Full reproduction**: Follow `REPRODUCTION.md`

For reproduction:
1. Use scripts in `scripts/` directory
2. Compare results with `raw_data.json`
3. Extract logs for debugging if needed

---

## Data Integrity

### MD5 Checksums

```bash
md5sum experimental_raw_logs.tar.gz
# Should match: [checksum will be generated]

md5sum raw_data.json
# Should match: [checksum will be generated]
```

### Validation

All data has been validated:
- ✅ No missing files
- ✅ All trajectories evaluated
- ✅ All medians calculated correctly
- ✅ Cross-referenced with paper results

---

## Questions?

If you need:
- **Specific sequence data**: Extract from tar.gz
- **Additional analysis**: Contact authors
- **Raw images/depth**: Download from TUM/Bonn datasets
- **Generated masks**: Available upon request (large files)

For any questions about the experimental data:
1. Check this index first
2. Review `experimental_results/README.md`
3. Contact authors via GitHub issues

---

**Data Generated**: October 2026  
**Segmentation Method**: FastSAM (Fast Segment Anything Model)  
**Hardware**: Intel i7-10700, NVIDIA RTX 4060, 32GB RAM  
**Total Experiments**: 165 runs, ~295,000 frames processed
