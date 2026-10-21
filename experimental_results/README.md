# Experimental Results

This directory contains all experimental data supporting the FM-SLAM paper.

## Data Files

### 1. raw_data.json (5.9KB)
Complete ATE (Absolute Trajectory Error) results for all 165 SLAM runs.

**Structure:**
```json
{
  "parameter_sensitivity": {
    "S1": [run1, run2, run3, run4, run5],  // ATE in meters
    "S2": [...],
    ...
  },
  "ablation_studies": {
    "walking_xyz": {
      "M0": [...],  // Baseline
      "M1": [...],  // Flow+RANSAC
      "M2": [...],  // M1+DBSCAN
      "M3": [...]   // FastSAM
    },
    ...
  },
  "supplementary_experiments": {
    "sitting_xyz": {
      "ORB-SLAM2": [...],
      "FM-SLAM": [...]
    },
    ...
  }
}
```

**Usage:**
```python
import json
with open('raw_data.json') as f:
    data = json.load(f)

# Get M3 results for walking_xyz
m3_results = data['ablation_studies']['walking_xyz']['M3']
median_ate = sorted(m3_results)[2]  # median of 5 runs
```

### 2. feature_retention_all_sequences.csv (253B)
Feature retention statistics for 4 sequences, 17,735 frames analyzed.

**Columns:**
- `Sequence`: Sequence name
- `M0_Erased`: Features filtered by M0 (baseline, always 0)
- `M3_Erased`: Features filtered by M3 (dynamic objects detected by FastSAM)
- `M3_Kept`: Features kept by M3 (static features)
- `Retention_Rate`: Percentage of features retained

**Key Finding:** Average 82.3% retention rate - no over-filtering issue

### 3. runtime_breakdown_summary.csv (339B)
Runtime performance breakdown for all methods.

**Columns:**
- `Method`: M0, M1, M2, M3
- `T_flow`: Optical flow time (ms)
- `T_ransac`: RANSAC time (ms)
- `T_dbscan`: DBSCAN clustering time (ms)
- `T_fastsam`: FastSAM inference time (ms, offline)
- `T_dynamic`: Total dynamic detection time (ms)
- `T_slam`: SLAM frontend time (ms)
- `T_total`: End-to-end time per frame (ms)
- `FPS`: Frames per second

**Key Finding:** Online tracking achieves 67 FPS, FastSAM runs offline at 56ms/frame on GPU

### 4. experimental_raw_logs.tar.gz (compressed)
Complete logs from all 165 SLAM runs, including:
- Frame-by-frame tracking logs
- Feature filtering statistics
- Camera trajectories
- ATE evaluation results

**Extract:**
```bash
tar -xzf experimental_raw_logs.tar.gz
```

**Structure after extraction:**
```
ablation_xyz/
├── M0/, M1/, M2/, M3/  (each with 5 runs)
ablation_rpy/
├── M0/, M1/, M2/, M3/
ablation_halfsphere/
├── M0/, M1/, M2/, M3/
ablation_static/
├── M0/, M1/, M2/, M3/
supplementary_experiments/
├── sitting_xyz/, sitting_rpy/, sitting_halfsphere/
├── bonn_crowd/, bonn_crowd2/, bonn_crowd3/
_test_sensitivity_full/
├── S1/, S2/, S3/, S4/, S5/
```

Each run directory contains:
- `runX.log`: Full SLAM log with "Erase features number" statistics
- `CameraTrajectory_runX.txt`: Estimated camera trajectory
- `ate_runX.txt`: ATE evaluation result
- `median_ate.txt`: Median ATE of 5 runs

## Experimental Setup

### Total Experiments: 165 SLAM runs

1. **Parameter Sensitivity** (25 runs)
   - 5 parameter configurations × 5 runs
   - Sequence: walking_xyz (827 frames)
   - Goal: Determine optimal RANSAC+DBSCAN parameters

2. **Ablation Studies** (80 runs)
   - 4 sequences × 4 methods × 5 runs
   - Sequences: walking_xyz, walking_rpy, walking_halfsphere, walking_static
   - Methods: M0 (Baseline), M1 (Flow+RANSAC), M2 (M1+DBSCAN), M3 (FastSAM)
   - Goal: Validate progressive improvements

