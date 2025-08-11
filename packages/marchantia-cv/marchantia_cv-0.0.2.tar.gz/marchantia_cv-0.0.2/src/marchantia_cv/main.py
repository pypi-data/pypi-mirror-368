import os, sys
import subprocess
import config
from concurrent.futures import ProcessPoolExecutor, as_completed
import datetime
from tqdm.auto import tqdm
import time
import random

import measure_size_watershed

def log_failure(log_path, img_name, reason):
    fail_now = datetime.datetime.now().strftime("%y%m%d-%H%M")
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    with open(log_path, 'a') as f:
        f.write(f"{fail_now} - Image {img_name}: {reason}\n")

#Define command
def parallel_images(img_path):
    now = config.now
    outdir_root = config.outdir_root
    outdirs = config.make_outdirs(outdir_root)
    log_path = os.path.join(outdirs['size_out'], "failed_images.log")
    start = time.process_time()

    try:
        img_path, failed = measure_size_watershed.process_image(img_path, now, outdirs)
    except subprocess.CalledProcessError as e:
        log_failure(log_path, img_path, f'[ERROR]: {e}\n')
        failed = 1

    end = time.process_time()
    cpu_time = end - start

    return img_path, failed, cpu_time

if __name__ == "__main__":

    cwd = config.cwd
    now = config.now

    # Point to photos directory
    os.chdir(cwd)
    images = config.collect_images(config.photos_dir, start_fname=".")

    outdir_root = config.outdir_root
    outdirs = config.make_outdirs(outdir_root)

    failures = 0

    start = time.time()
    for n in [1, 10, 100, 200]:
        cpu_start = time.process_time()
        cpu_time = 0
        select_images = random.sample(images, n)
        with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            with tqdm(total=len(select_images),
                      file=sys.stderr,
                      ascii=True,
                      miniters=1,
                      mininterval=0,
                      dynamic_ncols=True,
                      unit = "image") as pbar:
                futures = [executor.submit(parallel_images, img) for img in select_images]
                for future in as_completed(futures):
                    img_label, failed, worker_time = future.result()
                    failures += failed
                    cpu_time += worker_time
                    pbar.set_postfix(file=img_label)
                    pbar.update(1)
                    pbar.refresh()
                    sys.stderr.flush()


        wall_total = time.time() - start
        cpu_total = cpu_time - cpu_start

        print(f"Wall-clock time: {wall_total:.2f} seconds")
        print(f"Total CPU time: {cpu_total:.2f} seconds")
        print(f"CPU efficiency: {cpu_total / wall_total:.1f}x")

        print(f"Completed with {failures} failed batches. Check error log for details.")