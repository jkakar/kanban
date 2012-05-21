import os

from bzrlib.commands import Command
from bzrlib.option import Option

from launchpadlib.launchpad import Launchpad

from kanban.board import MilestoneBoard, PersonBoard, compare_bugs
from kanban.html import generate_html, generate_roadmap_html
from kanban.launchpad import (
    get_config_path, get_cache_path, get_launchpad, get_milestone_bugs,
    get_person_assigned_bugs, SERVICE_ROOT)
from kanban.roadmap import load_roadmap


class cmd_launchpad_login(Command):
    """Create an OAuth token to use with Launchpad commands.

    An OAuth token is required by commands that use launchpadlib.  Run this
    command to create an OAuth token, if you haven't already done so.  The
    token will be saved in ~/.cache/kanban/launchpadlib in a file called
    credentials.txt.  See https://help.launchpad.net/API for more information
    about launchpadlib.
    """

    def run(self):
        credentials_path = os.path.join(get_config_path(), "credentials.txt")
        if os.path.exists(credentials_path):
            raise RuntimeError(
                "Credentials already exist at %s" % credentials_path)
        launchpad = Launchpad.get_token_and_login(
            "kanban", SERVICE_ROOT, get_cache_path())
        launchpad.credentials.save(open(credentials_path, "w"))


class HTMLOutputMixin(Command):

    def write_output(self, html, output_file=None):
        """
        Write HTML output to C{output_file}, if supplied, or to the command's
        output stream.
        """
        if output_file is None:
            self.outf.write(html)
        else:
            with open(output_file, "w") as stream:
                stream.write(html.encode('utf-8'))


class cmd_generate_person_kanban(HTMLOutputMixin, Command):
    """Print an HTML kanban board for a person or team to the screen.

    The page shows bugs that are either open or were fixed within the last
    month, that are directly assigned to the named person.  If a team is
    provided the bugs shown will be for members of that team.
    """

    takes_args = ["person_name"]
    takes_options = [Option("output-file", short_name="o", type=str,
                            help="Write HTML to file."),
                     Option("include-needs-testing",
                            help="Include the 'Needs testing' category.")]
    _see_also = ["launchpad-login"]

    def run(self, person_name, output_file=None, include_needs_testing=None):
        launchpad = get_launchpad()
        person_board = PersonBoard(person_name,
                                   include_needs_testing=include_needs_testing)
        bugs = get_person_assigned_bugs(launchpad, person_name)
        for bug in sorted(bugs, compare_bugs):
            person_board.add(bug)
        self.write_output(generate_html(person_board), output_file)


class cmd_generate_milestone_kanban(HTMLOutputMixin, Command):
    """Print an HTML kanban board for a milestone to the screen."""

    takes_args = ["project_group", "milestone_name"]
    takes_options = [Option("output-file", short_name="o", type=str,
                            help="Write HTML to file."),
                     Option("include-needs-testing",
                            help="Include the 'Needs testing' category.")]
    _see_also = ["launchpad-login"]

    def run(self, project_group, milestone_name, output_file=None,
            include_needs_testing=None):
        launchpad = get_launchpad()
        milestone_board = MilestoneBoard(
            project_group, milestone_name,
            include_needs_testing=include_needs_testing)
        bugs = get_milestone_bugs(launchpad, project_group, milestone_name)
        for bug in sorted(bugs, compare_bugs):
            milestone_board.add(bug)
        self.write_output(generate_html(milestone_board), output_file)


class cmd_generate_roadmap(HTMLOutputMixin, Command):
    """Print an HTML kanban board for a roadmap to the screen.

    The JSON document should match the following format::

      {'project': '<launchpad-project-name>',
       'time_periods': [
           {'name': '<time-period-name>',
            'start_date': '<YYYY-MM-DD>',
            'end_date': '<YYYY-MM-DD>',
            'stories': [
                {'name': '<task-name>',
                 'description': '<task-description>',
                 'track': '<task-track>',
                 'status': '<Queued|Active|Done>',
                 'link': '<url>',
                 'assignees': ['<assignee>', ...]},
                ...]},
           ...]}

    The 'link' and 'assignees' fields are optional.
    """

    takes_args = ["roadmap_json_path"]
    takes_options = [Option("output-file", short_name="o", type=str,
                            help="Write HTML to file.")]

    def run(self, roadmap_json_path, output_file=None):
        with open(roadmap_json_path, "r") as file:
            json = file.read()
        roadmap = load_roadmap(json)
        self.write_output(generate_roadmap_html(roadmap), output_file)
