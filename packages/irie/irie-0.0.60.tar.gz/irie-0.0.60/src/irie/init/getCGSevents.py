#!/usr/bin/env python
import sys
import cesmd.search

# scrape.py <cesmd> <out-dir>
outdir = sys.argv[1]

cesmd.search.get_records(outdir, 
                         "cchern@berkeley.edu",
                         station_code=sys.argv[1], 
                         #unpack=True,
                         network="CE",
                         include_inactive=True,
                         process_level="processed",
)

