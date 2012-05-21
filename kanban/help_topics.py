from commandant.help_topics import DocstringHelpTopic


class topic_tutorial(DocstringHelpTopic):
    """A tutorial.

    Project goals
    =============

    Kanban has some explicit design goals:

     * High-level overview: we want a kanban-esque view of a project at
       roadmap and milestone levels so that we can easily see what's going on.

     * Zero intervention: other than creating bugs and branches and using the
       tools in Launchpad to represent and manage state as part of the normal
       development process, no additional effort should be required to
       maintain a kanban board.

     * Uncomplicated: the board must useful, but as simple as possible, so
       that it isn't overwhelming to look at.


    Using Kanban
    ============

    Kanban has a simple frontend to authenticate with Launchpad and generate
    HTML kanban boards for roadmaps and milestones for projects and project
    group in Launchpad.

    Authenticating with Launchpad
    -----------------------------

    Before you can generate a kanban board you need to authenticate with
    Launchpad.

      $ bin/kanban launchpad-login

    This will create OAuth credentials in $HOME/.config/kanban.  In addition,
    Kanban will cache data in $HOME/.cache/kanban.  You should grant Kanban
    read-only access to Launchpad because it never performs writes.

    Generating a kanban board
    -------------------------

    Once you've authenticated Kanban with Launchpad you're ready to generate
    an HTML kanban board for your project.  You can generate various different
    kanban views, depending on how your project manages its work.

    To see the bugs targetted to the 0.19 milestone of storm::

      $ bin/kanban generate-milestone-kanban storm 0.19 > kanban.html

    To see all bugs assigned to a particular person, including bugs 'Fix
    released' in the last month::

      $ bin/kanban generate-person-kanban mbp > kanban.html

    About bug categories:

      The kanban board assumes a set of bug categories: queued, in progress,
      needs review, needs testing, verified and released.  Each category is
      represented as a column on the kanban board.  With the exception of the
      verified category, they can each be determined from Launchpad state
      alone.  When a bug has been tested and confirmed to work, it will be put
      in the verified category when it has the 'verified' tag.

    About story lanes:

      A high-level overview of a roadmap or milestone is useful, but stories
      and bugs are not isolated from each other.  In many cases, a small
      collection of bugs represent the changes needed to realize a complete
      feature.  Bugs with 'story-<name>' tags are grouped into lanes, to show
      the progress of related bugs.  Using these tags is optional.

    Generating a roadmap
    --------------------

    A roadmap can be generated with a JSON input document matching this
    format::

      {'project': '<launchpad-project-name>',
       'time_periods': [
           {'name': '<time-period-name>',
            'start_date': '<YYYY-MM-DD>',
            'end_date': '<YYYY-MM-DD>',
            'stories': [
                {'name': '<story-name>',
                 'description': '<story-description>',
                 'track': '<story-track>',
                 'status': '<Queued|Active|Done>',
                 'link': '<url>',
                 'assignees': ['<assignee>', ...]},
                ...]},
           ...]}

    The link field for a story is optional.  A roadmap can be generated from a
    file:

      $ bin/kanban generate-roadmap roadmap.json > roadmap.html

    Each time period specified in the roadmap document will be represented as
    a column on the kanban board.  Stories are grouped into track lanes, but
    otherwise presented in the order they appear in the file.

    About tracks:

      A track is a major focus area in a roadmap.  Stories in the same track
      are grouped into lanes.

    About stories:

      A story represents a significant piece of work on a roadmap.  Stories
      are rendered as tiles on the roadmap.
    """
