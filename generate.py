from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
from typing import NamedTuple
import svg

with open("config.json", encoding="utf8") as f:
    CFG = json.load(f)

STYLE = """
text {
    font-family: Oswald;
}
"""

STYLE_ELEMENT = svg.Defs(
    elements=[
        svg.Style(type="text/css", text=STYLE),
    ],
)

background = lambda color: svg.Rect(x=0, y=0, width=500, height=500, fill=color)

primary = lambda text, y, size: svg.Text(
    fill="#fff",
    x=250,
    y=y,
    font_size=size,
    font_weight="bold",
    dominant_baseline="central",
    text_anchor="middle",
    text=text,
)

secondary = lambda text : svg.Text(
    fill="#fff",
    opacity=0.7,
    x=25,
    y=100,
    font_size=125,
    dominant_baseline="central",
    text=text,
)

primary_size = lambda text : CFG["TEXT_SIZES"][text] if text in CFG["TEXT_SIZES"] else 250

def create_icon(primary_text: str, seconday_text: str, color: str) -> svg.SVG:
    elements: list[svg.Element] = [STYLE_ELEMENT, background(color)]
    primary_y = 250

    if seconday_text != "":
        primary_y = 300
        elements.append(secondary(seconday_text))

    elements.append(primary(primary_text, primary_y, primary_size(primary_text)))

    return svg.SVG(
        viewBox=svg.ViewBoxSpec(0, 0, 500, 500),
        elements=elements,
    )

def raster(folder: Path, filename: str):
    subprocess.run([
                "resvg",
                "--width", "500",
                "--height", "500",
                folder.joinpath(filename + ".svg"),
                folder.joinpath(filename + ".png"),
            ], capture_output=True)

class Entry(NamedTuple):
    category: str
    subcategory: str
    data: list[str]

def process(entry: Entry):
    data = entry.data

    if len(entry.data) < 2:
        return

    for color_name, color in CFG["COLORS"].items():
        name = data[0]
        folder = Path("icons").joinpath(entry.category).joinpath(entry.subcategory).joinpath(color_name)
        os.makedirs(folder, exist_ok=True)
        secondary_text = data[2] if len(data) == 3 else ""
        svg_data = str(create_icon(data[1], secondary_text, "#" + color))
        filename = folder.joinpath(name + ".svg")
        with open(filename, "w", encoding="utf8", newline="\n") as f:
            f.write(svg_data)
        raster(folder, name)
        os.remove(filename)
        print(f"{name}: {color_name}")

def main():
    entries: list[Entry] = []

    for category, subcategories in CFG["ICONS"].items():
        for subcategory, entry_list in subcategories.items():
            for entry_data in entry_list:
                entries.append(Entry(category, subcategory, entry_data))
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process, entries)
                    

if __name__ == "__main__":
    main()