# Bug status states
NEW = "New"
INCOMPLETE = "Incomplete"
OPINION = "Opinion"
INVALID = "Invalid"
WONT_FIX = "Won't Fix"
EXPIRED = "Expired"
CONFIRMED = "Confirmed"
TRIAGED = "Triaged"
IN_PROGRESS = "In Progress"
FIX_COMMITTED = "Fix Committed"
FIX_RELEASED = "Fix Released"


# Bug importance states
CRITICAL = "Critical"
HIGH = "High"
MEDIUM = "Medium"
LOW = "Low"
WISHLIST = "Wishlist"
UNDECIDED = "Undecided"
IMPORTANCE_ORDER = [CRITICAL, HIGH, MEDIUM, LOW, WISHLIST, UNDECIDED]


# Merge proposal states
WORK_IN_PROGRESS = "Work in progress"
NEEDS_REVIEW = "Needs review"
APPROVED = "Approved"
REJECTED = "Rejected"
MERGED = "Merged"
MERGED_FAILED = "Code failed to merge"
QUEUED = "Queued"
SUPERSEDED = "Superseded"


class Bug(object):
    """A bug represents a work item."""

    def __init__(self, id, project, importance, status, title, assignee=None,
                 in_progress_date=None, branch=None, merge_proposal=None,
                 merge_proposal_status=None, merge_proposal_creation_date=None,
                 tags=None):
        self.id = id
        self.project = project
        self.importance = importance
        self.status = status
        self.title = title
        self.assignee = assignee
        self.in_progress_date = in_progress_date
        self.branch = branch
        self.merge_proposal = merge_proposal
        self.merge_proposal_status = merge_proposal_status
        self.merge_proposal_creation_date = merge_proposal_creation_date
        self.tags = tags if tags else []

    def get_story_tags(self):
        """Get the tags that start with C{story-}."""
        names = set()
        for tag in self.tags:
            if tag.startswith("story-"):
                names.add(tag)
        return list(names)

    def queued(self):
        """Determine if this bug is in queued for attention."""
        return self.status not in [IN_PROGRESS, FIX_COMMITTED,
                                   FIX_RELEASED]

    def in_progress(self):
        """Determine if a fix for this bug needs is in progress."""
        if self.status in [IN_PROGRESS]:
            if (self.merge_proposal
                and self.merge_proposal_status not in [WORK_IN_PROGRESS]):
                return False
            return True
        return False

    def needs_review(self):
        """Determine if the fix for this bug needs to be reviewed."""
        return (self.merge_proposal
                and self.merge_proposal_status in [NEEDS_REVIEW])

    def needs_testing(self):
        """Determine if the fix for this bug needs quality assurance testing.

        If a bug does not have a merge proposal, but it has a L{FIX_COMMITTED}
        status and has the C{verified} tag, it will be in the 'Needs testing'
        category.  If a bug does have a merge proposal, it must be in the
        L{APPROVED} or L{MERGED} states, in addition to being L{FIX_COMMITTED}
        and having the C{verified} tag to be in the 'Needs testing' category.
        """
        needs_testing1 = (self.status in [FIX_COMMITTED]
                          and not self.merge_proposal
                          and "verified" not in self.tags)
        needs_testing2 = (self.status in [IN_PROGRESS, FIX_COMMITTED]
                          and self.merge_proposal
                          and self.merge_proposal_status in [APPROVED, MERGED]
                          and "verified" not in self.tags)
        return needs_testing1 or needs_testing2

    def needs_release(self):
        """
        Determine if the fix for this bug has been verified to work correctly.
        """
        return self.status in [FIX_COMMITTED] and "verified" in self.tags

    def released(self):
        """Determine if the fix for this bug is released."""
        return self.status in [FIX_RELEASED]


def compare_bugs(a, b):
    """Compare two L{Bug}s.

    Bugs with a higher importance are sorted first.  Bugs with the same
    importance are ordered by bug number.
    """
    a_importance = IMPORTANCE_ORDER.index(a.importance)
    b_importance = IMPORTANCE_ORDER.index(b.importance)
    if a_importance < b_importance:
        return -1
    elif a_importance > b_importance:
        return 1
    else:
        return cmp(a.id, b.id)


