"""
@author = Cyril NOVEL
@license = Unlicense
@version = 0.2
@description = Tinify all images in a folder
"""

import tinify
import argparse
import logging
import glob
import os
import time


def get_list_images(folder):
    files = glob.glob(folder + '/**/*.png', recursive=True)
    files += glob.glob(folder + '/**/*.jpg', recursive=True)
    files += glob.glob(folder + '/**/*.jpeg', recursive=True)
    return files


def get_remaining_compressions():
    return 500 - tinify.compression_count


def init_tinify(key):
    try:
        tinify.key = key
        tinify.validate()
        remaining_compressions = get_remaining_compressions()
        logging.info("Remaining compressions: " + str(remaining_compressions))
        if remaining_compressions == 0:
            logging.error("Compression quota reached for this month!")
    except tinify.Error as e:
        logging.error(e.message)
        return False
    return True


def get_size_images(list_images, power):
    size_in_byte = 0
    for img in list_images:
        size_in_byte += os.path.getsize(img)
    size = size_in_byte / pow(1024, power)
    return float(int(size*10))/10.


def get_most_recent_action_date(file):
    return max(os.path.getmtime(file), os.path.getctime(file))


def get_images_since(number_of_days, list_images):
    days_in_epoch = number_of_days*24*60*60
    cur_time = time.time()
    return [img for img in list_images if get_most_recent_action_date(img) > cur_time - days_in_epoch]


def main():
    logging.getLogger().setLevel(logging.INFO)
    log_format = "[%(levelname)s] %(message)s"
    logging.basicConfig(format=log_format)
    logging.info("Running tinify script for images in a folder")
    parser = argparse.ArgumentParser(description="Tinify all PNG and JPG in a folder")
    parser.add_argument("-f", "--folder", dest="folder", help="Folder in which to look for images", required=True)
    parser.add_argument("-k", "--key", dest="key", help="API key for Tinify", required=True)
    parser.add_argument("-d", "--days", dest="number_of_days", type=float,
                        help="Only process the images that have been modified in the last n days", default=None)
    parser.add_argument("--dry_run", help="No compression will be done", action="store_true")

    args = parser.parse_args()

    if args.dry_run:
        logging.info("This is a dry run")

    if not init_tinify(args.key):
        return 1

    list_images = get_list_images(args.folder)
    if args.number_of_days is not None:
        list_images = get_images_since(args.number_of_days, list_images)
    if len(list_images) == 0:
        logging.info("No image has to be processed")
        return 0

    img_size = get_size_images(list_images, 1)
    logging.info(str(len(list_images)) + " images to compress, total size is " + str(img_size) + " kb")

    remaining_compressions = get_remaining_compressions()
    if remaining_compressions < len(list_images):
        logging.warning("Only " + str(remaining_compressions) + " out of " + str(len(list_images)) +
                        " images will be converted, since monthly quota will be reached during the compressions")

    error_count = 0
    if not args.dry_run:
        for img in list_images:
            if get_remaining_compressions() > 0:
                logging.debug("Processing " + img)
                try:
                    source = tinify.from_file(img)
                    source.to_file(img)
                    logging.debug("Processed " + img)
                except tinify.Error as e:
                    error_count += 1
                    logging.error(img + " failed because " + e.message)

    if error_count > 0:
        logging.warning(str(error_count) + " error(s) during processing")
    else:
        logging.info("No errors during processing")

    new_size = get_size_images(list_images, 1)
    reduction = 100*(1 - new_size/img_size)
    reduction = float(int(reduction*10))/10.
    logging.info("Total size is " + str(new_size) + " kb, " + str(reduction) + "% lighter")
    logging.info("Remaining compressions: " + str(get_remaining_compressions()))

    return 0


if __name__ == '__main__':
    main()
