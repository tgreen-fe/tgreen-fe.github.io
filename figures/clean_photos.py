"""Clean up the smart-notebook phone photos.

Order matters: white balance first (so exposure decisions are made on neutral
data), then exposure, then local contrast, then denoise last so we are not
sharpening noise we just amplified.
"""
import cv2, numpy as np, os, glob
from PIL import Image, ImageOps

SRC = "../smartNotebook/Photos"
OUT = "assets/img"
TMP = "/tmp/clean"
os.makedirs(TMP, exist_ok=True)
FILES = sorted(glob.glob(f"{SRC}/*.jpeg"))


def load(i):
    im = ImageOps.exif_transpose(Image.open(FILES[i])).convert("RGB")
    return cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)


def white_balance(img, pct=97):
    """Per-channel white-patch. Scale each channel so its bright end hits ~245."""
    out = img.astype(np.float32)
    for c in range(3):
        ref = np.percentile(out[:, :, c], pct)
        if ref > 8:
            out[:, :, c] *= 245.0 / ref
    return np.clip(out, 0, 255).astype(np.uint8)


def exposure(img, black=0.4, white=99.5, gamma=1.0):
    """Stretch levels between percentiles, then optional gamma lift."""
    out = img.astype(np.float32)
    lo = np.percentile(out, black)
    hi = np.percentile(out, white)
    out = (out - lo) * (255.0 / max(hi - lo, 1))
    out = np.clip(out, 0, 255)
    if gamma != 1.0:
        out = 255.0 * np.power(out / 255.0, 1.0 / gamma)
    return np.clip(out, 0, 255).astype(np.uint8)


def local_contrast(img, clip=1.6, grid=8):
    """CLAHE on lightness only, so colour is untouched."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=clip, tileGridSize=(grid, grid)).apply(l)
    return cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)


def denoise(img, h=4):
    return cv2.fastNlMeansDenoisingColored(img, None, h, h, 7, 21)


def sharpen(img, amount=0.6, sigma=1.2):
    blur = cv2.GaussianBlur(img, (0, 0), sigma)
    return cv2.addWeighted(img, 1 + amount, blur, -amount, 0)


def find_panel(img, min_frac=0.12):
    """Largest bright, low-saturation quadrilateral: the e-paper panel."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    v = hsv[:, :, 2]
    mask = cv2.inRange(v, int(np.percentile(v, 62)), 255)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((15, 15), np.uint8))
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None
    area_min = img.shape[0] * img.shape[1] * min_frac
    best = None
    for c in sorted(cnts, key=cv2.contourArea, reverse=True)[:5]:
        if cv2.contourArea(c) < area_min:
            continue
        peri = cv2.arcLength(c, True)
        for eps in (0.02, 0.03, 0.045, 0.06):
            ap = cv2.approxPolyDP(c, eps * peri, True)
            if len(ap) == 4:
                best = ap.reshape(4, 2).astype(np.float32)
                break
        if best is not None:
            break
    return best


def order_pts(p):
    s, d = p.sum(1), np.diff(p, axis=1).ravel()
    return np.array([p[np.argmin(s)], p[np.argmin(d)],
                     p[np.argmax(s)], p[np.argmax(d)]], dtype=np.float32)


def deskew(img, quad, pad=0.02):
    q = order_pts(quad)
    (tl, tr, br, bl) = q
    w = int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
    h = int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))
    px, py = int(w * pad), int(h * pad)
    dst = np.array([[px, py], [w - px, py], [w - px, h - py], [px, h - py]],
                   dtype=np.float32)
    M = cv2.getPerspectiveTransform(q, dst)
    return cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_CUBIC,
                               borderMode=cv2.BORDER_REPLICATE)


def save(img, name, maxw, quality=84):
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    im = Image.fromarray(rgb)
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    p = f"{OUT}/{name}.webp"
    im.save(p, "WEBP", quality=quality, method=6)
    im.save(f"{TMP}/{name}.png")
    print(f"  {name:24s} {str(im.size):12s} {os.path.getsize(p)//1024:4d} KB")
    return im


# ------------------------------------------------------------------ internals
img = load(5)
img = white_balance(img, 96)
img = exposure(img, black=0.3, white=99.2, gamma=1.55)
img = local_contrast(img, clip=1.9)
img = denoise(img, 5)
img = sharpen(img, 0.5)
img = img[40:, 30:-20]                     # trim desk edge and the frame lip
save(img, "notebook-internals", 1300)

# --------------------------------------------------------------------- panel
img = load(6)
img = white_balance(img, 95)
img = exposure(img, black=0.5, white=99.3, gamma=1.7)
img = local_contrast(img, clip=1.7)
img = denoise(img, 6)
img = sharpen(img, 0.5)
save(img, "notebook-panel", 1100)

# ---------------------------------------------------------------------- build
img = load(7)
img = white_balance(img, 98)
img = exposure(img, black=0.5, white=99.6, gamma=1.12)
img = local_contrast(img, clip=1.2)
img = sharpen(img, 0.4)
save(img, "notebook-build", 1100)

# -------------------------------------------------------------------- display
# The panel runs off the right edge of the frame, so it cannot be warped to a
# full rectangle. Correct colour and exposure, rotate the content upright, and
# crop to the panel instead.
raw = load(1)
img = white_balance(raw, 96)
img = exposure(img, black=0.5, white=99.4, gamma=1.35)
img = local_contrast(img, clip=1.8, grid=10)
img = sharpen(img, 0.7, 1.0)
img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)     # text reads horizontally
h, w = img.shape[:2]
img = img[int(h * 0.07):, int(w * 0.10):]           # trim the wood at top and left
save(img, "notebook-display", 1150, quality=87)
print("done")
