from datetime import datetime, timedelta

from jinja2 import Environment, PackageLoader

from kanban.board import MilestoneBoard


def branch_name(branch_url):
    """Extract and return the branch name from a branch URL."""
    return branch_url.split("/")[-1]


def branch_url(bug):
    """
    Return a URL for the branch or for its merge proposal, if one is
    available.
    """
    if bug.merge_proposal:
        return bug.merge_proposal
    else:
        return "https://code.launchpad.net/" + bug.branch[3:]


def importance_css_class(importance):
    """Convert an importance into a CSS class name."""
    return "%s-importance" % importance.lower()


def get_warn_date(start_date, age):
    """Get the warning date for this bug, if any."""
    while age:
        start_date += timedelta(days=1)
        if start_date.weekday() not in (5, 6):
            age -= 1
    return start_date


def warn(bug, in_progress_age, review_age, now=None):
    """Determine if C{bug} should have a warning badge shown for it.

    @param bug: A L{Bug} instance.
    @param in_progress_age: The number of days the bug must be in progress
        before a warning is shown.
    @param review_age: The number of days the bug must be in the review queue
        before a warning is shown.
    @param now: Optionally, the date to use when checking for warning status.
    """
    if bug.needs_review() and bug.merge_proposal_creation_date:
        now = now if now else datetime.now(
            bug.merge_proposal_creation_date.tzinfo)
        warn_date = get_warn_date(bug.merge_proposal_creation_date, review_age)
        return now > warn_date
    elif bug.in_progress() and bug.in_progress_date:
        now = now if now else datetime.now(bug.in_progress_date.tzinfo)
        warn_date = get_warn_date(bug.in_progress_date, in_progress_age)
        return now > warn_date
    return False


def generate_html(kanban_board):
    """Generate an HTML kanban board to represent L{Bug}s in C{milestone}."""
    environment = Environment(loader=PackageLoader("kanban", "templates"))
    environment.filters["branch_name"] = branch_name
    environment.filters["branch_url"] = branch_url
    environment.filters["importance_css_class"] = importance_css_class
    environment.filters["warn"] = lambda bug: warn(bug, 3, 1)
    environment.filters["danger"] = lambda bug: warn(bug, 7, 3)
    template = environment.get_template("kanban.html")
    data = {"kanban_board": kanban_board,
            "is_milestone": isinstance(kanban_board, MilestoneBoard),
            "now": datetime.utcnow().strftime("%a %e %b at %H:%M UTC")}
    return template.render(**data)


def status_css_class(status):
    """Convert a status into a CSS class name."""
    return "%s-status" % status.lower()


def generate_roadmap_html(roadmap):
    """Generate an HTML kanban board to represent a L{Roadmap}."""
    environment = Environment(loader=PackageLoader("kanban", "templates"))
    environment.filters["status_css_class"] = status_css_class
    template = environment.get_template("roadmap.html")

    width = 12 / len(roadmap.time_periods)

    headings = []
    for i, time_period in enumerate(roadmap.time_periods):
        position = i * width
        headings.append(
            {"css_class": "position-%d width-%d cell" % (position, width),
             "name": time_period.name,
             "count": len(time_period.stories),
             "time_span": "%s - %s" % (time_period.start_date.strftime("%b"),
                                       time_period.end_date.strftime("%b"))})

    tracks = []
    for track in roadmap.tracks:
        time_periods = []
        for i, time_period in enumerate(roadmap.time_periods):
            position = i * width
            time_periods.append(
                {"css_class": "position-%d width-%d cell" % (position, width),
                 "stories": time_period.get_stories_by_track(track)})
        tracks.append({"name": track, "time_periods": time_periods})

    data = {"roadmap": roadmap, "headings": headings, "tracks": tracks,
            "now": datetime.utcnow().strftime("%a %e %b at %H:%M UTC")}
    return template.render(**data)
