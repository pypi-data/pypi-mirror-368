"""Provides an interface to run the checks directly, without any proxy Python code."""

import logging
import os
import pickle
import sys
from collections.abc import Callable
from pathlib import Path

from configargparse import ArgumentParser

from github_checks.formatters.check_jsonschema import format_jsonschema_check_run_output
from github_checks.formatters.mypy import format_mypy_check_run_output
from github_checks.formatters.raw import format_raw_check_run_output
from github_checks.formatters.ruff import format_ruff_check_run_output
from github_checks.formatters.sarif import format_sarif_check_run_output
from github_checks.github_api import GitHubChecks
from github_checks.models import CheckRunConclusion, CheckRunOutput

LOG_OUTPUT_FORMATTERS: dict[
    str,
    Callable[
        [Path, Path, list[str] | None, bool],
        tuple[CheckRunOutput, CheckRunConclusion],
    ],
] = {
    "check-jsonschema": format_jsonschema_check_run_output,
    "ruff-json": format_ruff_check_run_output,
    "mypy-json": format_mypy_check_run_output,
    "sarif": format_sarif_check_run_output,
    "raw": format_raw_check_run_output,
}


def unpickle(pickle_fp: Path, err_msg: str) -> GitHubChecks | None:
    """Attempt to read the current checks session from the pickle file."""
    if not pickle_fp.exists():
        logging.fatal(err_msg)
        return None
    with args.pickle_filepath.open("rb") as pickle_file:
        return pickle.load(pickle_file)  # noqa: S301


