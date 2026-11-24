#!/usr/bin/env python3
"""Source-first public ReadNovelFull search for the 71 still-unmatched wishlist titles.

Only matching public book-index pages are considered; the strict ReadNovelFull
adapter must validate every indexed chapter before dispatch. Does not fetch
chapter prose. User-confirmed archiving permission is passed to the existing
workflows; this script never modifies HF data.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlsplit
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from tools import novelfull_alias_campaign as old
from tools import overnight_queue as q
from tools.readnovelfull_source import discover as index_book
from tools.mixed_source_bulk import _validated_url

TARGETS = old.TARGETS
CAMPAIGN = "readnovelfull-71-remaining-20261124"
SEARCH_PREFIX = "https://readnovelfull.com/novel-list/search?"
BATCH_SIZE = 10
MAX_ACTIVE = 2
MATCH_SCORE = 0.91
PAUSE = 0.65
SKIP_NOVELFULL = set("""
A Record Of Mortal’s Journey To Immortality
Attack Of The Adorable Kid: President Daddy's Infinite Pampering
Beautiful Time With You
Beauty And The Bodyguard
Bringing The Nation's Husband Home
Seoul Station's Necromancer
Legend of Swordsman
A Thought Through Eternity
I Can Extract Everything
Legend of Mythological Genes
Tensei Shitara Slime Datta Ken
The Military Female Soldier With Unwavering Stubbornness
Yong Heng Zhi Zun
Advent of Archmage
Arifureta Shokugyou De Sekai Saikyou
Charm Of Soul Pet
Crazy Levelling System
Desolate Era
Dungeon Defence
Evil Dragon Against The Heaven
Golden Time (JungYong)
Invincible Dragon Emperor
Levelling Up And Becoming Undefeated
Records of the Human Emperor
Solo Levelling
Soul Land
The School Prince is a Girl
Warlock Of Magus World
Xian Ni
""".strip().splitlines())
HISTORICAL_FLOORS = {
    "Godly Student": 2783,
    "Doom Lord": 856,
    "Beast Piercing The Heavens": 1445,
    "Past Life Returner": 575,
    "Omega Summoner": 3083,
    "Legend of Swordsman": 6492,
    "World Domination System": 1167,
    "Heavenly Star": 556,
    "The S-Classes That I Raised": 817,
    "Flower Master In The City": 1553,
}
FLOOR = {old.canon(k): int(v) for k, v in HISTORICAL_FLOORS.items()}


def search_html(title: str) -> str:
    url = SEARCH_PREFIX + urlencode({"keyword": title})
    req = Request(url, headers={"User-Agent": "NovelRetriever-Book-Index/1.0"})
    with urlopen(req, timeout=20) as res:
        if res.status != 200 or urlsplit(res.url).hostname != "readnovelfull.com":
            raise ValueError("Unexpected public search redirect/status")
        data = res.read(600001)
        if len(data) > 600000:
            raise ValueError("ReadNovelFull search result oversized")
        return data.decode("utf-8-sig", "replace")


def links(html: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    out, seen = [], set()
    for a in soup.select("a[href]"):
        url = urljoin("https://readnovelfull.com/", a["href"])
        p = urlsplit(url)
        if (p.scheme != "https" or p.hostname != "readnovelfull.com" or
            p.query or not re.fullmatch(r"/[a-z0-9][a-z0-9_-]*\.html", p.path)):
            continue
        title = a.get_text(" ", strip=True)
        if not title or len(title) > 230 or url in seen:
            continue
        seen.add(url)
        out.append((title, url))
    return out


def scan(out: Path, *, fetcher=search_html, discover=index_book,
         sleeper=time.sleep) -> dict:
    all_titles=json.loads(TARGETS.read_text(encoding="utf-8"))["titles"]
    assert len(all_titles)==100
    known={old.canon(x) for x in SKIP_NOVELFULL}
    selected=[x for x in all_titles if old.canon(x) not in known]
    assert len(selected)==71
    forbidden={old.canon(x) for x in q.read_json(q.DENY)["excluded"]}
    registry=q.read_json(q.REGISTRY)
    registered={x["url"] for x in registry["novels"] if any(
        d.get("status")=="complete" and d.get("range")=="all"
        for d in x.get("downloads",[]) if isinstance(d,dict))}
    verified, unresolved, req_count, url_seen = [], [], 0, set()
    for wanted in selected:
        if old.canon(wanted) in forbidden:
            unresolved.append({"title":wanted,"reason":"global_exclusion"})
            continue
        candidates=[]
        reasons=[]
        for term in old.queries(wanted):
            if req_count:
                sleeper(PAUSE)
            req_count+=1
            try:
                for source_title, link in links(fetcher(term)):
                    score=max(old.similarity(wanted,source_title),old.similarity(term,source_title))
                    if score>=MATCH_SCORE:
                        candidates.append((score,source_title,link))
            except HTTPError as exc:
                reasons.append("search_HTTP_"+str(exc.code))
                if exc.code in (403,429):
                    raise ValueError("Source blocked requests; stop without access bypass") from exc
            except (URLError,OSError,TimeoutError,ValueError) as exc:
                reasons.append("search_"+type(exc).__name__)
        candidates.sort(key=lambda x:(-x[0],x[2]))
        dedup={}
        for candidate in candidates:
            dedup.setdefault(candidate[2],candidate)
        candidates=list(dedup.values())
        if len(candidates)>1 and candidates[1][0]>=candidates[0][0]-.035:
            unresolved.append({"title":wanted,"reason":"ambiguous_source_titles",
                                "candidates":[x[1] for x in candidates[:3]]})
            continue
        if not candidates:
            unresolved.append({"title":wanted,"reason":",".join(reasons) or "not_found"})
            continue
        score, search_title, url=candidates[0]
        if url in url_seen or url in registered:
            unresolved.append({"title":wanted,"reason":"already_registered_or_reused_URL"})
            continue
        try:
            _, url=_validated_url(url)
            detail=discover(url)
            site_title=detail.get("title","")
            if max(old.similarity(wanted,site_title),old.similarity(search_title,site_title))<MATCH_SCORE:
                raise ValueError("Book title differs from search result")
            count=detail["numChapters"]
            if count<len(detail["chapters"]) or count<FLOOR.get(old.canon(wanted),2):
                raise ValueError(f"Short edition: indexed {count} chapters")
            if detail.get("status") not in ("Completed","Ongoing"):
                raise ValueError("Publication state unclear")
            verified.append({"title":wanted,"url":url,"source_title":site_title,
                             "chapters":count,"status":detail["status"],
                             "author":detail.get("author","Unknown"),"score":round(score,3)})
            url_seen.add(url)
            print("READNOVELFULL_VERIFIED",wanted,"=>",site_title,count,detail["status"],url,flush=True)
        except (ValueError, OSError,TimeoutError, KeyError, TypeError) as exc:
            unresolved.append({"title":wanted,"source_url":url,
                               "reason":"index_validation:"+str(exc)[:210]})
            print("READNOVELFULL_HELD",wanted,str(exc)[:200],flush=True)
    result={"version":1,"campaign":CAMPAIGN,"targets":len(selected),
            "verified":verified,"unresolved":unresolved,
            "search_requests":req_count,"contains_chapter_text":False}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("READNOVELFULL_SCAN_TOTAL",len(selected),"candidates,",len(verified),"verified,",len(unresolved),"held",flush=True)
    return result


def dispatch(payload: dict, out: Path, *, runner=subprocess.run,
             sleeper=time.sleep, clock=time.monotonic) -> dict:
    if payload.get("campaign")!=CAMPAIGN or payload.get("version")!=1:
        raise ValueError("Invalid scan report")
    if (os.getenv("GITHUB_REPOSITORY")!="RichardDaffern/Novel-Retriever" or
        os.getenv("GITHUB_ACTIONS")!="true" or os.getenv("GITHUB_RUN_ATTEMPT")!="1"):
        raise ValueError("Must run once on authorised GitHub Actions")
    selected=list(payload.get("verified",[]))
    skipped=set(old.canon(x) for x in SKIP_NOVELFULL)
    allowed={old.canon(x) for x in json.loads(TARGETS.read_text(encoding="utf-8"))["titles"]}
    registered={r["url"] for r in q.read_json(q.REGISTRY)["novels"] if any(
        d.get("status")=="complete" and d.get("range")=="all"
        for d in r.get("downloads",[]) if isinstance(d,dict))}
    seen=set()
    for x in selected:
        title=x.get("title",""); url=x.get("url","")
        _,canonical=_validated_url(url)
        if (old.canon(title) not in allowed or old.canon(title) in skipped or
            old.canon(title) in seen or canonical!=url or
            url in registered or x.get("chapters",0)<FLOOR.get(old.canon(title),2)):
            raise ValueError("Unapproved or duplicated bulk candidate")
        seen.add(old.canon(title))
    report={"version":1,"campaign":CAMPAIGN,"verified":len(selected),
            "submitted":[],"held":list(selected),"remaining":len(selected)}
    def save():
        out.parent.mkdir(parents=True,exist_ok=True)
        tmp=out.with_suffix(".tmp")
        tmp.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        tmp.replace(out)
    save()
    deadline=clock()+270*60
    while selected:
        if clock()>deadline:
            report["stop_reason"]="time_budget_exhausted"
            break
        try:
            active=q.active_workflows(runner=runner)
        except (OSError,ValueError,subprocess.SubprocessError) as exc:
            report["stop_reason"]="unable_to_check_active_workflows:"+type(exc).__name__
            break
        if active>=2:
            sleeper(75)
            continue
        batch=selected[:BATCH_SIZE]
        cmd=["gh","workflow","run","library-bulk-download.yml","--ref","main",
             "--raw-field","novel_urls="+",".join(x["url"] for x in batch),
             "--raw-field","chapter_range=","--raw-field","force=false",
             "--raw-field","confirm_rights=true"]
        try:
            runner(cmd,check=True,timeout=45)
        except (OSError,subprocess.SubprocessError) as exc:
            report["stop_reason"]="dispatch_rejected:"+type(exc).__name__
            break
        report["submitted"].append({"titles":[x["title"] for x in batch],
                                    "urls":[x["url"] for x in batch]})
        del selected[:len(batch)]
        report["held"]=list(selected)
        report["remaining"]=len(selected)
        save()
        print("READNOVELFULL_BULK_DISPATCHED",len(batch),"titles",flush=True)
        if selected:
            sleeper(90)
    save()
    return report


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("operation",choices=["scan","dispatch"])
    p.add_argument("--input",type=Path)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.operation=="scan":
        scan(args.out)
    else:
        if not args.input:
            p.error("dispatch requires --input")
        result=dispatch(json.loads(args.input.read_text(encoding="utf-8")),args.out)
        print("READNOVELFULL_DISPATCH_TOTAL",sum(len(b["titles"]) for b in result["submitted"]),flush=True)
        if result.get("stop_reason"):
            print("STOP",result["stop_reason"],flush=True)
            raise SystemExit(1)


if __name__=="__main__":
    main()
