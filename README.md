# Tinify In Folder
This Python script will tinify all the PNG and JPG images in a folder recursively.

## Installation

You need Python 3 installed, and these modules:

* os
* time
* glob
* logging
* argparse
* **tinify**

All of these should already be installed since they are fairly standard, except for tinify. To install tinify, run `pip install --upgrade tinify` in a command line.

## How to use it

The script is fairly simple.

Usage: `tinifyImg.py [-h] -f FOLDER -k KEY [-d NUMBER_OF_DAYS] [-v] [--dry_run]`    

Arguments:                        

* `-h`, `--help`: show this help message and exit       
* `-f FOLDER`, `--folder FOLDER`: Folder in which to look for images (required)
* `-k KEY`, `--key KEY`: API key for Tinify service (required)
* `-d NUMBER_OF_DAYS`, `--days NUMBER_OF_DAYS`: Only process the images that have been modified in the last `NUMBER_OF_DAYS` days (optional)
* `--dry_run`: Will run the script but won't perform any compression
* `-v`, `--verbose`: Will show complete output

The API key can be requested from the [TinyPNG website](https://tinypng.com/developers).

## Examples

Compress all the images in C:\Images that have been created or modified in the last 8 days:

`python tinifyImg.py -f C:\Images -k dummyapikey123456789abcdefghijkl -d 8`

Compress all the images in C:\Images\ToCompress:

`python tinifyImg.py -f C:\Images\ToCompress -k dummyapikey123456789abcdefghijkl`

Check how many images would be compress if we wanted to compress all the images in C:\Images\ToCompress:

`python tinifyImg.py -f C:\Images\ToCompress -k dummyapikey123456789abcdefghijkl --dry_run`

## Notes

This is the kind of command output you can expect:

```
python tinifyImg.py -f C:\Images\ToCompress -k dummyapikey123456789abcdefghijkl --dry_run
[INFO] Running tinify script for images in a folder
[INFO] This is a dry run
[INFO] Remaining compressions: 428
[INFO] 36 images to compress, total size is 794.5 kb
[INFO] No errors during processing
[INFO] Total size is 794.5 kb, 0.0% lighter
[INFO] Remaining compressions: 428
```

The script has an hardcoded limit of 500 compressions per month, which corresponds to the free plan of TinyPNG.

## License

This is free and unencumbered software released into the public domain. See LICENSE file for more information.