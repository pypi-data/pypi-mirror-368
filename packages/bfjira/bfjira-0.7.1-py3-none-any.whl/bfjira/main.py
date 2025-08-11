#!/usr/bin/env python3

import argparse
import os
import sys
from importlib import metadata

try:
    CLI_VERSION = metadata.version("bfjira")
except metadata.PackageNotFoundError:
    from . import __version__ as CLI_VERSION


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Interact with JIRA and Git for branch management"
    )
    parser.add_argument("--ticket", "-t", help="The JIRA ticket ID (e.g., SRE-1234).")
    parser.add_argument(
        "--no-upstream",
        action="store_true",
        help="Do not set upstream for the new branch",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Increase output verbosity"
    )
    parser.add_argument(
        "--issue-type",
        help=(
            "Set the type of issue for the branch prefix, "
            "overrides default issue type detection"
        ),
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Do not transition the ticket to 'In Progress'",
    )
    parser.add_argument("--version", action="version", version=CLI_VERSION)

    args = parser.parse_args()

    from git import Repo
    from bfjira.git_utils import create_branch, pop_stash, stash_changes, to_git_root
    from bfjira.jira_utils import branch_name, get_client, transition_to_in_progress
    from bfjira.log_config import setup_logging

    logger = setup_logging(verbose=args.verbose)

    if not args.ticket:
        logger.error("No ticket ID provided.")
        parser.print_help()
        sys.exit(1)

    # Load JIRA configuration from environment variables
    jira_server = os.getenv("JIRA_SERVER")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_api_token = os.getenv("JIRA_API_TOKEN")
    jira_ticket_prefix = os.getenv("JIRA_TICKET_PREFIX", "SRE")

    if not all([jira_server, jira_email, jira_api_token]):
        logger.error(
            "JIRA_SERVER, JIRA_EMAIL, and JIRA_API_TOKEN "
            "environment variables must be set."
        )
        sys.exit(1)

    ticket_id = args.ticket
    if ticket_id.isnumeric():
        ticket_id = f"{jira_ticket_prefix}-{ticket_id}"

    # Initialize JIRA client
    jira = get_client(jira_server, jira_email, jira_api_token)

    # Generate branch name based on JIRA ticket
    generated_branch_name = branch_name(jira, ticket_id, args.issue_type)

    # Perform Git operations
    to_git_root()
    repo = Repo(".")
    needs_stash_pop = False

    if repo.is_dirty(untracked_files=True):
        logger.warning("Repository has uncommitted changes.")
        response = input("Do you want to stash them? (y/n): ").lower()
        if response == "y":
            if stash_changes():
                needs_stash_pop = True
            else:
                logger.error("Failed to stash changes. Exiting.")
                sys.exit(1)
        else:
            logger.info("Please commit or stash your changes manually. Exiting.")
            sys.exit(0)

    try:
        create_branch(generated_branch_name, not args.no_upstream)

        # Transition JIRA ticket to 'In Progress'
        if not args.no_progress:
            transition_to_in_progress(jira, ticket_id)
        else:
            logger.info(
                f"Ticket {ticket_id} not transitioned to 'In Progress' "
                "as per user request."
            )
    finally:
        if needs_stash_pop:
            pop_stash()


if __name__ == "__main__":
    main()
