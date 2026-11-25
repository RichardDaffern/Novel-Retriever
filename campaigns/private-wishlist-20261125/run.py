"""Run the private wishlist batch with resumable chapter and book checkpoints."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
from urllib.parse import urlsplit
from zipfile import ZipFile, ZIP_DEFLATED

BASE = Path(__file__).resolve().parent
REPO = Path(os.environ.get('NOVEL_RETRIEVER',BASE/'retriever')).resolve()
DATA = BASE/'work'
OUT = BASE/'completed'
sys.path.insert(0,str(BASE))
sys.path.insert(0,str(REPO))
os.chdir(REPO)
os.environ["PATH"]=str(Path(sys.executable).parent)+os.pathsep+os.environ.get("PATH","")
from tools import chunked_download as chunks, freewebnovel_chunks, readnovelfull_chunks, wuxiaclick_chunks
from tools.novel_dedupe import inspect, identity_url
from tools.wuxiaclick_source import book_metadata, fetch_public_html
from public_sources import process

adapters={'readnovelfull.com':readnovelfull_chunks,'freewebnovel.com':freewebnovel_chunks,'wuxia.click':wuxiaclick_chunks}
lock=threading.Lock()
def emit(title,state,**fields):
    with lock, (BASE/'progress.jsonl').open('a',encoding='utf-8') as stream:
        stream.write(json.dumps(dict(time=time.time(),title=title,state=state,**fields),ensure_ascii=False)+'\n')

def reserve_quota(count):
    with sqlite3.connect(DATA/'quota.sqlite',timeout=30) as db:
        db.execute('CREATE TABLE IF NOT EXISTS uses (ts REAL, count INTEGER)')
        db.execute('BEGIN IMMEDIATE')
        consumed=db.execute('SELECT COALESCE(SUM(count),0) FROM uses WHERE ts>?',(time.time()-86400,)).fetchone()[0]
        if consumed+count>20:raise ValueError('Daily offline quota would be exceeded')
        db.execute('INSERT INTO uses VALUES (?,?)',(time.time(),count))

def download(row,url,folder):
    site=urlsplit(url).hostname
    if site in ('www.fanmtl.com','www.novelcool.com','www.royalroad.com'):
        return process(url,folder/'book',row['minimum'])
    if site=='wuxia.click':
        from bs4 import BeautifulSoup
        meta=book_metadata(fetch_public_html(url),url)
        if meta['numChapters']>20:raise ValueError('Whole-book download exceeds source allowance')
    adapter=adapters.get(site)
    planfile=folder/'plan.json'
    if planfile.exists():
        plan=json.loads(planfile.read_text())
    elif adapter:
        plan=adapter.plan_download(url,'',20 if site=='wuxia.click' else 100,planfile)
    else:
        plan=chunks.chapter_plan(url,chunks.discover_count(url),chunk_size=100)
        planfile.write_text(json.dumps(plan))
    if plan['total_chapters']<row['minimum']:raise ValueError('Index shorter than known edition')
    if site=='wuxia.click':reserve_quota(plan['total_chapters'])
    emit(row['title'],'chapter batches',url=url,chapters=plan['total_chapters'])
    for piece in plan['pieces']:
        start,end=piece['start'],piece['end']
        part=folder/'parts'/piece['name']
        if (part/'part.json').exists():
            chunks.validate_piece(part,url,plan['key'],start,end)
            continue
        fetch=adapter.fetch_batch if adapter else chunks.fetch_piece
        fetch(url,plan['key'],start,end,part,folder/'pending'/piece['name'],force=True)
    return chunks.assemble(plan,folder/'parts',folder/'assembly')

def handle(row):
    name=row['title']; final=OUT/(row['key']+'.zip')
    if final.exists():
        inspect(final)
        return
    for url in row['urls']:
        folder=DATA/hashlib.sha256(url.encode()).hexdigest()[:20]
        folder.mkdir(parents=True,exist_ok=True)
        try:
            emit(name,'checking source',url=url)
            book=download(row,url,folder)
            temp=final.with_suffix('.tmp')
            with ZipFile(temp,'w',ZIP_DEFLATED) as z:
                for f in book.iterdir():
                    if f.is_file() and (f.name in ('source.epub','metadata.json','chapters.json','cover.jpg','cover.png') or (f.name.startswith('chapter_') and f.suffix=='.txt')):
                        z.write(f,f.name)
            result=inspect(temp)
            if result['source_url']!=identity_url(url):raise ValueError('Archive source mismatch')
            os.replace(temp,final)
            emit(name,'completed',url=url,archive=final.name)
            return
        except Exception as err:
            emit(name,'source failed',url=url,reason=str(err)[:500])
    emit(name,'held')

if __name__=='__main__':
    DATA.mkdir(exist_ok=True);OUT.mkdir(exist_ok=True)
    from filelock import FileLock,Timeout
    with FileLock(str(BASE/'batch.lock'),timeout=0):
        rows=json.loads((BASE/'queue.json').read_text(encoding='utf-8'))
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(handle,rows))
