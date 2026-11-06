"""Parse the Chinese Chemical Society conference-paper retrieval system.

https://www.chemsoc.org.cn/library/papers/ — a rung-4 deposit index covering 210
CCS meetings. Each meeting record carries a 论文集 table with one abstract volume
(摘要集) per division, each stating its own 论文数.

Fetching note: the pages 302 to index.php for a bare request. They need a session
cookie and a Referer of the index page. See `fetch` below.
"""
import html
import re

BASE = "https://www.chemsoc.org.cn/library/papers/"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

#: volumes whose contents are invited talks, not contributed abstracts
INVITED_MARKERS = ("大会特邀报告",)


def _cells(row):
    return [html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
            for c in re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.S)]


def _rows(page):
    return re.findall(r"<tr[^>]*>(.*?)</tr>", page, flags=re.S)


def parse_meeting_list(page):
    """Every meeting on one index page, with the id its record lives at."""
    meetings = []
    for row in _rows(page):
        cells = _cells(row)
        m = re.search(r"meeting\.php\?id=(\d+)", row)
        if m and len(cells) >= 3:
            meetings.append({"year": cells[0], "name": cells[1],
                             "place": cells[2], "id": int(m.group(1))})
    return meetings


def parse_total_meetings(page):
    m = re.search(r"共找到\s*(\d+)\s*个会议", page)
    return int(m.group(1)) if m else None


def parse_page_count(page):
    m = re.search(r"第\s*\d+\s*/\s*(\d+)\s*页", page)
    return int(m.group(1)) if m else None


def parse_meeting_name(page):
    m = re.search(r"【会议名称】\s*([^<\n]+)", html.unescape(
        re.sub(r"<(?!/?td)[^>]*>", " ", page)))
    return m.group(1).strip() if m else None


def parse_volumes(page):
    """(volume name, 论文数) for every abstract volume in the 论文集 table."""
    volumes = []
    for row in _rows(page):
        cells = _cells(row)
        if len(cells) >= 2 and "摘要集" in cells[0] and re.fullmatch(r"\d+", cells[1]):
            volumes.append((cells[0], int(cells[1])))
    return volumes


def _is_invited(name):
    return any(marker in name for marker in INVITED_MARKERS)


def total_abstracts(page):
    return sum(n for _, n in parse_volumes(page))


def invited_abstracts(page):
    return sum(n for name, n in parse_volumes(page) if _is_invited(name))


def contributed_abstracts(page):
    return total_abstracts(page) - invited_abstracts(page)
