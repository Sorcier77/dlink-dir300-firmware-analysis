import sys

def search_sig(filename, signature, name):
    with open(filename, "rb") as f:
        data = f.read()
        offsets = []
        start = 0
        while True:
            idx = data.find(signature, start)
            if idx == -1:
                break
            offsets.append(idx)
            start = idx + 1
        print(f"Found {name} ({signature.hex()}) in {filename} at: {offsets}")

signatures = {
    "LZMA": b"\x5d\x00\x00",
    "SquashFS": b"hsqs",
    "SquashFS_BE": b"sqsh",
    "U-Boot": b"U-Boot",
    "uImage": b"\x27\x05\x19\x56",
    "uImage_swap": b"\x56\x19\x05\x27",
}

files = ["firmware_raw.bin", "firmware_swap16.bin", "firmware_swap32.bin"]

for f in files:
    print(f"--- {f} ---")
    for name, sig in signatures.items():
        search_sig(f, sig, name)
