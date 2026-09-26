# drone_art.py
# Core rendering logic for the drone-art pixel/circle grid.

from PIL import Image, ImageDraw
import config as CFG
import csv  # add near the top with the other imports

def read_video_frames(path):
    """
    Read a video (mp4/mov/etc.), center-crop each kept frame to square
    (goal 3), and return a list of square RGB PIL images.
    """
    try:
        import imageio.v3 as iio
    except ImportError:
        raise RuntimeError(
            "Video support needs imageio. Install with:\n"
            "    pip install imageio imageio-ffmpeg av"
        )

    # Decode only — keep this try narrow so real bugs aren't hidden.
    try:
        arrays = list(iio.imiter(path))
    except Exception as e:
        raise RuntimeError(
            f"could not decode '{path}' ({e}). "
            f"Try:  pip install av   (or)   pip install imageio-ffmpeg"
        )

    if not arrays:
        raise RuntimeError(f"no frames decoded from '{path}'.")

    raw = [make_square(Image.fromarray(arr), source_label=path) for arr in arrays]

    idx = _pick_indices(len(raw), CFG.MAX_FRAMES, CFG.VIDEO_SAMPLING)
    return [raw[i] for i in idx]

def hex_to_rgb(value):
    """'#0a101c' -> (10, 16, 28)."""
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _resample_filter():
    return Image.LANCZOS if CFG.RESAMPLE.upper() == "LANCZOS" else Image.NEAREST


def center_crop_square(img):
    """
    Goal 3: shave the 'extra' off the outer edges so the result is square.
    Crops equally from both long sides, keeping the center.
    """
    w, h = img.size
    if w == h:
        return img
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def make_square(img, source_label=""):
    """Return a square RGB image, cropping if allowed, else raise."""
    img = img.convert("RGB")
    w, h = img.size
    if w == h:
        return img
    if CFG.AUTO_CENTER_CROP:
        return center_crop_square(img)
    raise ValueError(
        f"{source_label or 'image'} is {w}x{h}, not square. "
        f"Set AUTO_CENTER_CROP=True in config.py or crop it first."
    )


def load_square_image(path):
    """Load a PNG/JPG and return a guaranteed-square RGB image."""
    return make_square(Image.open(path), source_label=path)


def to_grid(img):
    """Downsample any square image to a GRID x GRID pixel image."""
    return img.resize((CFG.GRID, CFG.GRID), _resample_filter())


def render_drone_frame(grid_img):
    """
    Turn a GRID x GRID image into the circle-dot 'drone art' rendering.
    Each source pixel becomes one filled circle with a gap around it.
    """
    grid = CFG.GRID
    cell = CFG.CELL_SIZE
    canvas_px = grid * cell

    bg = hex_to_rgb(CFG.BACKGROUND_HEX)
    canvas = Image.new("RGB", (canvas_px, canvas_px), bg)
    draw = ImageDraw.Draw(canvas)

    dot = cell * CFG.DOT_RATIO
    margin = (cell - dot) / 2.0

    px = grid_img.load()
    for y in range(grid):
        for x in range(grid):
            r, g, b = px[x, y]
            x0 = x * cell + margin
            y0 = y * cell + margin
            draw.ellipse([x0, y0, x0 + dot, y0 + dot], fill=(r, g, b))

    return canvas
def _pick_indices(total, max_frames, mode):
    """Choose which source-frame indices to keep."""
    if total <= max_frames:
        return list(range(total))
    if mode == "first":
        return list(range(max_frames))
    # "even": evenly spaced across the whole clip
    step = total / float(max_frames)
    return [int(i * step) for i in range(max_frames)]


def read_video_frames(path):
    """
    Read an MP4 (or other supported video), center-crop each kept frame to
    square (goal 3), and return a list of square RGB PIL images.
    Sampling respects MAX_FRAMES and VIDEO_SAMPLING from config.
    """
    import imageio.v3 as iio

    # Grab total frame count. We read lazily so we don't hold the whole clip.
    frames = []
    props = iio.improps(path, plugin="pyav")
    total = props.shape[0] if props.shape is not None else None

    if total:
        keep = set(_pick_indices(total, CFG.MAX_FRAMES, CFG.VIDEO_SAMPLING))
        for idx, arr in enumerate(iio.imiter(path, plugin="pyav")):
            if idx in keep:
                img = Image.fromarray(arr)
                frames.append(make_square(img, source_label=f"{path}#frame{idx}"))
            if len(frames) >= CFG.MAX_FRAMES:
                break
    else:
        # Fallback if frame count is unknown: just take the first MAX_FRAMES.
        for idx, arr in enumerate(iio.imiter(path, plugin="pyav")):
            if idx >= CFG.MAX_FRAMES:
                break
            img = Image.fromarray(arr)
            frames.append(make_square(img, source_label=f"{path}#frame{idx}"))

    return frames


def build_gif(frames, out_path):
    """Save a list of RGB frames as a looping GIF."""
    if not frames:
        return
    first, rest = frames[0], frames[1:]
    first.save(
        out_path,
        save_all=True,
        append_images=rest,
        duration=CFG.FRAME_DURATION_MS,
        loop=CFG.GIF_LOOP,
        optimize=False,
        disposal=2,
    )



def rgb_to_hex(rgb):
    """(240, 138, 36) -> '#f08a24'"""
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])


def ofdm_resource(x, y):
    """
    Map a 1-based UAV coordinate to (symbol, subcarrier_k), matching the
    example's 1000 subcarriers x 10 symbols per frame scheme.
    """
    idx = (y - 1) * CFG.GRID + (x - 1)
    symbol = idx // 1000 + 1
    k = idx % 1000 + 1
    return symbol, k


def frame_rows(step, grid_img):
    """Yield one CSV row per cell for a GRID x GRID frame."""
    px = grid_img.load()
    for y in range(1, CFG.GRID + 1):
        for x in range(1, CFG.GRID + 1):
            hexcode = rgb_to_hex(px[x - 1, y - 1])
            if CFG.INCLUDE_OFDM_COLUMNS:
                s, k = ofdm_resource(x, y)
                yield [step, x, y, s, k, hexcode]
            else:
                yield [step, x, y, hexcode]


def csv_header():
    if CFG.INCLUDE_OFDM_COLUMNS:
        return ["show_frame", "X", "Y", "ofdm_symbol", "subcarrier_k", "colour_hex"]
    return ["show_frame", "X", "Y", "colour_hex"]