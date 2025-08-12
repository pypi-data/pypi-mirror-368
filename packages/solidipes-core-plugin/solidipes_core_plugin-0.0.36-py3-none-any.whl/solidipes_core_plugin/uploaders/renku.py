import re
import subprocess

from git.exc import InvalidGitRepositoryError
from solidipes.uploaders.uploader import Uploader
from solidipes.utils.utils import get_git_repository, init_git_repository

RENKU_REMOTE_NAME = "renku"
RENKU_TEMPLATE_NAMES = ["solidipes", "jtcam"]
RENKU_TEMPLATES_REPO = "https://gitlab.com/dcsm/renku-templates.git"


class RenkulabUploader(Uploader):
    command = "renku"
    command_help = (
        "Upload study to Renku. Initialises a git repository if necessary, and copies template files to the study root"
        " directory."
    )

    def upload(self, args):
        main(args)

    def populate_arg_parser(self, parser):
        parser.description = self.command_help

        parser.add_argument(
            "remote_url",
            metavar="remote-url",
            nargs="?",
            default=None,
            help=(
                "URL of the remote repository to push to. Not needed if the repository has already been uploaded to"
                " Renku."
            ),
        )

        parser.add_argument(
            "template",
            nargs="?",
            default="solidipes",
            choices=RENKU_TEMPLATE_NAMES,
            help="Template to use for the Renku repository",
        )


def main(args):
    repo = init_git()

    if args.remote_url is not None:
        init_renku(args.template)
        add_remote(repo, args.remote_url)

    elif RENKU_REMOTE_NAME not in repo.remotes:
        print("Please provide a remote URL and template name.")
        return

    push(repo)

    session_link = get_session_link(repo)
    if session_link is not None:
        print(f"Session link: {session_link}")
    else:
        print("Please visit your hosting platform to start a session.")


def init_git():
    """Initialize git and create initial commit if necessary"""

    try:
        repo = get_git_repository()

    except InvalidGitRepositoryError:
        repo = init_git_repository()
        repo.git.checkout("main", b=True)
        repo.git.add(all=True)
        repo.index.commit("initial commit")

    return repo


def init_renku(template_name):
    subprocess.run([
        "renku",
        "init",
        "--template-source",
        RENKU_TEMPLATES_REPO,
        "--template-id",
        template_name,
    ])


def add_remote(repo, remote_url):
    if RENKU_REMOTE_NAME in repo.remotes:
        repo.delete_remote(RENKU_REMOTE_NAME)
    repo.create_remote(RENKU_REMOTE_NAME, remote_url)


def push(repo):
    print(f"Pushing to {repo.remotes[RENKU_REMOTE_NAME].url}")

    repo.git.push(RENKU_REMOTE_NAME)


def get_session_link(repo):
    remote_url = repo.remotes[RENKU_REMOTE_NAME].url

    if "renkulab.io" in remote_url:
        # Format: git@gitlab.renkulab.io:username/repo-name.git
        # or https://gitlab.renkulab.io/username/repo-name.git
        remote_url_pattern = re.compile(r"renkulab\.io[:/](.+)\.git$")
        remote_url_match = remote_url_pattern.search(remote_url)
        if remote_url_match is None:
            return None
        project_path = remote_url_match.group(1)
        return f"https://renkulab.io/projects/{project_path}/sessions/new?autostart=1"

    return None
