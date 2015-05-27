#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import shutil
import logging
import tempfile
import subprocess
import unicodecsv

from PIL import Image

"""
This script builds a directory location of canonicalized FLA data that 
is used to build the static site. It is a bootstrapping program to 
get the data into a jeklyll static site structure where it can be 
maintained from then on. It is not meant to be run repetitively.
"""

logging.basicConfig(filename="build.log", level=logging.INFO)

def main(in_csv, authors_json, output_dir, input_dirs):

    if not os.path.isdir(output_dir):
        logging.info("making directory %s", output_dir)
        os.makedirs(output_dir)

    authors = json.load(open(authors_json))

    file_index = make_file_index(input_dirs)

    with open(in_csv, 'rb') as csvfile:
        reader = unicodecsv.reader(csvfile)
        header = reader.next()

        for row in reader:
            collection = row[0]

            orig_id = row[1]
            article_id, page_id = get_article_page_ids(orig_id)

            author = row[16].split(' ; ')[0]
            author_slug = slug(author)

            if not author:
                logging.error("no author for %s", orig_id)
                continue

            author_dir = os.path.join(output_dir, collection, author_slug)
            if not os.path.isdir(author_dir):
                wikidata_id = authors.get(author)
                write_author(author, wikidata_id, author_dir)

            title = slug(row[4])
            if not title:
                logging.error("no title for %s", orig_id)
                continue

            article_dir = os.path.join(author_dir, title)
            if not os.path.isdir(article_dir):
                write_article(row, article_dir)

            img_path = file_index.get(page_id)
            if not img_path:
                logging.error("unable to find image for %s", orig_id)
                continue
            else:
                write_image(img_path, article_dir)

def write_author(author, wikidata_id, author_dir):
    logging.info("making author directory: %s", author_dir)
    os.makedirs(author_dir)
    html_file = os.path.join(author_dir, 'index.html')
    front_matter = [\
        "---",
        "layout: author",
        "name: %s"                  % author,
        "wikidata: %s"              % wikidata_id,
        "---"
    ]
    open(html_file, 'wb').write('\n'.join(front_matter).encode('utf8'))
     

def write_article(row, article_dir):
    logging.info("making article directory: %s", article_dir)
    os.makedirs(article_dir)
    html_file = os.path.join(article_dir, 'index.html')
    author = row[8].strip()
    if author == "--":
        author = ""
    creator = row[1].split("-")[2]
    subjects = row[16].split(" ; ")
    subjects = "\n".join(["    - " + s for s in subjects])
    front_matter = [\
        "---",
        "layout: article",
        "title: %s"                 % row[4],
        "author: %s"                % author,
        "publication: %s"           % row[9],
        "volume: %s"                % row[10],
        "issue: %s"                 % row[11],
        "pages: %s"                 % row[3],
        "year: %s"                  % row[13],
        "publisher: %s"             % row[14],
        "place_of_publication: %s"  % row[15],
        "subjects:",                  subjects,
        "creator: %s"               % creator,
        "---"
    ]
    open(html_file, 'wb').write('\n'.join(front_matter).encode('utf8'))


def make_file_index(input_dirs):
    """
    Build an index of page_ids to file paths to images. Give 
    preference to TIFF files, but record JPEG and DJVU files
    when now TIFF is found.
    """
    index = {}
    for dir in input_dirs:
        for dirpath, dirnames, filenames in os.walk(dir):
            for filename in filenames:
                article_id = get_page_id(filename)
                if article_id:
                    # don't overwrite our path if we have a tiff already
                    path = index.get(article_id, "")
                    if path:
                        prefix, ext = os.path.splitext(path)
                        if ext.lower() in ['tif', 'tiff']:
                            continue
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


def write_image(img_path, article_dir):
    logging.info("placing image %s in %s", img_path, article_dir)
    prefix, ext = os.path.splitext(os.path.basename(img_path).lower())

    m = re.match('.+-([0-9]+)(a|b)?$', prefix)
    if not m:
        logging.error("unknown page filename format: %s", img_path)
        return

    if m.group(2) == 'b':
        logging.error("ignoring B images")
        return

    prefix = "%02i" % int(m.group(1))

    dest = os.path.join(article_dir, prefix + '.tif')
    delete_after = False

    if ext == '.jpg' or ext == 'jpeg':
        src = jpg2tif(img_path)
        delete_after = True
    elif ext == '.tif' or ext == '.tiff':
        src = img_path
    elif ext == '.djvu':
        src = djvu2tiff(img_path)
        if src is None:
            logging.info("unable to convert %s to tiff", img_path)
            return None
        delete_after = True

    logging.info("copying %s to %s", src, dest)
    shutil.copyfile(src, dest)

    if delete_after:
        logging.info("deleting temp file %s", src)
        os.remove(src)


def article_path(bag_dir, collection, author, title):
    return os.path.join(bag_dir, slug(collection), slug(author), slug(title))


def jpg2tif(jpg_file):
    logging.info("converting %s to tif", jpg_file)
    i = Image.open(jpg_file)
    fh, tif_file = tempfile.mkstemp()
    i.save(tif_file, format='tiff')
    return tif_file


def djvu2tif(djvu_file):
    logging.info("converting %s to tif", img_path)
    fh, tif_file = tempfile.mkstemp()
    rc = subprocess.call(["ddjvu", '-format=tiff', djvu_file, tif_file])
    if rc == 0:
        return tif_file
    return None


def slug(s):
    s = s.lower()
    s = re.sub(r'[,;?.\'"]', '', s)
    s = re.sub(r'[-:;]', ' ', s)
    s = re.sub(' +', '-', s)
    return s


if __name__ == "__main__":
    in_csv = sys.argv[1]
    authors_json = sys.argv[2]
    output_dir = sys.argv[3]
    input_dirs = sys.argv[4:]
    main(in_csv, authors_json, output_dir, input_dirs)
