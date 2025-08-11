import os
import datetime

def collect_images(photos_dir, start_fname = "."):
    img_list = os.path.join(photos_dir, "img_list.txt")
    if not os.path.exists(img_list):
        images = []
        found = False

        for root, dirs, files in os.walk(photos_dir):
                for name in files:
                    if start_fname in name:
                        found = True
                    else:
                        found = found
                    while found:
                        if name.upper().endswith(".JPG"):
                            images.append(os.path.join(root, name))
                        break

        assert len(images) > 0, "No images found in {}".format(photos_dir)
        print("Found {} images".format(len(images)))

        with open(img_list, "w") as f:
            f.write("\n".join(images))
    else:
        with open(img_list) as f:
            images = f.read().splitlines()
    return images

def make_outdirs(outdir_root):
    outdir_names = ["crop_out", "size_out", "img_out"]
    if not os.path.exists(outdir_root):
        # Setup output directories
        outdirs = {}

        for dir_name in outdir_names:
            out = os.path.join(outdir_root, dir_name)
            outdirs[dir_name] = out
            os.makedirs(out, exist_ok=True)
            print(f"Created new output directory: {out}")
    else:
        outdirs = {}
        for dir_name in outdir_names:
            outdirs[dir_name] = os.path.join(outdir_root, dir_name)
    return outdirs


cwd = os.getcwd()
now = datetime.datetime.now().strftime("%y%m%d-%H%M")
photos_dir = os.path.join(cwd, "formatted")
outdir_root = os.path.join(cwd, "out", now)