3. **Supplementary Experiments** (60 runs)
   - 6 sequences × 2 methods × 5 runs
   - Sequences: 3 sitting + 3 bonn_crowd
   - Methods: ORB-SLAM2, FM-SLAM
   - Goal: Validate generalization and robustness

### Hardware Environment
- **CPU**: Intel i7-10700 @ 2.90GHz
- **GPU**: NVIDIA RTX 4060 (for FastSAM offline processing)
- **RAM**: 32GB DDR4
- **OS**: Ubuntu 20.04

## Correspondence to Paper Results

### Table 1: Ablation Study Results
**Data:** `raw_data.json` → `ablation_studies`
**Metric:** Median ATE of 5 runs

### Table 2: Supplementary Experiments
**Data:** `raw_data.json` → `supplementary_experiments`
**Metric:** Median ATE, success rate

### Table 3: Runtime Breakdown
**Data:** `runtime_breakdown_summary.csv`
**Metrics:** Per-component timing, FPS

### Table 4: Feature Retention Analysis
**Data:** `feature_retention_all_sequences.csv`
**Metric:** Retention rate percentage

### Figure 3: Runtime Comparison
**Data:** `runtime_breakdown_summary.csv` → `T_total` column

### Figure 4: Feature Retention Across Sequences
**Data:** `feature_retention_all_sequences.csv` → `Retention_Rate` column

## Data Verification

Verify data integrity:

```python
import json

# Load data
with open('raw_data.json') as f:
    data = json.load(f)

# Count runs
param_runs = sum(len(v) for v in data['parameter_sensitivity'].values())
ablation_runs = sum(len(m) for s in data['ablation_studies'].values() 
                    for m in s.values())
supp_runs = sum(len(m) for s in data['supplementary_experiments'].values() 
                for m in s.values())

print(f"Parameter sensitivity: {param_runs} runs")  # Expected: 25
print(f"Ablation studies: {ablation_runs} runs")    # Expected: 80
print(f"Supplementary: {supp_runs} runs")            # Expected: 60
print(f"Total: {param_runs + ablation_runs + supp_runs} runs")  # Expected: 165
```

## Reproducing Results

### Step 1: Prepare Dataset
Download TUM RGB-D dataset:
```bash
wget https://vision.in.tum.de/rgbd/dataset/freiburg3/rgbd_dataset_freiburg3_walking_xyz.tgz
tar -xzf rgbd_dataset_freiburg3_walking_xyz.tgz
```

### Step 2: Generate Masks with FastSAM
```bash
python scripts/generate_masks_fastsam.py \
    --model FastSAM-x.pt \
    --dataset rgbd_dataset_freiburg3_walking_xyz \
    --output masks/walking_xyz
```

### Step 3: Run SLAM
```bash
./Examples/RGB-D/rgbd_tum \
    Vocabulary/ORBvoc.txt \
    Examples/RGB-D/TUM3.yaml \
    rgbd_dataset_freiburg3_walking_xyz \
    Examples/RGB-D/associations/fr3_walking_xyz.txt \
    masks/walking_xyz
```

### Step 4: Evaluate ATE
```bash
# Install evo package
pip install evo

# Evaluate ATE
evo_ape tum groundtruth.txt CameraTrajectory.txt --align
```

Expected runtime:
- FastSAM mask generation: ~1 hour (827 frames × ~4-5s/frame on GPU)
- SLAM tracking: ~5-10 minutes (827 frames × ~0.4-0.7s/frame)
- Total per sequence: ~1-1.5 hours

## Questions?

For questions about the experimental data, please:
1. Check this README first
2. Review the paper methodology section
3. Open an issue on GitHub with specific questions

---

**Data Generated**: October 2026  
**Total Frames Processed**: ~295,000 frames  
**Total SLAM Runtime**: ~30 hours of computation  
**Segmentation Method**: FastSAM (Fast Segment Anything Model)
