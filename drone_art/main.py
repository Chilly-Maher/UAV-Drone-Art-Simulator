# main.py
# Run: python main.py

import os
import glob
import csv
import config as CFG
import drone_art as da


def find_inputs():
    files = []
    all_exts = CFG.IMAGE_EXTENSIONS + CFG.VIDEO_EXTENSIONS
    for f in sorted(glob.glob(os.path.join(CFG.INPUT_DIR, "*"))):
        if f.lower().endswith(all_exts):
            files.append(f)
    return files


def is_video(path):
    return path.lower().endswith(CFG.VIDEO_EXTENSIONS)


def render_and_save(square_img, name):
    """Downsample -> drone render -> save PNG. Returns (frame, grid_img)."""
    grid_img = da.to_grid(square_img)
    frame = da.render_drone_frame(grid_img)
    out_png = os.path.join(CFG.OUTPUT_DIR, f"{name}_drone.png")
    frame.save(out_png)
    print(f"  wrote {out_png}")
    return frame, grid_img


def main():
    os.makedirs(CFG.OUTPUT_DIR, exist_ok=True)

    inputs = find_inputs()
    if not inputs:
        exts = CFG.IMAGE_EXTENSIONS + CFG.VIDEO_EXTENSIONS
        print(f"No {exts} files found in '{CFG.INPUT_DIR}/'.")
        return

    frames = []

    # Open the CSV once (if enabled) and write the header.
    csv_fh = None
    csv_writer = None
    if CFG.WRITE_CSV:
        csv_path = os.path.join(CFG.OUTPUT_DIR, CFG.CSV_NAME)
        csv_fh = open(csv_path, "w", newline="")
        csv_writer = csv.writer(csv_fh)
        csv_writer.writerow(da.csv_header())

    step = 0  # global frame counter across all inputs

    def handle_frame(square_img, name):
        nonlocal step
        frame, grid_img = render_and_save(square_img, name)
        frames.append(frame)
        if csv_writer is not None and step % CFG.CSV_EVERY == 0:
            for row in da.frame_rows(step, grid_img):
                csv_writer.writerow(row)
        step += 1

    for path in inputs:
        if len(frames) >= CFG.MAX_FRAMES:
            print(f"Reached MAX_FRAMES ({CFG.MAX_FRAMES}); stopping.")
            break

        base = os.path.splitext(os.path.basename(path))[0]

        if is_video(path):
            print(f"video: {path}")
            try:
                video_frames = da.read_video_frames(path)
            except Exception as e:
                print(f"  skipped video: {e}")
                continue
            for i, sq in enumerate(video_frames):
                if len(frames) >= CFG.MAX_FRAMES:
                    break
                handle_frame(sq, f"{base}_f{i:04d}")
        else:
            print(f"image: {path}")
            try:
                square = da.load_square_image(path)
            except ValueError as e:
                print(f"  skipped: {e}")
                continue
            handle_frame(square, base)

    if csv_fh is not None:
        csv_fh.close()
        print(f"  wrote {os.path.join(CFG.OUTPUT_DIR, CFG.CSV_NAME)}")

    if not frames:
        print("No valid frames were rendered; nothing to animate.")
        return

    if len(frames) > 1:
        gif_path = os.path.join(CFG.OUTPUT_DIR, CFG.GIF_NAME)
        da.build_gif(frames, gif_path)
        print(f"  wrote {gif_path}  ({len(frames)} frames @ {CFG.FRAME_DURATION_MS} ms)")
    else:
        print("  only one frame -> skipped GIF (need 2+ frames).")


if __name__ == "__main__":
    main()