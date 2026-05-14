#!/usr/bin/env python3
"""
AI News Digest | AI 新闻摘要
Aggregates tech/AI news from multiple sources into a beautiful HTML digest.

Sources:
- Reddit: r/programming, r/MachineLearning, r/artificial, r/LocalLLaMA
- GitHub: New trending repositories
- Hacker News: Top stories

Usage:
    python main.py                  # Generate today's digest
    python main.py --output today.html  # Custom output file
"""

import argparse
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path


def fetch_reddit(subreddit, limit=5):
    """Fetch hot posts from a subreddit"""
    try:
        req = urllib.request.Request(
            f'https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}',
            headers={'User-Agent': 'Lizer/1.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            return [
                {
                    'title': post['data']['title'],
                    'score': post['data']['score'],
                    'url': f"https://reddit.com{post['data']['permalink']}",
                    'source': f'r/{subreddit}'
                }
                for post in data['data']['children']
                if not post['data']['stickied']
            ][:limit]
    except Exception as e:
        print(f"Reddit {subreddit} error: {e}", file=sys.stderr)
        return []


def fetch_github_trending():
    """Fetch newly created GitHub repos with stars"""
    try:
        req = urllib.request.Request(
            'https://api.github.com/search/repositories?q=created:>2026-05-13&sort=stars&order=desc&per_page=5',
            headers={'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Lizer/1.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            return [
                {
                    'title': repo['full_name'],
                    'score': repo['stargazers_count'],
                    'url': repo['html_url'],
                    'description': repo['description'] or '',
                    'language': repo['language'] or 'Unknown',
                    'source': 'GitHub'
                }
                for repo in data.get('items', [])[:5]
            ]
    except Exception as e:
        print(f"GitHub error: {e}", file=sys.stderr)
        return []


def generate_html(digest_data, date_str):
    """Generate beautiful HTML digest"""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI News Digest | {date_str}</title>
    <style>
        :root {{
            --bg: #0d1117;
            --card: #161b22;
            --border: #30363d;
            --text: #c9d1d9;
            --accent: #58a6ff;
            --accent2: #f78166;
            --accent3: #3fb950;
            --muted: #8b949e;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 2rem; }}
        header {{
            text-align: center;
            padding: 2rem 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 2rem;
        }}
        header h1 {{
            font-size: 2rem;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        header .date {{ color: var(--muted); margin-top: 0.5rem; }}
        .section {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .section h2 {{
            font-size: 1.2rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border);
        }}
        .news-item {{
            padding: 0.8rem 0;
            border-bottom: 1px solid var(--border);
        }}
        .news-item:last-child {{ border-bottom: none; }}
        .news-item a {{
            color: var(--text);
            text-decoration: none;
            font-weight: 500;
        }}
        .news-item a:hover {{ color: var(--accent); }}
        .news-item .meta {{
            color: var(--muted);
            font-size: 0.85rem;
            margin-top: 0.3rem;
        }}
        .score {{
            display: inline-block;
            background: var(--accent);
            color: var(--bg);
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
            font-size: 0.75rem;
            margin-right: 0.5rem;
        }}
        footer {{
            text-align: center;
            padding: 2rem 0;
            color: var(--muted);
            border-top: 1px solid var(--border);
        }}
        footer a {{ color: var(--accent); text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📰 AI News Digest</h1>
            <div class="date">{date_str}</div>
        </header>
"""

    # Programming News
    if digest_data.get('programming'):
        html += """        <div class="section">
            <h2>💻 Programming | 编程</h2>
"""
        for item in digest_data['programming']:
            html += f"""            <div class="news-item">
                <span class="score">{item['score']}⭐</span>
                <a href="{item['url']}" target="_blank">{item['title']}</a>
                <div class="meta">{item['source']}</div>
            </div>
"""
        html += "        </div>\n"

    # AI/ML News
    if digest_data.get('ai_ml'):
        html += """        <div class="section">
            <h2>🤖 AI & Machine Learning | 人工智能</h2>
"""
        for item in digest_data['ai_ml']:
            html += f"""            <div class="news-item">
                <span class="score">{item['score']}⭐</span>
                <a href="{item['url']}" target="_blank">{item['title']}</a>
                <div class="meta">{item['source']}</div>
            </div>
"""
        html += "        </div>\n"

    # GitHub Trending
    if digest_data.get('github'):
        html += """        <div class="section">
            <h2>🚀 GitHub Trending | 热门仓库</h2>
"""
        for item in digest_data['github']:
            html += f"""            <div class="news-item">
                <span class="score">{item['score']}⭐</span>
                <a href="{item['url']}" target="_blank">{item['title']}</a>
                <div class="meta">{item['description'][:100] if item['description'] else ''} | {item['language']}</div>
            </div>
"""
        html += "        </div>\n"

    html += """        <footer>
            <p>🤖 Generated by <a href="https://github.com/LizerAIDev">Lizer AI Developer</a></p>
            <p style="margin-top: 0.5rem;">自主生成 | Autonomously Generated</p>
        </footer>
    </div>
</body>
</html>"""

    return html


def main():
    parser = argparse.ArgumentParser(description="AI News Digest Generator")
    parser.add_argument("--output", default="digest.html", help="Output HTML file")
    args = parser.parse_args()

    print("📰 Fetching news from multiple sources...")
    
    digest_data = {
        'programming': fetch_reddit('programming', 5),
        'ai_ml': fetch_reddit('artificial', 3) + fetch_reddit('LocalLLaMA', 3),
        'github': fetch_github_trending()
    }

    date_str = datetime.now().strftime("%Y-%m-%d")
    html = generate_html(digest_data, date_str)

    output_path = Path(args.output)
    output_path.write_text(html, encoding='utf-8')
    
    total = sum(len(v) for v in digest_data.values())
    print(f"✅ Digest generated: {output_path}")
    print(f"   {total} news items from {len(digest_data)} sources")


if __name__ == "__main__":
    main()