if __name__ == "__main__":
    argparser = ArgumentParser(
        prog="github-checks",
        description="CLI for the github-checks library. Please note: the commands of "
        "this CLI need to be used in a specific order (see individual command help for "
        "details) and pass values to each other through environment variables.",
    )
    argparser.add_argument(
        "--pickle-filepath",
        type=Path,
        default=Path("/tmp/github-checks.pkl"),  # noqa: S108
        help="File in which the authenticated checks session will be cached.",
    )
    subparsers = argparser.add_subparsers(
        description="Operation to be performed by the CLI.",
        required=True,
        dest="command",
    )
    init_parser = subparsers.add_parser(
        "init",
        help="Authenticate this environment as a valid check run session for the GitHub"
        " App installation, retrieving an app token to authorize subsequent check run "
        "orchestration actions. This will store an authenticated GitHub checks session"
        "in the file configured in `--pickle-filepath`.",
    )
    init_parser.add_argument(
        "--app-id",
        type=str,
        env_var="GH_APP_ID",
        help="ID of the GitHub App that is authorized to orchestrate Check Runs.",
    )
    init_parser.add_argument(
        "--pem-path",
        type=Path,
        env_var="GH_PRIVATE_KEY_PEM",
        help="Private key to authenticate as the GitHub App specified in --app-id.",
    )
    init_parser.add_argument(
        "--repo-base-url",
        type=str,
        env_var="GH_REPO_BASE_URL",
        help="Base URL of the repo with scheme, e.g. https://github.com/jdoe/myproject.",
    )
    init_parser.add_argument(
        "--app-install-id",
        type=str,
        env_var="GH_APP_INSTALL_ID",
        help="ID of the repository's GitHub App installation used by the check.",
    )
    init_parser.add_argument(
        "--overwrite-existing",
        action="store_true",
        help="If an existing checks session is found (pickle file exists), overwrite it"
        ". If a session is found and this is not set, initialization will abort.",
    )

    clone_parser = subparsers.add_parser(
        "clone-repo",
        help="Clone the configured repository to a local folder, using the app's "
        "same initialized session as is used for the Checks API. Only requires that the"
        "app installation has repository read permissions, can be useful to avoid "
        "separate authenticated cloning mechanism (e.g. through deploy keys). Requires "
        "git to be installed on this system, such that `git clone` can be used.",
    )
    clone_parser.add_argument(
        "--revision",
        type=str,
        env_var="GH_CHECK_REVISION",
        default="master",
        help="Revision/commit SHA hash that should be checked out. If not specified, "
        "the repository default revision is checked out, usually master/main HEAD.",
    )
    clone_parser.add_argument(
        "--local-repo-path",
        type=Path,
        env_var="GH_LOCAL_REPO_PATH",
        help="Path to the local folder to clone the repository to. If not used, no "
        "path is passed to the `git clone` command, thus defaulting to a folder by the "
        "repos's name within the current working directory.",
    )

    start_parser = subparsers.add_parser(
        "start-check-run",
        help="Start a check run for a specific commit/revision hash, using the "
        "current initialized session. Will show up in GitHub PRs as a running check.",
    )
    start_parser.add_argument(
        "--revision",
        type=str,
        env_var="GH_CHECK_REVISION",
        help="Revision/commit SHA hash that this check run is validating.",
    )
    start_parser.add_argument(
        "--check-name",
        type=str,
        env_var="GH_CHECK_NAME",
        help="A name for this check run. Will be shown on any respective GitHub PRs.",
    )

    finish_parser = subparsers.add_parser(
        "finish-check-run",
        help="Finish the currently running check run, posting all the check annotations"
        ", the surrounding summary output and the appropriate check conclusion.",
    )
    finish_parser.add_argument(
        "validation_log",
        type=Path,
        help="Logfile of a supported format (see option --format for details).",
    )
    finish_parser.add_argument(
        "--log-format",
        choices=LOG_OUTPUT_FORMATTERS.keys(),
        required=True,
        help="Format of the provided log file.",
    )
    finish_parser.add_argument(
        "--local-repo-path",
        type=Path,
        env_var="GH_LOCAL_REPO_PATH",
        required=True,
        help="Path to the local copy of the repository, for deduction of relative paths"
        " by the formatter, for any absolute paths contained in the logfile.",
    )
    finish_parser.add_argument(
        "--conclusion",
        choices=CheckRunConclusion,
        required=False,
        help="Optional override for the conclusion this check run should finish with."
        "If not provided, success/action_required are used, depending on annotations.",
    )
    finish_parser.add_argument(
        "--checksignore-filepath",
        type=Path,
        help="File containing a list of file patterns to ignore for check annotations "
        "and the check verdict. Useful to incrementally introduce checks to an existing"
        " codebase, where some files are not yet compliant with the checks.",
    )
    finish_parser.add_argument(
        "--checksignore-verdict-only",
        action="store_true",
        help="If set, only the check verdict will be affected by the checksignore file,"
        "but annotations will still be generated for these files.",
    )
    subparsers.add_parser(
        "cleanup",
        help="Clean up the local environment variables and"
        " the pickle file, if present. Recommended to use if you don't"
        " plan to run another checks run in this environment. Otherwise, sensitive"
        " information is left on the local file system (e.g. access token), which can"
        " pose a security risk.",
    )
    args = argparser.parse_args(sys.argv[1:])
    gh_checks: GitHubChecks

    if args.command == "init":
        os.environ["GH_REPO_BASE_URL"] = args.repo_base_url

        if args.pickle_filepath.exists() and not args.overwrite_existing:
            logging.fatal(
                "[github-checks] Trying to initialize GitHub checks, but an instance "
                "is already initialized (pickle file exists) and `--overwrite-existing`"
                " is not set. Aborting.",
            )
            sys.exit(-1)

        gh_checks = GitHubChecks(
            repo_base_url=args.repo_base_url,
            app_id=args.app_id,
            app_installation_id=args.app_install_id,
            app_privkey_pem=args.pem_path,
        )
        with args.pickle_filepath.open("wb") as pickle_file:
            pickle.dump(gh_checks, pickle_file)

    if args.command == "clone-repo":
        if not (
            gh_checks := unpickle(
                args.pickle_filepath,
                "[github-checks] Trying to clone a repo without initialization "
                "(pickle file not found). Aborting.",
            )
        ):
            sys.exit(-1)
        if args.local_repo_path.is_dir() and any(args.local_repo_path.iterdir()):
            logging.fatal(
                "[github-checks] Local repository path exists and contains "
                "files. Aborting to avoid overwriting important files.",
            )
            sys.exit(-1)
        gh_checks.clone_repo(args.revision, args.local_repo_path)
        # don't need to dump the pickle file, as we've only read from the session

    if args.command == "start-check-run":
        if not (
            gh_checks := unpickle(
                args.pickle_filepath,
                "[github-checks] Trying to start a github check without "
                "initialization (pickle file not found). Aborting.",
            )
        ):
            sys.exit(-1)

        gh_checks.start_check_run(
            revision_sha=args.revision,
            check_name=args.check_name,
        )
        with args.pickle_filepath.open("wb") as pickle_file:
            pickle.dump(gh_checks, pickle_file)

    elif args.command == "finish-check-run":
        if not Path(args.local_repo_path).exists():
            logging.fatal(
                "[github-checks] Cannot find local repository copy for resolution "
                "of relative paths. Aborting.",
            )
            sys.exit("-1")
        if not (
            gh_checks := unpickle(
                args.pickle_filepath,
                "[github-checks] Error: Trying to update a github check, but no check "
                "is currently running. Quitting.",
            )
        ):
            sys.exit(-1)

        with args.pickle_filepath.open("rb") as pickle_file:
            gh_checks = pickle.load(pickle_file)  # noqa: S301

        ignored_globs: list[str] | None = None
        if args.checksignore_filepath and args.checksignore_filepath.exists():
            with args.checksignore_filepath.open("r", encoding="utf-8") as ignore_file:
                ignored_globs = ignore_file.readlines()

        check_run_output: CheckRunOutput
        check_run_conclusion: CheckRunConclusion
        check_run_output, check_run_conclusion = LOG_OUTPUT_FORMATTERS[args.log_format](
            Path(args.validation_log),
            Path(args.local_repo_path),
            ignored_globs,
            args.checksignore_verdict_only,
        )
        if args.conclusion:
            # override if present
            check_run_conclusion = CheckRunConclusion(args.conclusion)

        gh_checks.finish_check_run(check_run_conclusion, check_run_output)

    elif args.command == "cleanup":
        # delete the pickle file, the config won't be needed anymore
        if args.pickle_filepath.exists():
            args.pickle_filepath.unlink()

        # delete all environment variables for good measure
        for env_var in [
            "GH_APP_ID",
            "GH_APP_INSTALL_ID",
            "GH_PRIVATE_KEY_PEM",
            "GH_REPO_BASE_URL",
            "GH_CHECK_REVISION",
            "GH_CHECK_NAME",
        ]:
            os.environ.pop(env_var, default=None)
