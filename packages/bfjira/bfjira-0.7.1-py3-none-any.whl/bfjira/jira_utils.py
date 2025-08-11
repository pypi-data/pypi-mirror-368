"""JIRA utility functions."""

import logging
import re

from jira import JIRA

logger = logging.getLogger("bfjira")


def get_client(jira_server, jira_email, jira_api_token):
    """Initialize and return a JIRA client."""
    try:
        return JIRA(server=jira_server, basic_auth=(jira_email, jira_api_token))
    except Exception as e:
        logger.error(f"Error initializing JIRA client: {e}")
        raise


def branch_name(jira, ticket_id, issue_type_override=None):
    """Generate a branch name based on JIRA ticket information."""
    try:
        ticket = jira.issue(ticket_id)
        issue_type = ticket.fields.issuetype.name.lower()
        if issue_type == "story":
            branch_prefix = "feature"
        elif issue_type == "bug":
            branch_prefix = "fix"
        elif issue_type == "sub-task":
            branch_prefix = "task"
        else:
            branch_prefix = issue_type_override if issue_type_override else issue_type

        sanitized_summary = re.sub(
            r"[^a-zA-Z0-9-_]", "", ticket.fields.summary.replace(" ", "_")
        ).lower()
        branch_name = f"{branch_prefix}/{ticket_id}-{sanitized_summary}"
        return branch_name[:100]  # Truncate if longer than 100 characters
    except Exception as e:
        logger.error(f"Error generating branch name for ticket {ticket_id}: {e}")
        raise


def transition_to_in_progress(jira, ticket_id):
    """Transition the specified JIRA ticket to 'In Progress' status."""
    try:
        logger.debug(f"Transitioning ticket ID: {ticket_id}")
        transitions = jira.transitions(ticket_id)
        in_progress_transition = next(
            (t for t in transitions if t["name"].lower() == "in progress"), None
        )
        if in_progress_transition:
            jira.transition_issue(ticket_id, in_progress_transition["id"])
            logger.info(f"Ticket {ticket_id} transitioned to 'In Progress'.")
        else:
            logger.warning(f"No 'In Progress' transition found for ticket {ticket_id}.")
    except Exception as e:
        logger.error(f"Error transitioning ticket {ticket_id} to 'In Progress': {e}")
        raise
