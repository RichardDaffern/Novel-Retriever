"""Private downloads from ordinary book indexes and public chapter pages."""
import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from tools.chunked_download import _epub

def page(url):
    with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as response:
        if urlsplit(response.url).hostname != urlsplit(url).hostname:
            raise ValueError("Cross-site redirect")
        body = response.read(8_000_001)
    if len(body) > 8_000_000:
        raise ValueError("Page exceeds expected size")
    return BeautifulSoup(body, "html5lib")

def catalogue(url):
    doc = page(url)
    host = urlsplit(url).hostname
    fan = host == 'www.fanmtl.com'
    title = doc.select_one('h1')
    author = doc.select_one('.author a' if fan else '.bookinfo-author a')
    rows = {}
    def add(n, link):
        address = urljoin(url, link)
        if urlsplit(address).hostname != host or (n in rows and rows[n] != address):
            raise ValueError("Conflicting chapter links")
        rows[n] = address
    if host == 'www.royalroad.com':
        author = doc.select_one('a[href*="/profile/"][property="name"], .fic-title a[href*="/profile/"]')
        anchors=doc.select('table#chapters td a[href*="/chapter/"]')
        for a in anchors:
            address=urljoin(url,a['href'])
            if '/fiction/5701/' not in address:raise ValueError('Unexpected Royal Road identity')
            if address not in rows.values():add(len(rows)+1,address)
    elif fan:
        advertised=re.search(r'([0-9,]+)\s+Chapters',doc.get_text(' ',strip=True),re.I)
        slug = Path(urlsplit(url).path).stem
        tab = next(a for a in doc.select('a[href]') if 'tab=chapters' in a['href'])
        current = urljoin(url, tab['href'])
        visited = set()
        while current:
            if current in visited or len(visited) >= 550:
                raise ValueError("Repeating or oversized catalogue")
            visited.add(current)
            doc = page(current)
            for a in doc.select('.chapter-list a[href], li a[href]'):
                m = re.fullmatch(r'/novel/'+re.escape(slug)+r'_(\d+)\.html',urlsplit(urljoin(url,a['href'])).path)
                if m: add(int(m[1]),a['href'])
            nxt = next((a['href'] for a in doc.select('a[href]') if a.get_text(strip=True) == '>' and 'wjm='+slug in a['href']),None)
            current = urljoin(url,nxt) if nxt else None
            if current and urlsplit(current).hostname != host: raise ValueError('Unexpected pagination host')
            if current: time.sleep(1)
        if not advertised or len(rows)!=int(advertised[1].replace(',','')):raise ValueError('Catalogue differs from published chapter count')
    else:
        anchors=doc.select('.chapter-item-list a[href]')
        for a in anchors:
            label = a.get('title') or a.get_text(' ',strip=True)
            if len(anchors)==1 and re.search(r'one[ -]?shot',label,re.I):
                add(1,a['href']);continue
            m = re.search(r'\b(?:chapter|ch\.)\s*(\d+)(?![\d.])\b',label,re.I)
            if not m or not '/chapter/' in a['href']:
                raise ValueError('Unresolved split, special or unnumbered chapter')
            add(int(m[1]),a['href'])
    if not title or not rows or sorted(rows)!=list(range(min(rows),max(rows)+1)) or min(rows) not in (0,1):
        raise ValueError('Missing or non-contiguous catalogue')
    return title.get_text(' ',strip=True),author.get_text(' ',strip=True) if author else 'Unknown',sorted(rows.items())

def chapter(url, fan, number):
    doc = page(url)
    if urlsplit(url).hostname=='www.royalroad.com':
        heading=doc.select_one('h1')
        container=doc.select_one('.chapter-content')
        if not heading or not container:raise ValueError('Royal Road chapter unavailable')
        body='\n\n'.join(p.get_text(' ',strip=True) for p in container.select('p'))
        if len(body)<250:raise ValueError('Royal Road chapter truncated')
        return heading.get_text(' ',strip=True),body
    header = doc.select_one('#chapter-article h2' if fan else '.chapter-title')
    container = doc.select_one('.chapter-content' if fan else '.chapter-start-mark')
    if not header or not container: raise ValueError('No readable chapter')
    if not fan:
        start = container
        texts=[]
        for node in start.find_next_siblings():
            if 'chapter-end-mark' in node.get('class',[]): break
            if node.name=='p': texts.append(node.get_text(' ',strip=True))
        if not texts: raise ValueError('No text inside chapter markers')
    heading = header.get_text(' ',strip=True)
    if not (number==1 and re.search(r'one[ -]?shot',heading,re.I)) and not re.search(r'\b(?:chapter|ch\.)\s*'+str(number)+r'\b',heading,re.I): raise ValueError('Chapter number mismatch')
    body = '\n\n'.join(p.get_text(' ',strip=True) for p in container.select('p') if p.get_text(strip=True)) if fan else '\n\n'.join(t for t in texts if t)
    if len(body)<250 or any(term in body.lower() for term in ['unlock this chapter','chapter is locked','chapter preview only','exceeded your reading limit']):
        raise ValueError('Empty, restricted or partial chapter')
    return heading,body

def process(url,folder,minimum):
    title,author,links = catalogue(url)
    if len(links)<minimum: raise ValueError(f'Index has {len(links)}, below required {minimum}')
    folder.mkdir(parents=True,exist_ok=True)
    rows,seen=[],set()
    for pos,(number,link) in enumerate(links,1):
        name=f'chapter_{pos:05d}.txt'
        path=folder/name
        record=folder/(name+'.json')
        if path.exists() and record.exists():
            row=json.loads(record.read_text())
            if row['url']!=link or hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']: raise ValueError('Checkpoint identity mismatch')
            body=path.read_text(encoding='utf-8').split('\n\n',1)[1]
        else:
            time.sleep(1)
            heading,body=chapter(link,'fanmtl.com' in url,number)
            data=(heading+'\n\n'+body+'\n').encode()
            row=dict(position=pos,chapter_number=number,url=link,title=heading,file=name,sha256=hashlib.sha256(data).hexdigest(),word_count=len(body.split()))
            path.write_bytes(data)
            record.write_text(json.dumps(row))
        digest=hashlib.sha256(' '.join(body.split()).encode()).hexdigest()
        if digest in seen: raise ValueError('Repeated chapter body')
        seen.add(digest);rows.append(row)
    _epub(folder,rows,title,author,'en',url)
    (folder/'metadata.json').write_text(json.dumps(dict(title=title,author=author,language='en',chapter_count=len(rows),source_url=url)))
    (folder/'chapters.json').write_text(json.dumps(rows))
    return folder