class BugCollectionMixin(object):
    """A named collecton of L{Bug}s organized into categories.

    @param name: The name of the L{Bug} collection.
    @param include_needs_testing: Optionally, a flag indicating whether or not
        to use the 'Needs testing' category.  Defaults to C{False}.
    """

    def __init__(self, name, include_needs_testing=None):
        self.name = name
        self.include_needs_testing = include_needs_testing
        self.bugs = []
        self.queued = []
        self.in_progress = []
        self.needs_review = []
        self.needs_testing = []
        self.needs_release = []
        self.released = []

    def add(self, bug):
        """Add C{bug} to this collection."""
        self.bugs.append(bug)
        if bug.released():
            self.released.append(bug)
        elif bug.needs_release():
            self.needs_release.append(bug)
        elif bug.needs_testing():
            if self.include_needs_testing:
                self.needs_testing.append(bug)
            else:
                self.needs_release.append(bug)
        elif bug.needs_review():
            self.needs_review.append(bug)
        elif bug.in_progress():
            self.in_progress.append(bug)
        else:
            self.queued.append(bug)


class Story(BugCollectionMixin):
    """A story is a collection of L{Bug}s related to a particular feature.

    @param name: The name of this story.
    @param include_needs_testing: Optionally, a flag indicating whether or not
        to use the 'Needs testing' category.  Defaults to C{False}.
    """


class StoryCollectionMixin(BugCollectionMixin):
    """A collection of L{Bug}s grouped into L{Story}s.

    @param name: The name of this collection.
    @param include_needs_testing: Optionally, a flag indicating whether or not
        to use the 'Needs testing' category.  Defaults to C{False}.
    """

    def __init__(self, name, include_needs_testing=None):
        super(StoryCollectionMixin, self).__init__(
            name, include_needs_testing=include_needs_testing)
        self._stories = {}

    @property
    def stories(self):
        """A C{list} of L{Story}s, sorted alphabetically."""
        return sorted(self._stories.values(), compare_stories)

    def add(self, bug):
        """Add C{bug} to this milestone."""
        super(StoryCollectionMixin, self).add(bug)
        stories = self._get_stories(bug)
        for story in stories:
            story.add(bug)

    def _get_stories(self, bug):
        """Get the L{Story}s that C{bug} is associated with."""
        stories = []
        names = bug.get_story_tags()
        if names:
            for name in names:
                story = self._stories.get(name)
                if story:
                    stories.append(story)
                else:
                    story = Story(
                        name, include_needs_testing=self.include_needs_testing)
                    self._stories[name] = story
                    stories.append(story)
        else:
            if None not in self._stories:
                self._stories[None] = Story(
                    None, include_needs_testing=self.include_needs_testing)
            stories.append(self._stories[None])

        return stories


class MilestoneBoard(StoryCollectionMixin):
    """
    A milestone board contains a collection of L{Bug}s targetted to a
    milestone in Launchpad.

    @param project_name: The name of the project or project group in Launchpad
        this milestone is part of.
    @param milestone_name: The name of this milestone.
    @param include_needs_testing: Optionally, a flag indicating whether or not
        to use the 'Needs testing' category.  Defaults to C{False}.
    """

    def __init__(self, project_name, milestone_name,
                 include_needs_testing=None):
        super(MilestoneBoard, self).__init__(
            milestone_name, include_needs_testing=include_needs_testing)
        self.project_name = project_name


class PersonBoard(StoryCollectionMixin):
    """
    A person board contains a collection of L{Bug}s targetted to a particular
    person or team.

    @param name: The name of the person or team.
    @param include_needs_testing: Optionally, a flag indicating whether or not
        to use the 'Needs testing' category.  Defaults to C{False}.
    """


def compare_stories(a, b):
    """Compare two L{Story}s.

    L{Story}s are sorted alphabetically.  The default story is always sorted
    last.
    """
    if a.name is None:
        return 1
    if b.name is None:
        return -1
    return cmp(a.name, b.name)
