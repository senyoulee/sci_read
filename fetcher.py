import requests
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from config import CATEGORIES, ARXIV_API_URL, MAX_RESULTS_PER_REQUEST, AUTHORS_CAP, FETCH_DELAY

ARXIV_NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'arxiv': 'http://arxiv.org/schemas/atom',
    'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
}


def parse_entries(root):
    papers = []
    for entry in root.findall('atom:entry', ARXIV_NS):
        id_url = entry.find('atom:id', ARXIV_NS).text
        arxiv_id = id_url.split('/abs/')[-1].split('v')[0]

        title = entry.find('atom:title', ARXIV_NS).text.strip().replace('\n', ' ')
        abstract = entry.find('atom:summary', ARXIV_NS).text.strip().replace('\n', ' ')

        all_authors = [
            a.find('atom:name', ARXIV_NS).text
            for a in entry.findall('atom:author', ARXIV_NS)
        ]
        if len(all_authors) > AUTHORS_CAP:
            authors = ', '.join(all_authors[:AUTHORS_CAP]) + ', et al.'
        else:
            authors = ', '.join(all_authors)

        published = entry.find('atom:published', ARXIV_NS).text
        submitted = published[:10]  # YYYY-MM-DD

        cats = [c.get('term') for c in entry.findall('atom:category', ARXIV_NS)]
        categories = ', '.join(cats)

        journal_el = entry.find('arxiv:journal_ref', ARXIV_NS)
        journal_ref = journal_el.text.strip() if journal_el is not None and journal_el.text else ''

        url = f"https://arxiv.org/abs/{arxiv_id}"

        papers.append({
            'arxiv_id': arxiv_id,
            'title': title,
            'abstract': abstract,
            'authors': authors,
            'submitted': submitted,
            'categories': categories,
            'journal_ref': journal_ref,
            'url': url,
        })
    return papers


def fetch_papers_for_category(category, date_from, date_to):
    """Fetch all papers for a category in a date range with pagination."""
    all_papers = []
    start = 0

    date_from_str = date_from.strftime('%Y%m%d')
    date_to_str = date_to.strftime('%Y%m%d')
    query = f'cat:{category} AND submittedDate:[{date_from_str}0000 TO {date_to_str}2359]'

    while True:
        params = {
            'search_query': query,
            'start': start,
            'max_results': MAX_RESULTS_PER_REQUEST,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending',
        }
        try:
            resp = requests.get(ARXIV_API_URL, params=params, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            print(f"  Error fetching {category} (start={start}): {e}")
            break

        root = ET.fromstring(resp.content)
        total_el = root.find('opensearch:totalResults', ARXIV_NS)
        total = int(total_el.text) if total_el is not None else 0
        entries = parse_entries(root)
        all_papers.extend(entries)

        start += len(entries)
        if start >= total or len(entries) == 0:
            break

        time.sleep(FETCH_DELAY)

    return all_papers


def fetch_daily():
    """Fetch recent papers (last 7 days) for all categories.
    Wide window accounts for weekends/holidays; DB dedup prevents duplicates.
    """
    today = datetime.now(timezone.utc).date()
    two_days_ago = today - timedelta(days=7)

    all_papers = []
    for cat in CATEGORIES:
        print(f"  Fetching {cat} ({today - timedelta(days=7)} to {today})...")
        papers = fetch_papers_for_category(cat, two_days_ago, today)
        print(f"    Found {len(papers)} papers")
        all_papers.extend(papers)
        time.sleep(FETCH_DELAY)

    return all_papers


def fetch_backfill(period):
    """Fetch historical papers. period: '1y', '6m', '3m'"""
    today = datetime.now(timezone.utc).date()
    days_map = {'1y': 365, '6m': 180, '3m': 90}
    if period not in days_map:
        raise ValueError(f"Unknown period: {period}. Choose from 1y, 6m, 3m.")
    date_from = today - timedelta(days=days_map[period])

    all_papers = []
    for cat in CATEGORIES:
        print(f"  Backfilling {cat} from {date_from} to {today}...")
        papers = fetch_papers_for_category(cat, date_from, today)
        print(f"    Found {len(papers)} papers")
        all_papers.extend(papers)
        time.sleep(FETCH_DELAY)

    return all_papers
