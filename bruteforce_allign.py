import os
import struct

def strings(filename, min=4):
    with open(filename, errors="ignore") as f:  
        result = ""
        for c in f.read():
            if c.isprintable():
                result += c
                continue
            if len(result) >= min:
                yield result
            result = ""
        if len(result) >= min:  
            yield result

def brute_force(input_file):
    print(f"--- BRUTE FORCE ALIGNMENT: {input_file} ---")
    with open(input_file, 'rb') as f:
        original_data = f.read()

    # On teste les décalages de 0 à 3 octets
    for shift in range(4):
        # On coupe le début
        data = original_data[shift:]
        
        # Padding pour que la longueur soit multiple de 4
        while len(data) % 4 != 0:
            data += b'\x00'
            
        variants = {}
        
        # 1. Variante Normale (Little Endian / No Swap)
        variants[f"shift{shift}_normal"] = data
        
        # 2. Variante Swap 16 (Byte Swap)
        swap16 = bytearray(len(data))
        for i in range(0, len(data), 2):
            swap16[i] = data[i+1]
            swap16[i+1] = data[i]
        variants[f"shift{shift}_swap16"] = swap16
        
        # 3. Variante Swap 32 (Word Swap)
        swap32 = bytearray(len(data))
        for i in range(0, len(data), 4):
            swap32[i] = data[i+3]
            swap32[i+1] = data[i+2]
            swap32[i+2] = data[i+1]
            swap32[i+3] = data[i]
        variants[f"shift{shift}_swap32"] = swap32
        
        # Analyse des variantes
        for name, content in variants.items():
            # On cherche des signatures texte fortes
            text_content = content[:20000] # On scanne juste les 20 premiers Ko (Bootloader)
            try:
                text_decoded = text_content.decode('ascii', errors='ignore')
            except:
                continue
                
            score = 0
            keywords = ["U-Boot", "Linux", "SquashFS", "Ralink", "D-Link", "mips", "bootcmd", "jaguar"]
            found_words = []
            
            for k in keywords:
                if k in text_decoded:
                    score += 1
                    found_words.append(k)
            
            if score > 0:
                print(f"[SUCCESS] Found signatures in {name}.bin !")
                print(f"   -> Keywords: {found_words}")
                # Sauvegarder le gagnant
                with open(f"{name}.bin", "wb") as out:
                    out.write(content)
                print(f"   -> Saved as {name}.bin")

brute_force('firmware_raw.bin')
