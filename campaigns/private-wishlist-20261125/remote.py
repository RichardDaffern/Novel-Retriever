"""Run a single book privately. Only the encrypted result leaves this runner."""
import argparse
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit
from run import BASE, DATA, OUT, handle

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--matrix',action='store_true')
    parser.add_argument('--book')
    args=parser.parse_args()
    rows=json.loads((BASE/'queue.json').read_text(encoding='utf-8'))
    for row in rows:
        row['urls']=[u for u in row['urls'] if urlsplit(u).hostname!='wuxia.click']
    selected=[row for row in rows if row['urls']]
    if args.matrix:
        print(json.dumps([r['key'] for r in selected],separators=(',',':')))
        return 0
    row=next(r for r in selected if r['key']==args.book)
    DATA.mkdir(exist_ok=True);OUT.mkdir(exist_ok=True)
    handle(row)
    return 0 if (OUT/(row['key']+'.zip')).is_file() else 1

if __name__=='__main__':sys.exit(main())
