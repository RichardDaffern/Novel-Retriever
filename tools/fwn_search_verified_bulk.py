"""Search real FreeWebNovel listings for wishlist books missing from both preferred sites.

This is the source-level fallback campaign after NovelFull and ReadNovelFull.
It searches the public /search?keyword= endpoint rather than guessing slugs.
No chapter prose is downloaded in discovery. Source identity, original-edition
minimums, exclusions and the existing downloader's chapter integrity gates
remain enforced. Only explicitly authorised original public novels proceed.
"""
from __future__ import annotations

import argparse
from difflib import SequenceMatcher
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlsplit
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from tools import overnight_queue as q
from tools.freewebnovel_downloader import book_details
from tools.freewebnovel_source import fetch_public_html, validate_book_url

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ROOT / "campaigns/fwn-search-20261125/targets.json"
CAMPAIGN = "freewebnovel-real-search-20261125"
SEARCH_ROOT = "https://freewebnovel.com/search"
BATCH_SIZE = 8
MAX_IN_FLIGHT = 2
SEARCH_DELAY_SECONDS = 0.65
RUN_DELAY_SECONDS = 120
POLL_DELAY_SECONDS = 75

# From the previous NovelFull/ReadNovelFull campaign and known failed source
# audits. Do not redownload existing completed artefacts from a lower priority
# website or duplicate a currently running request.
ALREADY_SUBMITTED = {
    "World Domination System", "Path to Heaven", "Omega Summoner",
    "A Record Of Mortal’s Journey To Immortality",
    "Attack Of The Adorable Kid: President Daddy's Infinite Pampering",
    "Beautiful Time With You",
    "Bringing The Nation's Husband Home", "Legend of Swordsman",
    "Legend of Mythological Genes", "Tensei Shitara Slime Datta Ken",
    "The Military Female Soldier With Unwavering Stubbornness",
    "Yong Heng Zhi Zun",
}
KNOWN_FULL_LENGTH = {
    "Past Life Returner": 575, "Omega Summoner": 3089,
    "World Domination System": 1167, "Legend of Swordsman": 6492,
    "The S-Classes That I Raised": 817, "Flower Master In The City": 1553,
    "Doom Lord": 856, "Beast Piercing The Heavens": 1445,
    "Godly Student": 2783, "The Military Female Soldier With Unwavering Stubbornness": 5577,
    "Game Market 1983": 252, "Tomb Raider King": 416,
    "Heavenly Star": 556, "Weapon Master": 2276,
}
FLOOR = {q.norm(k):v for k,v in KNOWN_FULL_LENGTH.items()}


def normalise(title: str) -> str:
    text=unicodedata.normalize("NFKD",title).encode("ascii","ignore").decode().lower()
    text=text.replace("levelling","leveling").replace("favourite","favorite")
    return " ".join(re.findall(r"[a-z0-9]+",text))


def score(a: str,b: str) -> float:
    left=normalise(a);right=normalise(b)
    if left==right and left:
        return 1.0
    # Prefixes/suffixes are allowed when the user supplied a colon subtitle.
    if ":" in a and normalise(a.rsplit(":",1)[-1])==right:
        return 1.0
    if ":" in b and left==normalise(b.rsplit(":",1)[-1]):
        return 1.0
    at=[s for s in left.split() if s not in {"the","a","an","of","and","with","in","to"}]
    bt=[s for s in right.split() if s not in {"the","a","an","of","and","with","in","to"}]
    if at==bt and len(at)>=2:
        return 1.0
    if len(left)<13 or len(right)<13:
        return 0.0
    lexical=sum(any(SequenceMatcher(None,t,u).ratio()>=.88 for u in bt) for t in at)/max(1,len(at))
    ratio=SequenceMatcher(None,left,right).ratio()
    return ratio if lexical>=.9 and ratio>=.94 else 0.0


def queries(title: str) -> list[str]:
    candidates=[title]
    if ":" in title:
        candidates.append(title.rsplit(":",1)[-1].strip())
    swapped=(title.replace("Levelling","Leveling").replace("levelling","leveling")
                   .replace("Favourite","Favorite"))
    if swapped!=title:
        candidates.append(swapped)
    return list(dict.fromkeys(x for x in candidates if len(x.strip())>=3))


def search_page(phrase: str) -> str:
    url=SEARCH_ROOT+"?"+urlencode({"keyword":phrase})
    with urlopen(Request(url,headers={"User-Agent":"NovelRetriever-Book-Index/1.0"}),
                 timeout=25) as response:
        final=urlsplit(response.url)
        if (response.status!=200 or final.hostname!="freewebnovel.com"
                or final.path!="/search"):
            raise ValueError("Unexpected search response or cross-path redirect")
        data=response.read(600001)
        if len(data)>600000:
            raise ValueError("Search page exceeded 600 KiB")
        return data.decode("utf-8-sig","replace")


