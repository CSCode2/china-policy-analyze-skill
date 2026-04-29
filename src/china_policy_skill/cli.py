import argparse
import json
import os
import subprocess
import sys


def run_daily_update():
    cwd = os.getcwd()
    script = os.path.join(cwd, "scripts", "_run_daily_update.py")
    if not os.path.exists(script):
        print(f"Error: {script} not found. Run from the project root directory.", file=sys.stderr)
        sys.exit(1)
    os.execv(sys.executable, [sys.executable, script] + sys.argv[1:])


def wechat_search():
    from china_policy_skill.fetch.fetch_wechat import WeChatSearcher

    parser = argparse.ArgumentParser(prog="cpi wechat-search", description="Search WeChat public accounts for policy articles")
    parser.add_argument("query", help="Search keyword")
    parser.add_argument("--account", "-a", help="Search within a specific account (e.g. 中国人民银行)")
    parser.add_argument("--category", "-c", help="Search across accounts in a category (e.g. economy_finance)")
    parser.add_argument("--max", "-m", type=int, default=3, help="Max results (default: 3)")
    parser.add_argument("--fetch", "-f", action="store_true", help="Fetch full article content")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    ws = WeChatSearcher()

    if args.account:
        if args.fetch:
            articles = ws.search_by_account_and_fetch(args.account, keyword=args.query, max_results=args.max)
        else:
            articles = ws.search_by_account(args.account, keyword=args.query, max_results=args.max)
    elif args.category:
        if args.fetch:
            articles = ws.search_by_category_and_fetch(args.category, keyword=args.query, max_results=args.max)
        else:
            articles = ws.search_by_category(args.category, keyword=args.query, max_results=args.max)
    else:
        if args.fetch:
            articles = ws.search_and_fetch(args.query, max_results=args.max)
        else:
            articles = ws.search(args.query, max_results=args.max)

    if args.json:
        data = []
        for a in articles:
            item = {"title": a.title, "url": a.url, "abstract": a.abstract, "account": a.account_name}
            if a.markdown:
                item["markdown"] = a.markdown
            data.append(item)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for i, a in enumerate(articles, 1):
            acc = f" [{a.account_name}]" if a.account_name else ""
            print(f"\n--- Article {i}{acc} ---")
            print(f"Title:    {a.title}")
            print(f"URL:      {a.url}")
            print(f"Abstract: {a.abstract[:200]}")
            if a.markdown:
                preview = a.markdown[:2000]
                print(f"Content:  {preview}{'...' if len(a.markdown) > 2000 else ''}")
        if not articles:
            print("No articles found.")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: cpi <command> [options]")
        print()
        print("Commands:")
        print("  update          Run daily corpus update")
        print("  wechat-search   Search WeChat public accounts for policy articles")
        print()
        print("Run 'cpi wechat-search --help' for search options.")
        sys.exit(0)

    cmd = sys.argv[1]
    rest = sys.argv[2:]

    if cmd == "update":
        sys.argv = sys.argv[:1] + rest
        run_daily_update()
    elif cmd == "wechat-search":
        sys.argv = ["cpi wechat-search"] + rest
        wechat_search()
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print("Available commands: update, wechat-search", file=sys.stderr)
        sys.exit(1)
