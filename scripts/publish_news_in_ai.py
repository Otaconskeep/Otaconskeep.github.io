#!/usr/bin/env python3
"""Publish News in AI when the Keep's Home Current edition changes.

The public page is a built snapshot. This rebuilds it from the live edition
and pushes GitHub Pages. It commits only news/.
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
    build = subprocess.run(
        [sys.executable, str(ROOT / 'scripts' / 'build_news_in_ai.py')],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    sys.stdout.write(build.stdout)
    sys.stderr.write(build.stderr)
    if build.returncode != 0:
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
        'Publish the latest News in AI edition.\n\nThe Keep refreshed Home Current, so the public page follows it.',
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
    rebase = git('rebase', 'origin/main', check=False)
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