def book_links(html: str) -> list[tuple[str,str]]:
    soup=BeautifulSoup(html,"html.parser")
    links=[];seen=set()
    for a in soup.select("a[href]"):
        u=urljoin("https://freewebnovel.com/",a["href"])
        p=urlsplit(u)
        if (p.scheme!="https" or p.hostname!="freewebnovel.com" or
            p.query or not re.fullmatch(r"/novel/[a-z0-9]+(?:-[a-z0-9]+)*",p.path)):
            continue
        title=a.get_text(" ",strip=True)
        if not 2<=len(title)<=230 or u in seen:
            continue
        seen.add(u)
        links.append((title,"https://freewebnovel.com"+p.path))
    return links


def discover(out:Path,*,searcher=search_page,page_fetcher=fetch_public_html,
             parser=book_details,sleeper=time.sleep) ->dict:
    targets=json.loads(TARGETS.read_text(encoding="utf-8"))["titles"]
    if len(targets)!=100 or len({q.norm(t) for t in targets})!=100:
        raise ValueError("Unexpected wishlist reconciliation source")
    registry=q.read_json(q.REGISTRY)["novels"]
    done=[x for x in registry if any(
        d.get("status")=="complete" and d.get("range")=="all"
        for d in x.get("downloads",[]) if isinstance(d,dict))]
    complete_names={q.norm(x["title"]) for x in done}
    complete_urls={x["url"] for x in done}
    previous=q.read_json(q.VERIFIED)["entries"]
    completed_aliases={q.norm(x["title"]) for x in previous
                       if x.get("url") in complete_urls}
    excluded={q.norm(t) for t in q.read_json(q.DENY)["excluded"]}
    skip={q.norm(t) for t in ALREADY_SUBMITTED}
    skip.update(complete_names)
    skip.update(completed_aliases)
    # Historical deterministic FreeWebNovel content/index failures should be
    # recovered separately, not retried wholesale as new books.
    blocked={q.norm(x) for x in q.read_json(
        q.OVERNIGHT/"blocked-full-retries-20261120.json")["titles"]}
    blocked.update(q.norm(t) for t in (
        "This MC Is Kickass", "Past Life Returner", "Tomb Raider King",
        "World Domination System", "Beautiful Time With You",
    ))
    verified=[];held=[];requests=0;seen_urls=set();blocked_site=False
    for title in targets:
        key=q.norm(title)
        if key in excluded:
            held.append({"title":title,"reason":"global_red_or_dropped_exclusion"})
            continue
        if key in skip:
            held.append({"title":title,"reason":"complete_or_already_submitted"})
            continue
        if key in blocked:
            held.append({"title":title,"reason":"known_deterministic_source_failure"})
            continue
        found=[];errors=[]
        for phrase in queries(title):
            if blocked_site:
                break
            if requests:
                sleeper(SEARCH_DELAY_SECONDS)
            requests+=1
            try:
                for other,url in book_links(searcher(phrase)):
                    rank=max(score(title,other),score(phrase,other))
                    if rank>=.94:
                        found.append((rank,other,url))
            except HTTPError as exc:
                errors.append(f"search_HTTP_{exc.code}")
                if exc.code in (403,429):
                    blocked_site=True
            except (URLError,OSError,ValueError,TimeoutError) as exc:
                errors.append("search_"+type(exc).__name__)
        found.sort(key=lambda x:(-x[0],x[2]))
        distinct=[];used=set()
        for match in found:
            if match[2] not in used:
                used.add(match[2]);distinct.append(match)
        if len(distinct)>1 and distinct[1][0]>=distinct[0][0]-.035:
            held.append({"title":title,"reason":"ambiguous_search_results",
                         "alternatives":[x[1] for x in distinct[:4]]})
            continue
        if not distinct:
            held.append({"title":title,"reason":",".join(errors) or
                         ("source_access_blocked" if blocked_site else "not_found")})
            continue
        similarity,name,url=distinct[0]
        try:
            url=validate_book_url(url)
            if url in complete_urls or url in seen_urls:
                raise ValueError("Already registered or duplicate source URL")
            result=parser(page_fetcher(url),url)
            if max(score(title,result["title"]),score(name,result["title"]))<.94:
                raise ValueError("Book page title disagrees with the requested novel")
            count=result["numChapters"]
            minimum=FLOOR.get(key,2)
            if count<minimum:
                raise ValueError(f"Short source edition: {count} chapters, expected at least {minimum}")
            if result.get("status") not in ("Completed","Ongoing"):
                raise ValueError("No verified publication status")
            candidate={"title":title,"url":url,"source_title":result["title"],
                       "author":result["author"],"chapters":count,
                       "status":result["status"],"confidence":round(similarity,3)}
            seen_urls.add(url);verified.append(candidate)
            print("FWSOURCE_VERIFIED",title,"=>",result["title"],count,url,flush=True)
        except (ValueError,KeyError,OSError,TypeError) as exc:
            held.append({"title":title,"url":url,"reason":"source_index:"+str(exc)[:230]})
            print("FWSOURCE_HELD",title,str(exc)[:230],flush=True)
    result={"campaign":CAMPAIGN,"version":1,"requested_titles":len(targets),
            "verified":verified,"unresolved":held,"search_requests":requests,
            "source_access_blocked":blocked_site,
            "contains_chapter_prose":False}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("FW_SOURCE_RESULT",len(verified),"verified",len(held),"held",requests,"searches",flush=True)
    return result


