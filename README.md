This directory contains scripts for normalizing and massaging the 
orginal FLA spreadsheets and scan data that were given to MITH using
Box in April 2015. The original spreadsheets were created by multiple
people and needed to be normalized before further processing can be done.

The original spreadsheets from Box are included in the spreadsheets
directory. You will want to mount those Box directories like this, 
or you will need to adjust the Makefile:

    /data/box-group-foreign-literatures-in-america
    /data/Conrad Collection

To get the various dependencies run:

    make install

The name normalization can take a while, so the master.csv and authors.json
output has been commited to git. Unless you want to rebuild them you can
create the static site with:

    make build

If you want to run the entire workflow run:

    make

When the build is complete you should see a directory structure like:

    /data/fla/{collection}/index.html
    /data/fla/{collection}/{author}/index.html
    /data/fla/{collection}/{author}/image.jpg
    /data/fla/{collection}/{author}/{title}/index.html
    /data/fla/{collection}/{author}/{title}/01.tif
