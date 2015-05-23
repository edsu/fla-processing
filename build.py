#!/usr/bin/env python

import os
import re
import sys
import logging
import unicodecsv

logging.basicConfig(filename="build.log", level=logging.INFO)

def main(in_csv, output_dir, input_dirs):

    if not os.path.isdir(output_dir):
        logging.info("making directory %s", output_dir)
        os.makedirs(output_dir)

    file_index = make_file_index(input_dirs)

    csv_out_file = os.path.join(output_dir, "master.csv")
    csv_out = unicodecsv.writer(open(csv_out_file, "wb"))
    with open('master.csv', 'rb') as csvfile:
        reader = unicodecsv.reader(csvfile)
        header = reader.next()

        last_article_id = None
        for row in reader:
            orig_id = row[1]
            article_id, page_id = get_article_page_ids(orig_id)

            row[1] = article_id

            if last_article_id == None:
                last_article_id = article_id

            img_path = file_index.get(page_id)

            if not img_path:
                logging.error("unable to find image for %s" % orig_id)
            else:
                move_image(img_path, output_dir, article_id)

            if article_id != last_article_id:
                csv_out.writerow(row)
                last_article_id = None
                logging.info("wrote csv row for %s" % article_id)

        csv_out.writerow(row)


def make_file_index(input_dirs):
    """
    Build an index of page_ids to file paths to images.
    """
    index = {}
    for dir in input_dirs:
        for dirpath, dirnames, filenames in os.walk(dir):
            for filename in filenames:
                article_id = get_page_id(filename)
                if article_id:
                    index[article_id] = os.path.join(dirpath, filename)
    return index


def get_page_id(s):
    s = s.lower().strip()
    s = re.sub('\.(tiff?|jpg|jpeg|djvu)$', '', s, re.IGNORECASE)
    s = s.replace('.', '-')
    parts = s.split("-")
    if len(parts) != 5:
        return None
    if parts[0] != "fla":
        return None
    return "-".join(parts)

    m = re.match(r'^(.+)\.(.+)$', s)
    if not m:
        return None

    prefix, ext = m.groups()
    if ext.lower() not in ['tif', 'tiff', 'djvu']:
        return None

    prefix = prefix.replace('.', '-')
    parts = prefix.split('-')
    if len(parts) != 5:
        return None

    # remove pages sequence
    parts.pop()

    return "-".join(parts)


def get_article_page_ids(s):
    page_id = get_page_id(s)
    parts = page_id.split('-')
    return '-'.join(parts[0:-1]), page_id


def move_image(path, output_dir, article_id):
    article_dir = os.path.join(output_dir, article_id)
    if not os.path.isdir(article_dir):
        logging.info("making article dir %s", article_dir)
        os.makedirs(article_dir)
    prefix, ext = os.path.splitext(path.lower())
    if ext == '.jpg':
        pass
    elif ext == '.tif' or ext == '.tiff':
        pass
    elif ext == '.djvu':
        pass


def slug(s):
    s = s.lower()
    s = re.sub(r'[.\'"]', '', s)
    s = re.sub(r'[-:;]', ' ', s)
    s = re.sub(' +', '-', s)
    return s


if __name__ == "__main__":
    in_csv = sys.argv[1]
    output_dir = sys.argv[2]
    input_dirs = sys.argv[3:]
    main(in_csv, output_dir, input_dirs)
