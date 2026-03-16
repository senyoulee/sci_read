import argparse
from datetime import datetime, timezone
from fetcher import fetch_daily, fetch_backfill
from storage import init_db, save_papers, search_papers
from exporter import export_and_push


def cmd_fetch(args):
    print("Fetching recent papers from arxiv...")
    papers = fetch_daily()
    new_papers = save_papers(papers)
    print(f"Saved {len(new_papers)} new papers (out of {len(papers)} fetched)")

    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    filename = f"daily_{today}.txt"
    export_and_push(papers, filename, f"[arxiv] Daily report {today}")


def cmd_backfill(args):
    period = args.period
    print(f"Starting backfill for period: {period}")
    papers = fetch_backfill(period)
    new_papers = save_papers(papers)
    print(f"Saved {len(new_papers)} new papers (out of {len(papers)} fetched)")

    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    filename = f"backfill_{period}_{today}.txt"
    export_and_push(papers, filename, f"[arxiv] Backfill {period} report {today}")


def cmd_search(args):
    results = search_papers(
        keyword=args.keyword,
        author=args.author,
        category=args.category,
        date_from=args.date_from,
        date_to=args.date_to,
    )
    print(f"Found {len(results)} papers")

    ts = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    parts = []
    if args.keyword:
        parts.append(args.keyword.replace(' ', '_'))
    if args.author:
        parts.append(args.author.replace(' ', '_'))
    if args.category:
        parts.append(args.category)
    label = '_'.join(parts) if parts else 'search'

    filename = f"search_{label}_{ts}.txt"
    export_and_push(results, filename, f"[arxiv] Search: {label} {ts}")


def main():
    init_db()

    parser = argparse.ArgumentParser(description='arxiv Paper Gatherer for hep-lat, hep-th, hep-ex')
    sub = parser.add_subparsers(dest='command')

    # fetch
    sub.add_parser('fetch', help="Fetch today's new papers and export daily report")

    # backfill
    p_back = sub.add_parser('backfill', help='Backfill historical papers')
    p_back.add_argument('--period', choices=['1y', '6m', '3m'], required=True,
                        help='How far back to fetch')

    # search
    p_search = sub.add_parser('search', help='Search stored papers and export results')
    p_search.add_argument('--keyword', help='Search in title and abstract')
    p_search.add_argument('--author', help='Filter by author name')
    p_search.add_argument('--category', choices=['hep-lat', 'hep-th', 'hep-ex'],
                          help='Filter by category')
    p_search.add_argument('--date-from', dest='date_from', metavar='YYYY-MM-DD',
                          help='Start date')
    p_search.add_argument('--date-to', dest='date_to', metavar='YYYY-MM-DD',
                          help='End date')

    args = parser.parse_args()

    if args.command == 'fetch':
        cmd_fetch(args)
    elif args.command == 'backfill':
        cmd_backfill(args)
    elif args.command == 'search':
        cmd_search(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
