"""Release module.

Branch Develop
--------------
    * Do nothing

Branch Release or Hotfix
--------------
    1. Get git diff between master and release
    2. Select only conventional commits
    3. Define next version number
    4. Save current log in CI's cache.

Branch Master
-------------
    1. Get cache from CI
    2. Update changelog.md with cached log
    3. Send cached log to Gihtub Release
    4. Merge data in develop
"""
import sys
from typing import Optional

import arrow
import semver
from buzio import console
from git import InvalidGitRepositoryError, Repo
from jinja2 import Template

from megalus import __version__, version_data


def get_repo() -> Repo:
    """Return Git Repo object.

    :return: Repo instance
    """
    try:
        return Repo('.')
    except InvalidGitRepositoryError:
        console.error('No git found.')
        sys.exit(1)


class Release:
    """Release main class."""

    prefixes = ['feat:', 'fix:', 'chore:', 'docs:', 'style:', 'refactor:', 'perf:', 'test:', 'other:']

    def __init__(self):
        self.major_release = False
        self.repo = get_repo()
        self.commits = {}

    def get_prefix(self, subject: str) -> Optional[str]:
        """Check if subject is a conventional commit.

        :param subject: commit subject
        :return: string
        """
        for prefix in self.prefixes:
            if prefix in subject:
                return prefix

    @property
    def branch(self) -> str:
        """Return active branch name.

        :return: str
        """
        return self.repo.active_branch.name

    @staticmethod
    def get_template():
        """Get jinja template for Changelog.

        :return: File read.
        """
        with open("CHANGELOG.jinja2") as file:
            return file.read()

    def release(self):
        """Make Release.

        :return: None
        """
        if self.commits:
            template = Template(self.get_template())
            context = {
                'release': {
                    "version": f"{self.get_release_type()} {self.get_next_version()}",
                    "date": arrow.utcnow().format("YYYY-MM-DD")
                },
                'commits': self.commits,
                'prefixes': self.prefixes,
                'has_commits': True,
                'git_url': next(self.repo.remotes[0].urls)
            }
            body = template.render(context)
            print(body)

    def get_release_type(self):
        """Return Release Title

        :return: string
        """
        branch = self.repo.active_branch.name
        if branch in ['master', 'hotfix']:
            return "Hotfix"
        else:
            return "Release"

    def get_next_version(self):
        """Return SemVer next version.

        :return: string
        """
        current_token = "beta" if version_data['beta'] else None
        if current_token:
            return semver.bump_prerelease(__version__)
        if self.major_release:
            return semver.bump_major(__version__)
        elif len(self.commits['feat:']) > 0:
            return semver.bump_minor(__version__)

    def get_commits(self):
        """Get commits from git.

        :return: list
        """

        def _parse_commit(commit: str) -> dict:
            data = commit.split("#")
            return {
                "hash": data[0],
                "author": data[1],
                "date": arrow.get(data[2], "YYYY-MM-DD HH:mm:ss Z").format("YYYY-MM-DD"),
                "subject": data[3].replace(prefix, "").strip(),
                "prefix": self.get_prefix(data[3])
            }

        commit_raw_list = console.run('git log origin/master.. --format="%h#%an#%ai#%s" | grep -P "[^$]"',
                                      get_stdout=True)
        if "BREAKING CHANGE" in commit_raw_list:
            self.major_release = True
        commits_per_prefix = {}
        for prefix in self.prefixes:
            all_commits = commit_raw_list.split("\n")
            commits_per_prefix[prefix] = [
                _parse_commit(commit)
                for commit in all_commits
                if "#" in commit and prefix in commit.split("#")[3]
            ]
        self.commits = commits_per_prefix

    def execute(self):
        """Execute command."""
        self.get_commits()
        self.release()


def main() -> None:
    """Main code.

    :return: None
    """
    release = Release()

    if release.branch not in ['master', 'hotfix', 'release', 'develop']:
        console.info('Branch not allowed: {}. Skipping...'.format(release.branch))
        sys.exit(0)

    release.execute()


if __name__ == "__main__":
    main()
