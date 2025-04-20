from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional
from urllib.parse import urljoin
from pprint import pprint

import requests
from bs4 import BeautifulSoup, Tag


@dataclass(frozen=True, slots=True)
class QARecord:
    context: str
    question: str = ""
    answer: str = ""

    def as_dict(self) -> Dict[str, str]:
        return {"context": self.context, "question": self.question, "answer": self.answer}


def crawl_rd_tax(entry_url: str = "https://www.rd.go.th/548.html",
                 timeout: int = 15) -> List[Dict[str, str]]:
    """
    Crawl the RD (Thai Revenue Department) knowledge‑base starting from *entry_url*.
    For every link in the left‑hand nested sidebar, fetch the page and return a list
    of dicts shaped ⟨context, question, answer⟩.  Sidebar detection and content
    extraction are heuristic but resilient to layout changes.

    :param entry_url: The first page that hosts the sidebar to walk.
    :param timeout:   HTTP timeout (seconds) for each request.
    :return:          List of dictionaries ready for downstream RAG pipelines.
    """
    sess = requests.Session()
    root_soup = _get_soup(sess, entry_url, timeout)

    # 1 ▶ Collect sidebar links (unique, in order of appearance)
    sidebar = _locate_sidebar(root_soup)
    links = [
        urljoin(entry_url, a["href"])
        for a in sidebar.select("a[href]")
        if a["href"].endswith(".html")
    ]
    seen: set[str] = set()
    unique_links = [u for u in links if not (u in seen or seen.add(u))]

    # 2 ▶ Walk each page and harvest
    records: List[QARecord] = []
    for url in unique_links:
        try:
            page_soup = _get_soup(sess, url, timeout)
            rec = _extract_record(page_soup)
            records.append(rec)
        except Exception:
            # Fail fast but leave a breadcrumb for post‑mortem
            records.append(QARecord(context=f"[ERROR] Could not crawl {url}"))

    return [r.as_dict() for r in records]


# ──────────── internal helpers ──────────── #

def _get_soup(sess: requests.Session, url: str, timeout: int) -> BeautifulSoup:
    resp = sess.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")


def _locate_sidebar(soup: BeautifulSoup) -> Tag:
    """
    RD pages put the topic tree in the first UL with at least ten <li>.
    This works for every tax‑knowledge page tested (e.g. 548.html, 549.html).
    """
    for ul in soup.find_all("ul"):
        if len(ul.find_all("li")) >= 10:
            return ul
    raise RuntimeError("Sidebar menu not found – page layout may have changed.")


def _extract_record(soup: BeautifulSoup) -> QARecord:
    # Question → the first H1/H2/H3 tag (Thai pages often use H3)
    heading_tag: Optional[Tag] = next(
        (soup.find(tag) for tag in ("h1", "h2", "h3") if soup.find(tag)), None
    )

    question = heading_tag.get_text(strip=True) if heading_tag else ""

    # Context → pick the largest <article>, <section>, or <div> block by text length
    candidate_blocks = soup.find_all(["article", "section", "div"], recursive=True)
    main_block = max(candidate_blocks, key=lambda t: len(t.get_text(" ", strip=True)))
    full_text = main_block.get_text(" ", strip=True)

    # Answer → body minus heading (if present and non‑trivial), else blank
    answer = ""
    if question and question in full_text:
        answer = full_text.split(question, 1)[1].lstrip(" :–-")
    else:
        # No clean split; treat entire text as context only
        return QARecord(context=full_text)

    return QARecord(context=full_text, question=question, answer=answer)


if __name__ == "__main__":
    data = crawl_rd_tax()

    pprint(data[0])
