#!/usr/bin/env python3
"""Publish every news desk when the Keep's editions change.

Builds AI & Homelab, Systems Engineering, and the News hub (which reads
both desks' archives for its latest-story previews) in that order, then
commits and pushes whatever under news/ actually changed. It commits
only news/.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = {
    **os.environ,
    'GIT_AUTHOR_NAME': 'Antonio G. Garcia',
    'GIT_AUTHOR_EMAIL': '230031249+Otaconskeep@users.noreply.github.com',
    'GIT_COMMITTER_NAME': 'Antonio G. Garcia',
    'GIT_COMMITTER_EMAIL': '230031249+Otaconskeep@users.noreply.github.com',
}

BUILDERS = ('build_news_in_ai.py', 'build_news_se.py', 'build_news_hub.py')


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ['git', *args],
        cwd=ROOT,
        env=ENV,
        text=True,
        capture_output=True,
        check=check,
    )


def main() -> int:
    for script in BUILDERS:
        build = subprocess.run(
            [sys.executable, str(ROOT / 'scripts' / script)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        sys.stdout.write(build.stdout)
        sys.stderr.write(build.stderr)
        if build.returncode != 0:
            print(f'{script} failed, stopping')
            return build.returncode

    names = git('status', '--porcelain', '--', 'news').stdout.splitlines()
    paths = []
    for line in names:
        path = line[3:].strip()
        if path.startswith('news/'):
            paths.append(path)
    if not paths:
        print('news unchanged')
        return 0

    git('add', '--', 'news')
    commit = git(
        'commit',
        '-m',
        'Publish the latest news editions.\n\nThe Keep refreshed its editions, so the public pages follow.',
        check=False,
    )
    sys.stdout.write(commit.stdout)
    sys.stderr.write(commit.stderr)
    if commit.returncode != 0:
        return commit.returncode
    fetch = git('fetch', 'origin', check=False)
    sys.stdout.write(fetch.stdout)
    sys.stderr.write(fetch.stderr)
    if fetch.returncode != 0:
        return fetch.returncode
    # Other work in this checkout must not block the news push.
    rebase = git('rebase', '--autostash', 'origin/main', check=False)
    sys.stdout.write(rebase.stdout)
    sys.stderr.write(rebase.stderr)
    if rebase.returncode != 0:
        git('rebase', '--abort', check=False)
        return rebase.returncode
    push = git('push', 'origin', 'HEAD:main', check=False)
    sys.stdout.write(push.stdout)
    sys.stderr.write(push.stderr)
    return push.returncode


if __name__ == '__main__':
    raise SystemExit(main())
