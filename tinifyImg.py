"""
@author = Cyril NOVEL
@license = Unlicense
@version = 0.3
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


class Tinifier:
    class Error(Exception):
        pass

    def __init__(self, key):
        self._init = False
        try:
            tinify.key = key
            tinify.validate()
        except tinify.Error as e:
            logging.error(e.message)
            raise Tinifier.Error("Failed to validate key with Tinify")
        self._init = True

    def remaining_free_compressions(self):
        if not self.is_initialized():
            raise Tinifier.Error("Tinifier is not initialized")
        return max(0, 500 - tinify.compression_count)

    def can_perform_free_compressions(self):
        return self.remaining_free_compressions() > 0

    def is_initialized(self):
        return self._init

    def compress_image(self, image):
        if not self.is_initialized():
            raise Tinifier.Error("Tinifier is not initialized")
        try:
            source = tinify.from_file(image)
            source.to_file(image)
        except tinify.Error as e:
            logging.error(image + " failed because " + e.message)
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
    return [img for img in list_images
            if get_most_recent_action_date(img) > cur_time - days_in_epoch]


def main():
    logging.getLogger().setLevel(logging.INFO)
    log_format = "[%(levelname)s] %(message)s"
    logging.basicConfig(format=log_format)
    logging.info("Running tinify script for images in a folder")
    parser = argparse.ArgumentParser(description="Tinify all PNG and JPG in a folder")
    parser.add_argument("-f", "--folder", dest="folder", help="Folder in which to look for images",
                        required=True)
    parser.add_argument("-k", "--key", dest="key", help="API key for Tinify", required=True)
    parser.add_argument("-d", "--days", dest="number_of_days", type=float,
                        help="Only process the images that have been modified in the last n days",
                        default=None)
    parser.add_argument("--dry_run", help="No compression will be done", action="store_true")
    parser.add_argument("-v", "--verbose", help="Complete output", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.dry_run:
        logging.info("This is a dry run")

    try:
        tinifier = Tinifier(args.key)
    except Tinifier.Error as e:
        logging.error(e)
        return 1

    list_images = get_list_images(args.folder)
    if args.number_of_days is not None:
        list_images = get_images_since(args.number_of_days, list_images)
    if len(list_images) == 0:
        logging.info("No image has to be processed")
        return 0

    img_size = get_size_images(list_images, 1)
    logging.info(str(len(list_images)) + " images to compress, total size is " + str(img_size) +
                 " kb")

    remaining_compressions = tinifier.remaining_free_compressions()
    if remaining_compressions < len(list_images):
        logging.warning("Only " + str(remaining_compressions) + " out of " + str(len(list_images)) +
                        " images will be converted, since monthly quota will be reached during the "
                        "compressions")

    error_count = 0
    uncompressed_count = 0
    for img in list_images:
        if not tinifier.can_perform_free_compressions():
            uncompressed_count += 1
            logging.warning("No more free compressions, can't compress " + img)
            continue
        logging.debug("Processing " + img)
        if not args.dry_run and not tinifier.compress_image(img):
            error_count += 1
        else:
            logging.debug(img + " processed")

    if error_count > 0:
        logging.warning(str(error_count) + " error(s) during processing")
    elif uncompressed_count > 0:
        logging.warning(str(uncompressed_count) + " images skipped because there are no remaining "
                                                  "compressions left")
    else:
        logging.info("No errors during processing")

    new_size = get_size_images(list_images, 1)
    reduction = 100*(1 - new_size/img_size)
    reduction = float(int(reduction*10))/10.
    logging.info("Total size is " + str(new_size) + " kb, " + str(reduction) + "% lighter")
    logging.info("Remaining compressions: " + str(tinifier.remaining_free_compressions()))

    return 0


if __name__ == '__main__':
    main()
