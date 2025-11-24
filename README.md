# D-Link DIR-300 Firmware Recovery Report

## Problem Description
An attempt was made to extract the firmware from a D-Link DIR-300 router via UART. The extraction resulted in a file named `firmware_raw.bin`. However, initial analysis showed that the file was corrupted and could not be unpacked or analyzed correctly by standard tools like `binwalk`.

### Symptoms
*   `binwalk` failed to find valid signatures or found misaligned ones.
*   Attempts to mount or decompress potential data streams failed.
*   Visual inspection of the binary suggested entropy issues.

## Analysis & Root Cause
An analysis of the byte distribution revealed a specific pattern of corruption consistent with **Text Mode capture** over a serial connection.

*   **The Issue:** Every Line Feed byte (`0x0A`) in the original binary was automatically converted into a Carriage Return + Line Feed sequence (`0x0D 0x0A`) by the terminal emulator or serial driver during capture.
*   **Evidence:**
    *   Count of `0x0A` bytes: **15,466**
    *   Count of `0x0D 0x0A` sequences: **15,466**
    *   This exact match confirms that *every* single LF was expanded, inserting 15,466 extra `0x0D` bytes into the file, shifting all subsequent data and breaking offsets.

## The Fix
A Python script (`fix_newlines.py`) was created to reverse this transformation. It reads the raw binary and replaces every `\r\n` sequence back to `\n`.

*   **Script:** `fix_newlines.py`
*   **Input:** `firmware_raw.bin`
*   **Output:** `firmware_repaired.bin`

## Results
After repairing the newlines, the firmware structure became valid and readable by `binwalk`.

### Firmware Structure (Repaired)
| Decimal Offset | Hex Offset | Description |
| :--- | :--- | :--- |
| **327,711** | `0x5001F` | **uImage Firmware Header** (Linux Kernel)<br>- OS: Linux<br>- Image Name: "Linux Kernel Image"<br>- Data Size: 882,687 bytes |
| **1,245,247** | `0x13003F` | **SquashFS Filesystem**<br>- Version: 3.0 (Little Endian)<br>- Inode Count: 1078 |

### Extracted Artifacts
*   **`firmware_repaired.bin`**: The fully restored, bit-perfect firmware image.
*   **`kernel_fixed`**: The extracted and decompressed Linux Kernel (version 2.6.21).

## How to Reproduce
1.  Run the fix script:
    ```bash
    python3 fix_newlines.py
    ```
2.  Analyze the output:
    ```bash
    binwalk firmware_repaired.bin
    ```
3.  Extract the filesystem (using binwalk):
    ```bash
    binwalk -e firmware_repaired.bin
    ```
