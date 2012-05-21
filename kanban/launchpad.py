from datetime import datetime, timedelta
import os
import sys

# Uncomment this to see debug output showing the requests being made to
# Launchpad.
#
# import httplib2
# httplib2.debuglevel = 1

from lazr.restfulclient.errors import HTTPError

from launchpadlib.credentials import Credentials
from launchpadlib.launchpad import Launchpad
from launchpadlib.uris import LPNET_SERVICE_ROOT

from kanban.board import Bug


SERVICE_ROOT = LPNET_SERVICE_ROOT


def is_unauthorized(error):
    """True if error is HTTP 401 Unauthorized."""
    # See bug 735332 asking for this to be in lazr.restful instead.
    return error.response.status == 401


def is_forbidden(error):
    """True if error is HTTP 403 Forbidden."""
    # See bug 735332 asking for this to be in lazr.restful instead.
    return error.response.status == 403


def _make_path(path):
    """Ensure that C{path} exists in the current user's home directory."""
    path = os.path.join(os.environ["HOME"], path)
    config_path = os.path.join(path, "launchpadlib")
    if not os.path.exists(config_path):
        os.makedirs(config_path)
    return config_path


def get_config_path():
    """Get the path for configuration data."""
    return _make_path(".config/kanban")


def get_cache_path():
    """Get the path for cached data."""
    return _make_path(".cache/kanban")


def get_launchpad():
    """Get a Launchpad instance.

    @raise RuntimeError: Raised if credentials are not available.
    """
    credentials_path = os.path.join(get_config_path(), "credentials.txt")
    if not os.path.exists(credentials_path):
        raise RuntimeError(
            "Run the launchpad-login command to create OAuth credentials.")
    credentials = Credentials()
    credentials.load(open(credentials_path, "r"))
    return Launchpad(credentials, SERVICE_ROOT, get_cache_path())


def get_project_group(launchpad, name):
    """Get the project group called C{name} or C{None} if one doesn't exist.

    @param launchpad: A C{Launchpad} instance.
    @param name: The name of the project group.
    """
    result = launchpad.project_groups.search(text=name)
    for project in result:
        if project.name == name:
            return project
    return None


def get_project(launchpad, name):
    """Get the project called C{name} or C{None} if one doesn't exist.

    @param launchpad: A C{Launchpad} instance.
    @param name: The name of the project.
    """
    result = launchpad.projects.search(text=name)
    for project in result:
        if project.name == name:
            return project
    return None


def get_milestone(launchpad, project_name, milestone_name):
    """Get the milestone for the specified project.

    @param launchpad: A C{Launchpad} instance.
    @param project_name: The name of the Launchpad project the milestone
        belongs to.  Optionally, this can be a project group.
    @param milestone_name: The name of the milestone to fetch.
    """
    project_group = get_project_group(launchpad, project_name)
    if project_group:
        return _get_milestone(launchpad, project_group, milestone_name)

    project = get_project(launchpad, project_name)
    if project:
        return _get_milestone(launchpad, project, milestone_name)

    return None


def _get_milestone(launchpad, project, name):
    """Get the milestone called C{name} from C{project}.

    @param launchpad: A C{Launchpad} instance.
    @param project: A C{project} or C{project_group} instance from Launchpad.
    @param name: The name of the milestone to fetch.
    """
    for milestone in project.all_milestones_collection:
        if milestone.name == name:
            return milestone
    return None


RELEVANT_STATUSES = ["New", "Incomplete", "Expired", "Confirmed", "Triaged",
                     "In Progress", "Fix Committed", "Fix Released"]


def trace(message):
    """Write C{message} to stderr."""
    sys.stderr.write(unicode(message) + '\n')


def get_person_assigned_bugs(launchpad, person_name):
    """Get a C{list} of L{Bug}s assigned to C{person}.

    @param launchpad: A C{Launchpad} instance.
    @param person_name: The name of the person or team to fetch bugs for.
    """
    bug_set = set()
    person = launchpad.people[person_name]
    # Directly assigned bugs.
    bug_set.update(get_person_directly_assigned_bugs(launchpad, person))
    # If a team, get everyone transitively in the team.
    for member in person.participants:
        trace("check bugs for participant %s" % member)
        bug_set.update(get_person_directly_assigned_bugs(launchpad, member))
    return list(bug_set)


def get_person_directly_assigned_bugs(launchpad, person):
    """Generator yields L{Bug}s assigned to C{person}.

    @param launchpad: A C{Launchpad} instance.
    @param person: A C{person} instance from Launchpad.
    """
    for bug_task in person.searchTasks(status=RELEVANT_STATUSES,
                                       assignee=person):
        # It's nice to see fixed bugs for the sake of a sense of
        # accomplishment, but we don't want the kanban to get too big.
        trace(bug_task)
        if (bug_task.status == "Fix Released"):
            date_closed = bug_task.date_closed
            age = datetime.now(date_closed.tzinfo) - date_closed
            if (age > timedelta(days=31)):
                trace("fixed too long ago, omitting")
                continue
        yield _create_bug(bug_task)


def get_milestone_bugs(launchpad, project_name, milestone_name):
    """Get a C{list} of L{Bug}s from a milestone in Launchpad.

    @param launchpad: A C{Launchpad} instance.
    @param project_name: The name of the Launchpad project the milestone
        belongs to.  Optionally, this can be a project group.
    @param milestone_name: The name of the milestone to fetch.
    """
    bugs = []
    milestone = get_milestone(launchpad, project_name, milestone_name)
    for bug_task in milestone.searchTasks(status=RELEVANT_STATUSES):
        bugs.append(_create_bug(bug_task))
    return bugs


def _create_bug(bug_task):
    """Create a L{Bug} from a C{bug_task} instance loaded from Launchpad."""
    launchpad_bug = bug_task.bug
    assignee = bug_task.assignee
    in_progress_date = bug_task.date_in_progress

    if assignee is not None:
        assignee = assignee.name
    branch_url = None
    merge_proposal_url = None
    merge_proposal_status = None
    merge_proposal_creation_date = None
    try:
        for branch in launchpad_bug.linked_branches:
            launchpad_branch = branch.branch
            branch_url = launchpad_branch.bzr_identity
            for merge_proposal in launchpad_branch.landing_targets:
                merge_proposal_creation_date = merge_proposal.date_created
                merge_proposal_status = merge_proposal.queue_status
                merge_proposal_url = merge_proposal.web_link
                break
    except HTTPError, e:
        # Due to <http://pad.lv/735346>, at the moment bugs with
        # any private linked branches hide all of them and raise an error.
        if is_forbidden(e) or is_unauthorized(e):
            trace("Skipping forbidden or unauthorized linked branches")
            pass
        else:
            raise
    return Bug(launchpad_bug.id, bug_task.bug_target_name, bug_task.importance,
               bug_task.status, launchpad_bug.title, assignee,
               in_progress_date, branch_url, merge_proposal_url,
               merge_proposal_status, merge_proposal_creation_date,
               launchpad_bug.tags)
