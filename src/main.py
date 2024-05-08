import os
import shutil

from config import CONTENT_DIR, PUBLIC_DIR, STATIC_DIR, TEMPLATE_FILE
from generate import generate_pages_recursive


def copy_files(src_dir, dst_dir):
    for item in os.listdir(src_dir):
        if os.path.isfile(os.path.join(src_dir, item)):
            src_file = os.path.join(src_dir, item)
            dst_file = os.path.join(dst_dir, item)
            shutil.copy(src_file, dst_file)
        else:
            new_src_dir = os.path.join(src_dir, item)
            new_dst_dir = os.path.join(dst_dir, item)
            os.mkdir(new_dst_dir)
            copy_files(new_src_dir, new_dst_dir)


def main():
    try:
        shutil.rmtree(PUBLIC_DIR)
    except FileNotFoundError:
        pass
    finally:
        os.mkdir(PUBLIC_DIR)

    copy_files(STATIC_DIR, PUBLIC_DIR)

    generate_pages_recursive(CONTENT_DIR, TEMPLATE_FILE, PUBLIC_DIR)


main()
