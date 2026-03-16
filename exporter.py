import os
import subprocess
from datetime import datetime
from config import REPORTS_DIR, REPO_DIR

SEP = '=' * 80
DIV = '-' * 80


def format_paper(paper):
    journal = paper.get('journal_ref') or 'Preprint (not yet published)'
    lines = [
        SEP,
        f"[{paper['arxiv_id']}] {paper['title']}",
        SEP,
        f"Area     : {paper['categories']}",
        f"Date     : {paper['submitted']}",
        f"Authors  : {paper['authors']}",
        f"Journal  : {journal}",
        f"URL      : {paper['url']}",
        "",
        "Abstract:",
        f"  {paper['abstract']}",
        "",
        DIV,
    ]
    return '\n'.join(lines)


def write_report(papers, filename):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filepath = os.path.join(REPORTS_DIR, filename)

    header_lines = [
        "arxiv Paper Report",
        f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Papers    : {len(papers)}",
        SEP,
        "",
    ]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(header_lines) + '\n')
        for paper in papers:
            f.write(format_paper(paper) + '\n')

    print(f"Report written: {filepath}")
    return filepath


def git_push(filepath, message):
    rel = os.path.relpath(filepath, REPO_DIR)
    try:
        subprocess.run(['git', '-C', REPO_DIR, 'add', rel], check=True)
        subprocess.run(['git', '-C', REPO_DIR, 'commit', '-m', message], check=True)
        subprocess.run(['git', '-C', REPO_DIR, 'push'], check=True)
        print(f"Pushed to GitHub: {rel}")
    except subprocess.CalledProcessError as e:
        print(f"Git error (push skipped): {e}")


def export_and_push(papers, filename, commit_message):
    filepath = write_report(papers, filename)
    git_push(filepath, commit_message)
    return filepath
