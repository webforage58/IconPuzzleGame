from PIL import Image, ImageDraw, ImageFont

EMOJI = "😄"
ICON_SPECS = [
    (512, "icon-512.png"),
    (192, "icon-192.png"),
    (180, "apple-touch-icon.png"),
]

def make_base_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("NotoColorEmoji.ttf", int(size * 0.75))
    except IOError:
        font = ImageFont.load_default()
    # measure via textbbox instead of .textsize
    bbox = draw.textbbox((0, 0), EMOJI, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - w) / 2 - bbox[0]
    y = (size - h) / 2 - bbox[1]
    draw.text((x, y), EMOJI, font=font, fill="black")
    return img

def main():
    master_size, master_name = ICON_SPECS[0]
    master = make_base_icon(master_size)
    master.save(master_name)
    print(f"🖼  Saved {master_name}")
    for size, name in ICON_SPECS[1:]:
        thumb = master.resize((size, size), Image.LANCZOS)
        thumb.save(name)
        print(f"🖼  Saved {name}")

if __name__ == "__main__":
    main()
