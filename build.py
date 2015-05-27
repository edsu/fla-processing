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
is used to build the static site. It is a throw away bootstrapping program 
to get the data into an initial jeklyll static site structure where it can 
be maintained from then on. It is not meant to be run repetitively as part
of a curation workflow.
"""

logging.basicConfig(filename="build.log", level=logging.INFO)


def main(in_csv, authors_json, output_dir, input_dirs):

    if not os.path.isdir(output_dir):
        logging.info("making directory %s", output_dir)
        os.makedirs(output_dir)

    # this contains a simple mapping of authors names to wikidata ids
    authors = json.load(open(authors_json))

    # keep track of clippings seen
    clipping_index = {}

    # keep track of page images
    page_index = make_page_index(input_dirs)

    with open(in_csv, 'rb') as csvfile:
        reader = unicodecsv.reader(csvfile)
        header = reader.next()
        for row in reader:
            logging.info("processing %s", row[1])
            for a in row[16].split(' ; '):
                write_author(output_dir, a, authors.get(a))

            clipping_dir = get_clipping_dir(output_dir, row, clipping_index)
            if not clipping_dir:
                logging.error("couldn't determine clipping directory for %s", row[1])
                continue
            
            img_path = page_index.get(get_page_id(row[1]))
            if not img_path:
                logging.error("couldn't find image for %s", row[1])
                continue
            write_image(img_path, clipping_dir)


def write_author(output_dir, author, wikidata_id):
    author_dir = os.path.join(output_dir, '_authors', slug(author))
    if os.path.isdir(author_dir):
        return
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
     

def write_clipping_info(row, clipping_dir):
    os.makedirs(clipping_dir)
    html_file = os.path.join(clipping_dir, 'index.html')
    author = row[8].strip()
    if author == "--":
        author = ""
    creator = row[1].split("-")[2]
    subjects = row[16].split(" ; ")
    subjects = "\n".join(["    - " + s for s in subjects])
    front_matter = [\
        "---",
        "layout: clipping",
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
        "collection: %s"            % row[0],
        "creator: %s"               % creator,
        "---"
    ]
    open(html_file, 'wb').write('\n'.join(front_matter).encode('utf8'))
    return clipping_dir


def get_clipping_dir(output_dir, row, clipping_index):
    """
    A complicated function that returns the next numeric clipping directory
    to use. The clipping directories are a simple numbered sequence. If the
    clipping directory already exists for the supplied row in the clipping
    index it is returned immediately.
    """
    clipping_id = get_clipping_id(row[1])
    if clipping_id in clipping_index:
        return clipping_index[clipping_id]

    clippings_dir = os.path.join(output_dir, "_clippings")
    if not os.path.isdir(clippings_dir):
        os.makedirs(clippings_dir)

    # deterrmine the next in the sequence
    r = re.compile('^[0-9]+$')
    existing = map(int, filter(r.match, os.listdir(clippings_dir)))
    existing.sort()
    if len(existing) == 0:
        num = 1
    else:
        num = int(existing[-1]) + 1

    clipping_dir = os.path.join(output_dir, "_clippings", "%05i" % num)
    logging.info("making clipping directory %s", clipping_dir)
    write_clipping_info(row, clipping_dir)
    clipping_index[clipping_id] = clipping_dir

    return clipping_dir


def make_page_index(input_dirs):
    """
    Build an index of page_ids to file paths to images. Give 
    preference to TIFF files, but record JPEG and DJVU files
    when now TIFF is found.
    """
    index = {}
    for dir in input_dirs:
        for dirpath, dirnames, filenames in os.walk(dir):
            for filename in filenames:
                clipping_id = get_page_id(filename)
                if clipping_id:
                    # don't overwrite our path if we have a tiff already
                    path = index.get(clipping_id, "")
                    if path:
                        prefix, ext = os.path.splitext(path)
                        if ext.lower() in ['tif', 'tiff']:
                            continue
                    index[clipping_id] = os.path.join(dirpath, filename)
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
    

def get_clipping_id(s):
    parts = get_page_id(s).split('-')
    parts.pop()
    return '-'.join(parts)


def write_image(img_path, clipping_dir):
    logging.info("placing image %s in %s", img_path, clipping_dir)

    prefix, ext = os.path.splitext(os.path.basename(img_path).lower())
    m = re.match('.+-([0-9]+)(a|b)?$', prefix)
    if not m:
        logging.error("unknown page filename format: %s", img_path)
        return

    if m.group(2) == 'b':
        logging.error("ignoring B images")
        return
    prefix = "%03i" % int(m.group(1))
    dest = os.path.join(clipping_dir, prefix + '.tif')

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

    return dest


def jpg2tif(jpg_file):
    logging.info("converting %s to tif", jpg_file)
    i = Image.open(jpg_file)
    fd, tif_file = tempfile.mkstemp()
    i.save(tif_file, format='tiff')
    os.close(fd)
    return tif_file


def djvu2tif(djvu_file):
    logging.info("converting %s to tif", img_path)
    fd, tif_file = tempfile.mkstemp()
    rc = subprocess.call(["ddjvu", '-format=tiff', djvu_file, tif_file])
    if rc != 0:
        return None
    os.close(fd)
    return tif_file


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
