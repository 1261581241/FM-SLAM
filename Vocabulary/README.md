# ORB Vocabulary

The ORB vocabulary file (`ORBvoc.txt`) is required for ORB-SLAM2 to work.

## Extract Before Use

```bash
tar -xzf ORBvoc.txt.tar.gz
```

This will extract `ORBvoc.txt` (139MB) in this directory.

## Why Compressed?

The vocabulary file is large (139MB) and compresses well. We provide it compressed to:
- Reduce repository size
- Speed up git clone
- Stay within GitHub file size recommendations

## Alternative Download

If you already have ORB-SLAM2 installed, you can copy the vocabulary from there:
```bash
cp /path/to/ORB_SLAM2/Vocabulary/ORBvoc.txt ./
```

Or download from ORB-SLAM2 repository:
https://github.com/raulmur/ORB_SLAM2/tree/master/Vocabulary
