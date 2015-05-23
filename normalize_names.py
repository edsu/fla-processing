#!/usr/bin/env python

import os
import re
import sys
import json
import unicodecsv

from wikidata_suggest import suggest

in_csv = unicodecsv.reader(open(sys.argv[1], 'rb'))
out_fh = open(sys.argv[2], "wb")
out_csv = unicodecsv.writer(out_fh)
authors_file = sys.argv[3]

seen_header = False

if os.path.isfile(authors_file):
    authors = json.load(open(authors_file))
else:
    authors = {}

for row in in_csv:

    # copy over the headers
    if not seen_header:
        out_csv.writerow(row)
        seen_header = True
        continue

    # can be multiple names separated by semicolons
    names = [n.strip() for n in row[16].split(";")]

    # no names, no work to do :)
    if len(names) == 1 and names[0] == "":
        continue

    # use wikidata to normalize the names
    new_names = []
    for name in names:

        if name in authors:
            new_names.append(name)
            continue

        parts = [n.strip() for n in name.split(',', 1)]
        if len(parts) == 2:
            name = ' '.join([parts[1], parts[0]])

        wikidata = suggest(name)

        if wikidata:
            new_names.append(wikidata['label'])
            authors[wikidata['label']] = wikidata['id']
        else:
            new_names.append(name)
            authors[name] = None
        
        json.dump(authors, open(authors_file, 'w'), indent=2)

    # write out the normalized names
    row[16] = " ; ".join(new_names)
    out_csv.writerow(row)
    out_fh.flush()
    