def dispatch(source:dict,out:Path,*,runner=subprocess.run,sleeper=time.sleep,
             clock=time.monotonic,minutes=250)->dict:
    if source.get("campaign")!=CAMPAIGN or source.get("version")!=1:
        raise ValueError("Invalid source report")
    if (os.getenv("GITHUB_REPOSITORY")!="RichardDaffern/Novel-Retriever"
        or os.getenv("GITHUB_ACTIONS")!="true" or os.getenv("GITHUB_RUN_ATTEMPT")!="1"):
        raise ValueError("Only a first-attempt authorised GitHub Actions dispatcher may submit")
    targets={q.norm(t) for t in json.loads(TARGETS.read_text(encoding="utf-8"))["titles"]}
    denied={q.norm(t) for t in q.read_json(q.DENY)["excluded"]}
    completed={r["url"] for r in q.read_json(q.REGISTRY)["novels"] if any(
        d.get("status")=="complete" and d.get("range")=="all"
        for d in r.get("downloads",[]) if isinstance(d,dict))}
    selected=list(source.get("verified",[]))
    urls=set();names=set()
    for item in selected:
        title=item.get("title","");url=item.get("url","")
        canonical=validate_book_url(url)
        if (q.norm(title) not in targets or q.norm(title) in denied or
            q.norm(title) in names or canonical!=url or url in completed
            or url in urls or int(item.get("chapters",0))<FLOOR.get(q.norm(title),2)):
            raise ValueError(f"Unapproved or repeated novel: {title}")
        names.add(q.norm(title));urls.add(url)
    report={"campaign":CAMPAIGN,"version":1,"verified":len(selected),
            "submitted":[],"held":list(selected),"remaining":len(selected)}
    def persist():
        out.parent.mkdir(parents=True,exist_ok=True)
        tmp=out.with_suffix(".tmp")
        tmp.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        tmp.replace(out)
    persist();deadline=clock()+minutes*60
    while selected:
        if clock()>=deadline:
            report["stop_reason"]="dispatch_time_budget";break
        try:
            active=q.active_workflows(runner=runner)
        except (OSError,ValueError,subprocess.SubprocessError) as exc:
            report["stop_reason"]="could_not_check_active_runs:"+type(exc).__name__;break
        if active>=MAX_IN_FLIGHT:
            sleeper(POLL_DELAY_SECONDS);continue
        batch=selected[:BATCH_SIZE]
        command=["gh","workflow","run",q.WORKFLOW,"--ref","main",
                 "--raw-field","novel_urls="+",".join(x["url"] for x in batch),
                 "--raw-field","chapter_range=","--raw-field","force=false",
                 "--raw-field","confirm_rights=true"]
        try:
            runner(command,check=True,timeout=45)
        except (OSError,subprocess.SubprocessError) as exc:
            report["stop_reason"]="dispatch_failed:"+type(exc).__name__;break
        report["submitted"].append({"titles":[x["title"] for x in batch],
                                    "urls":[x["url"] for x in batch]})
        del selected[:len(batch)]
        report["held"]=list(selected);report["remaining"]=len(selected)
        persist()
        print("FW_BULK_DISPATCHED",len(batch),[x["title"] for x in batch],flush=True)
        if selected:sleeper(RUN_DELAY_SECONDS)
    persist()
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("operation",choices=("discover","dispatch"))
    parser.add_argument("--source",type=Path)
    parser.add_argument("--out",type=Path,required=True)
    options=parser.parse_args()
    if options.operation=="discover":
        discover(options.out)
    else:
        if not options.source:parser.error("dispatch needs --source")
        result=dispatch(json.loads(options.source.read_text(encoding="utf-8")),options.out)
        print("FW_BULK_TOTAL",sum(len(x["titles"]) for x in result["submitted"]),
              "submitted;",result["remaining"],"held",flush=True)
        if result.get("stop_reason"):
            raise SystemExit(1)


if __name__=="__main__":
    main()
