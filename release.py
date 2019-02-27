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
from buzio import console
from git import InvalidGitRepositoryError, Repo
from jinja2 import Template

CHANGELOG_TEMPLATE = """
## {{ release.version }} ({{ release.date }})
{% if has_commits %}
{% for prefix in prefixes %}
### {{ prefix.title() }}
{% for commit in commits %}
* [commit.hash]({{ git_url }}/{{ commit.hash }}) {{ commit.subject.replace(prefix, "") }} [{{ commit.author }}]
{% endfor %}
{% endfor %}
{% else %}
_No conventional commits was founded._

*Last commit*: {{ lasts_commit }}
{% endif %}

"""


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
        self.repo = get_repo()

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

    def master(self):
        pass

    def release(self):
        """Make Release.

        :return: None
        """
        commits = self.get_commits()
        if commits:
            template = Template(CHANGELOG_TEMPLATE)
            context = {
                'release': {
                    "version": "0.0.1",
                    "data": arrow.utcnow().format("%d-%m-%Y")
                },
                'commits': commits,
                'git_url': next(self.repo.remotes[0].urls),
                'prefixes': self.prefixes if not commits['breaking_change']
                else self.prefixes.insert(0, 'Breaking Changes:')
            }
            body = template.render(context)
            print(body)

    def get_commits(self):
        commit_raw_list = console.run('git log origin/master.. --format="%h#%an#%ai#%s" | grep -P "[^$]"',
                                      get_stdout=True)
        commits = {
            key: []
            for key in self.prefixes
        }
        breaking = False
        has_commits = False
        first_commit_subject = None
        if commit_raw_list:
            all_commits = commit_raw_list.split("\n")
            for data in all_commits:
                if not "#" in data:
                    continue
                hash = data.split("#")[0]
                author = data.split("#")[1]
                date = data.split("#")[2] # arrow.get(data.split("#")[2]).date()
                subject = data.split("#")[3]
                prefix = self.get_prefix(subject) or "other:"
                breaking = "BREAKING CHANGE" in subject
                if not first_commit_subject:
                    first_commit_subject = "{} ({}) [{}]".format(subject, date, author)
                if prefix:
                    has_commits = True
                    commits[prefix].append({
                        "hash": hash,
                        "author": author,
                        "date": date,
                        "subject": subject,
                        "breaking": breaking
                    })
        commits['breaking_change'] = breaking
        commits['has_commits'] = has_commits
        commits['last_commit'] = first_commit_subject
        return commits

    def hotfix(self):
        pass

    def execute(self):
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
