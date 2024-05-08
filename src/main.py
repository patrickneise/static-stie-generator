import os
import shutil

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
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    CONTENT_DIR = os.path.join(BASE_DIR, "content")
    PUBLIC_DIR = os.path.join(BASE_DIR, "public")
    STATIC_DIR = os.path.join(BASE_DIR, "static")
    TEMPLATE_FILE = os.path.join(BASE_DIR, "template.html")

    try:
        shutil.rmtree(PUBLIC_DIR)
    except FileNotFoundError:
        pass
    finally:
        os.mkdir(PUBLIC_DIR)

    copy_files(STATIC_DIR, PUBLIC_DIR)

    generate_pages_recursive(CONTENT_DIR, TEMPLATE_FILE, PUBLIC_DIR)


main()
