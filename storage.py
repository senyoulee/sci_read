import sqlite3
import os
from config import DB_PATH


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            arxiv_id    TEXT PRIMARY KEY,
            title       TEXT,
            abstract    TEXT,
            authors     TEXT,
            submitted   DATE,
            categories  TEXT,
            journal_ref TEXT,
            url         TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_papers(papers):
    """Insert papers, skip duplicates. Returns list of newly inserted papers."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    new_papers = []
    for p in papers:
        try:
            c.execute('''
                INSERT OR IGNORE INTO papers
                (arxiv_id, title, abstract, authors, submitted, categories, journal_ref, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                p['arxiv_id'], p['title'], p['abstract'], p['authors'],
                p['submitted'], p['categories'], p['journal_ref'], p['url']
            ))
            if c.rowcount > 0:
                new_papers.append(p)
        except Exception as e:
            print(f"Error saving {p['arxiv_id']}: {e}")
    conn.commit()
    conn.close()
    return new_papers


def search_papers(keyword=None, author=None, category=None, date_from=None, date_to=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    query = "SELECT * FROM papers WHERE 1=1"
    params = []

    if keyword:
        query += " AND (title LIKE ? OR abstract LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if author:
        query += " AND authors LIKE ?"
        params.append(f"%{author}%")
    if category:
        query += " AND categories LIKE ?"
        params.append(f"%{category}%")
    if date_from:
        query += " AND submitted >= ?"
        params.append(date_from)
    if date_to:
        query += " AND submitted <= ?"
        params.append(date_to)

    query += " ORDER BY submitted DESC"

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    columns = ['arxiv_id', 'title', 'abstract', 'authors', 'submitted', 'categories', 'journal_ref', 'url']
    return [dict(zip(columns, row)) for row in rows]
