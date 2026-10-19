import base64
from io import BytesIO
from PIL import Image

def main():
    img = Image.open(r"D:\Velox\branding\assets\velox_logo_512.png").convert("RGBA")
    thumb = img.resize((48, 48), Image.Resampling.LANCZOS)
    buf = BytesIO()
    thumb.save(buf, format="PNG", optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    icons_path = r"D:\Velox\src\ui\webui\resources\cr_elements\icons.html.ts"
    with open(icons_path, "r", encoding="utf-8") as f:
        content = f.read()

    target = """      <g id="chrome-product" viewBox="0 -960 960 960">
        <path d="M336-479q0 60 42 102t102 42q60 0 102-42t42-102q0-60-42-102t-102-42q-60 0-102 42t-42 102Zm144 216q11 0 22.5-.5T525-267L427-99q-144-16-237.5-125T96-479q0-43 9.5-84.5T134-645l160 274q28 51 78 79.5T480-263Zm0-432q-71 0-126.5 42T276-545l-98-170q53-71 132.5-109.5T480-863q95 0 179 45t138 123H480Zm356 72q15 35 21.5 71t6.5 73q0 155-100 260.5T509-96l157-275q14-25 22-52t8-56q0-40-15-77t-41-67h196Z">
        </path>
      </g>"""

    replacement = f"""      <g id="chrome-product" viewBox="0 0 24 24">
        <image width="24" height="24" href="data:image/png;base64,{b64}"></image>
      </g>"""

    if target in content:
        new_content = content.replace(target, replacement)
        with open(icons_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully updated icons.html.ts with VELOX logo!")
    else:
        print("Target string not found in icons.html.ts!")

if __name__ == "__main__":
    main()
