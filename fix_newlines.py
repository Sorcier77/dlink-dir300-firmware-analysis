def fix_newlines(input_file, output_file):
    print(f"Fixing {input_file} -> {output_file}...")
    with open(input_file, 'rb') as f:
        data = f.read()
    
    # Replace CRLF with LF
    fixed_data = data.replace(b'\r\n', b'\n')
    
    print(f"Original size: {len(data)}")
    print(f"Fixed size:    {len(fixed_data)}")
    print(f"Removed {len(data) - len(fixed_data)} bytes (CRs).")
    
    with open(output_file, 'wb') as f:
        f.write(fixed_data)

fix_newlines('firmware_raw.bin', 'firmware_fixed_newlines.bin')
