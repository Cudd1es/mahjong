import os
from PIL import Image

ASSETS_DIR = "web/public"
TARGETS = [
    "compass_dial.png",
    "score_plate.png",
    "btn_ron.png",
    "btn_pon.png",
    "btn_kan.png",
    "btn_chi.png",
    "btn_tsumo.png",
    "btn_skip.png"
]

def remove_black_bg(filename):
    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(path):
        print(f"Skipping {filename}, not found.")
        return

    print(f"Processing {filename}...")
    img = Image.open(path).convert("RGBA")
    datas = img.getdata()
    
    # Threshold for black/dark background
    threshold = 80
    new_data = []
    
    for item in datas:
        # item is (r, g, b, a)
        # Check if pixel is dark (black or dark gray mosaic)
        # Mosaic usually alternates between black and dark gray (e.g., 30-50)
        r, g, b = item[0], item[1], item[2]
        
        # Condition 1: Simplistic dark threshold
        is_dark = r < threshold and g < threshold and b < threshold
        
        # Condition 2: Neutral gray check (often checkerboards are neutral)
        # If R, G, B are close to each other (diff < 10) and relatively dark
        is_gray = abs(r-g) < 10 and abs(g-b) < 10 and r < threshold
        
        if is_dark or is_gray:
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    img.save(path, "PNG")
    print(f"Saved {filename}")

if __name__ == "__main__":
    for t in TARGETS:
        remove_black_bg(t)
