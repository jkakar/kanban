from datetime import datetime

from testtools import TestCase

from kanban.board import (
    Bug, MilestoneBoard, PersonBoard, Story, compare_bugs, compare_stories,
    NEW, CONFIRMED, TRIAGED, IN_PROGRESS, FIX_COMMITTED, FIX_RELEASED,
    UNDECIDED, WISHLIST, LOW, MEDIUM, HIGH, CRITICAL, WORK_IN_PROGRESS,
    NEEDS_REVIEW, APPROVED, MERGED)


class BugTest(TestCase):

    def test_instantiate_with_default_values(self):
        """
        An ID, project name, importance and title must be provided when a
        L{Bug} is instantiated.  All other values default to C{None}.
        """
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title")
        self.assertEqual("1", bug.id)
        self.assertEqual("kanban", bug.project)
        self.assertEqual(MEDIUM, bug.importance)
        self.assertEqual("In Progress", bug.status)
        self.assertEqual("A title", bug.title)
        self.assertIs(None, bug.assignee)
        self.assertIs(None, bug.in_progress_date)
        self.assertIs(None, bug.branch)
        self.assertIs(None, bug.merge_proposal)
        self.assertIs(None, bug.merge_proposal_status)
        self.assertIs(None, bug.merge_proposal_creation_date)
        self.assertEqual([], bug.tags)

    def test_instantiate(self):
        """
        In addition to the required values an assignee, 'In progress' date,
        branch URL, merge proposal URL, merge proposal status, merge proposal
        review request date and a list of tags can be provided when a L{Bug}
        is instantiated.
        """
        now = datetime.utcnow()
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title", "jkakar",
                  now, "branch_url", "merge_url", NEEDS_REVIEW, now,
                  ["test"])
        self.assertEqual("jkakar", bug.assignee)
        self.assertEqual(now, bug.in_progress_date)
        self.assertEqual("branch_url", bug.branch)
        self.assertEqual("merge_url", bug.merge_proposal)
        self.assertEqual(NEEDS_REVIEW, bug.merge_proposal_status)
        self.assertEqual(now, bug.merge_proposal_creation_date)
        self.assertEqual(["test"], bug.tags)

    def test_get_story_tags_without_matches(self):
        """
        L{Bug.get_story_tags} returns an empty list if no tags start with
        C{story-}.
        """
        now = datetime.utcnow()
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title", "jkakar", now,
                  "branch_url", "merge_url", NEEDS_REVIEW, now, ["test"])
        self.assertEqual([], bug.get_story_tags())

    def test_get_story_tags(self):
        """
        L{Bug.get_story_tags} returns the list of tags that start with
        C{story-}.
        """
        now = datetime.utcnow()
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title", "jkakar", now,
                  "branch_url", "merge_url", NEEDS_REVIEW, now,
                  ["test", "story-test"])
        self.assertEqual(["story-test"], bug.get_story_tags())

    def test_queued_with_new_status(self):
        """A L{Bug} with a L{NEW} status is in the 'Queued' category."""
        bug = Bug("1", "kanban", MEDIUM, NEW, "A title")
        self.assertTrue(bug.queued())
        self.assertFalse(bug.in_progress())
        self.assertFalse(bug.needs_review())
        self.assertFalse(bug.needs_testing())
        self.assertFalse(bug.needs_release())
        self.assertFalse(bug.released())

    def test_queued_with_confirmed_status(self):
        """A L{Bug} with a L{CONFIRMED} status is in the 'Queued' category."""
        bug = Bug("1", "kanban", MEDIUM, CONFIRMED, "A title")
        self.assertTrue(bug.queued())
        self.assertFalse(bug.in_progress())
        self.assertFalse(bug.needs_review())
        self.assertFalse(bug.needs_testing())
        self.assertFalse(bug.needs_release())
        self.assertFalse(bug.released())

    def test_queued_with_triaged_status(self):
        """A L{Bug} with a L{TRIAGED} status is in the 'Queued' category."""
        bug = Bug("1", "kanban", MEDIUM, TRIAGED, "A title")
        self.assertTrue(bug.queued())
        self.assertFalse(bug.in_progress())
        self.assertFalse(bug.needs_review())
        self.assertFalse(bug.needs_testing())
        self.assertFalse(bug.needs_release())
        self.assertFalse(bug.released())

    def test_in_progress(self):
        """
        A L{Bug} with an L{IN_PROGRESS} status is in the 'In progress'
        category.
        """
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title")
        self.assertFalse(bug.queued())
        self.assertTrue(bug.in_progress())
        self.assertFalse(bug.needs_review())
        self.assertFalse(bug.needs_testing())
        self.assertFalse(bug.needs_release())
        self.assertFalse(bug.released())

    def test_in_progress_with_work_in_progress_merge_proposal(self):
        """
        A L{Bug} with an L{IN_PROGRESS} status that has a merge proposal with
        a L{NEEDS_REVIEW} status is in the 'In progress' category.
        """
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title",
                  merge_proposal="url", merge_proposal_status=WORK_IN_PROGRESS)
        self.assertFalse(bug.queued())
        self.assertTrue(bug.in_progress())
        self.assertFalse(bug.needs_review())
        self.assertFalse(bug.needs_testing())
        self.assertFalse(bug.needs_release())
        self.assertFalse(bug.released())

    def test_needs_review(self):
        """
        A L{Bug} with an L{IN_PROGRESS} status and a merge proposal with a
        L{NEEDS_REVIEW} status is in the 'Needs review' category.
        """
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title",
                  merge_proposal="url", merge_proposal_status=NEEDS_REVIEW)
        self.assertFalse(bug.queued())
        self.assertFalse(bug.in_progress())
        self.assertTrue(bug.needs_review())
        self.assertFalse(bug.needs_testing())
        self.assertFalse(bug.needs_release())
        self.assertFalse(bug.released())

    def test_needs_testing_in_progress_with_approved_merge_proposal(self):
        """
        A L{Bug} with an L{IN_PROGRESS} statuslinked to a merge proposal with
        an L{APPROVED} status is in the 'Needs testing' category.
        """
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title",
                  merge_proposal="url", merge_proposal_status=APPROVED)
        self.assertFalse(bug.queued())
        self.assertFalse(bug.in_progress())
        self.assertFalse(bug.needs_review())
        self.assertTrue(bug.needs_testing())
        self.assertFalse(bug.needs_release())
        self.assertFalse(bug.released())

    def test_needs_testing_in_progress_with_merged_merge_proposal(self):
        """
        A L{Bug} with an L{IN_PROGRESS} status linked to a merge proposal with
        an L{APPROVED} status is in the 'Needs testing' category.
        """
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title",
                  merge_proposal="url", merge_proposal_status=MERGED)
        self.assertFalse(bug.queued())
        self.assertFalse(bug.in_progress())
        self.assertFalse(bug.needs_review())
        self.assertTrue(bug.needs_testing())
        self.assertFalse(bug.needs_release())
        self.assertFalse(bug.released())

    def test_needs_testing_fix_committed_with_approved_merge_proposal(self):
        """
        A L{Bug} with an L{FIX_COMMITTED} statuslinked to a merge proposal
        with an L{APPROVED} status is in the 'Needs testing' category.
        """
        bug = Bug("1", "kanban", MEDIUM, FIX_COMMITTED, "A title",
                  merge_proposal="url", merge_proposal_status=APPROVED)
        self.assertFalse(bug.queued())
        self.assertFalse(bug.in_progress())
        self.assertFalse(bug.needs_review())
        self.assertTrue(bug.needs_testing())
        self.assertFalse(bug.needs_release())
        self.assertFalse(bug.released())

    def test_needs_testing_fix_committed_with_merged_merge_proposal(self):
        """
        A L{Bug} with an L{FIX_COMMITTED} status linked to a merge proposal
        with an L{APPROVED} status is in the 'Needs testing' category.
        """
        bug = Bug("1", "kanban", MEDIUM, FIX_COMMITTED, "A title",
                  merge_proposal="url", merge_proposal_status=MERGED)
        self.assertFalse(bug.queued())
        self.assertFalse(bug.in_progress())
        self.assertFalse(bug.needs_review())
        self.assertTrue(bug.needs_testing())
        self.assertFalse(bug.needs_release())
        self.assertFalse(bug.released())

    def test_needs_testing_fix_committed_without_merge_proposal(self):
        """
        A L{Bug} with an L{FIX_COMMITTED} status not linked to a merge
        proposal is in the 'Needs testing' category.
        """
        bug = Bug("1", "kanban", MEDIUM, FIX_COMMITTED, "A title")
        self.assertFalse(bug.queued())
        self.assertFalse(bug.in_progress())
        self.assertFalse(bug.needs_review())
        self.assertTrue(bug.needs_testing())
        self.assertFalse(bug.needs_release())
        self.assertFalse(bug.released())

    def test_needs_release(self):
        """
        A L{Bug} with a L{FIX_COMMITTED} status linked to a merge proposal
        with an L{MERGED} status and the C{verified} tag is in the
        'Needs release' category.
        """
        bug = Bug("1", "kanban", MEDIUM, FIX_COMMITTED, "A title",
                  merge_proposal="url", merge_proposal_status=MERGED,
                  tags=["verified"])
        self.assertFalse(bug.queued())
        self.assertFalse(bug.in_progress())
        self.assertFalse(bug.needs_review())
        self.assertFalse(bug.needs_testing())
        self.assertTrue(bug.needs_release())
        self.assertFalse(bug.released())

    def test_needs_release_without_merge_proposal(self):
        """
        A L{Bug} with a L{FIX_COMMITTED} status that is not linked to a merge
        proposal, but has the C{verified} tag is in the 'Needs release'
        category.
        """
        bug = Bug("1", "kanban", MEDIUM, FIX_COMMITTED, "A title",
                  branch="branch_url", tags=["verified"])
        self.assertFalse(bug.queued())
        self.assertFalse(bug.in_progress())
        self.assertFalse(bug.needs_review())
        self.assertFalse(bug.needs_testing())
        self.assertTrue(bug.needs_release())
        self.assertFalse(bug.released())

    def test_released(self):
        """
        A L{Bug} with a L{FIX_RELEASED} status is in the 'Released' category.
        """
        bug = Bug("1", "kanban", MEDIUM, FIX_RELEASED, "A title")
        self.assertFalse(bug.queued())
        self.assertFalse(bug.in_progress())
        self.assertFalse(bug.needs_review())
        self.assertFalse(bug.needs_testing())
        self.assertFalse(bug.needs_release())
        self.assertTrue(bug.released())


class CompareBugsTest(TestCase):

    def test_sort_order(self):
        """The L{compare_bugs} method sorts higher importance bugs first."""
        bugs = [Bug("1", "kanban", UNDECIDED, FIX_RELEASED, "A title"),
                Bug("2", "kanban", WISHLIST, FIX_RELEASED, "A title"),
                Bug("3", "kanban", LOW, FIX_RELEASED, "A title"),
                Bug("4", "kanban", MEDIUM, FIX_RELEASED, "A title"),
                Bug("5", "kanban", HIGH, FIX_RELEASED, "A title"),
                Bug("6", "kanban", CRITICAL, FIX_RELEASED, "A title")]
        self.assertEquals(list(reversed(bugs)), sorted(bugs, compare_bugs))

    def test_same_status_defers_to_bug_number(self):
        """
        L{Bug}s with the same importance status are secondarily ordered by
        L{Bug.id}.
        """
        bugs = [Bug("2", "kanban", UNDECIDED, FIX_RELEASED, "Zebra"),
                Bug("1", "kanban", UNDECIDED, FIX_RELEASED, "Alpha")]
        self.assertEquals(list(reversed(bugs)), sorted(bugs, compare_bugs))


class BugCollectionMixinTestBase(object):

    def test_add_queued(self):
        """
        A L{Bug} in the 'Queued' category is stored in the
        L{BugCollectionMixin.bugs} and the L{Story.queued} lists, in the
        default story.
        """
        bug = Bug("1", "kanban", MEDIUM, NEW, "A title")
        kanban_board = self.create_test_class()
        kanban_board.add(bug)
        self.assertEqual([bug], kanban_board.bugs)
        self.assertEqual([bug], kanban_board.queued)
        self.assertEqual([], kanban_board.in_progress)
        self.assertEqual([], kanban_board.needs_review)
        self.assertEqual([], kanban_board.needs_testing)
        self.assertEqual([], kanban_board.needs_release)
        self.assertEqual([], kanban_board.released)

    def test_add_in_progress(self):
        """
        A L{Bug} in the 'In progress' category is stored in the
        L{BugCollectionMixin.bugs} and the L{Story.in_progress} lists, in the
        default story.
        """
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title")
        kanban_board = self.create_test_class()
        kanban_board.add(bug)
        self.assertEqual([bug], kanban_board.bugs)
        self.assertEqual([], kanban_board.queued)
        self.assertEqual([bug], kanban_board.in_progress)
        self.assertEqual([], kanban_board.needs_review)
        self.assertEqual([], kanban_board.needs_testing)
        self.assertEqual([], kanban_board.needs_release)
        self.assertEqual([], kanban_board.released)

    def test_add_needs_review(self):
        """
        A L{Bug} in the 'Needs review' category is stored in the
        L{BugCollectionMixin.bugs} and the L{Story.in_progress} lists, in the
        default story.
        """
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title",
                  merge_proposal="url", merge_proposal_status=NEEDS_REVIEW)
        kanban_board = self.create_test_class()
        kanban_board.add(bug)
        self.assertEqual([bug], kanban_board.bugs)
        self.assertEqual([], kanban_board.queued)
        self.assertEqual([], kanban_board.in_progress)
        self.assertEqual([bug], kanban_board.needs_review)
        self.assertEqual([], kanban_board.needs_testing)
        self.assertEqual([], kanban_board.needs_release)
        self.assertEqual([], kanban_board.released)

    def test_add_needs_testing(self):
        """
        A L{Bug} in the 'Needs testing' category is stored in the
        L{BugCollectionMixin.bugs} and the L{Story.needs_testing} lists, in
        the default story.
        """
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title",
                  merge_proposal="url", merge_proposal_status=APPROVED)
        kanban_board = self.create_test_class(include_needs_testing=True)
        kanban_board.add(bug)
        self.assertEqual([bug], kanban_board.bugs)
        self.assertEqual([], kanban_board.queued)
        self.assertEqual([], kanban_board.in_progress)
        self.assertEqual([], kanban_board.needs_review)
        self.assertEqual([bug], kanban_board.needs_testing)
        self.assertEqual([], kanban_board.needs_release)
        self.assertEqual([], kanban_board.released)

    def test_add_needs_testing_disabled(self):
        """
        A L{Bug} in the 'Needs testing' category is stored in the
        L{BugCollectionMixin.bugs} and the L{Story.needs_release} lists, in
        the default story, when the 'Needs testing' category is disabled.
        """
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title",
                  merge_proposal="url", merge_proposal_status=APPROVED)
        kanban_board = self.create_test_class()
        kanban_board.add(bug)
        self.assertEqual([bug], kanban_board.bugs)
        self.assertEqual([], kanban_board.queued)
        self.assertEqual([], kanban_board.in_progress)
        self.assertEqual([], kanban_board.needs_review)
        self.assertEqual([], kanban_board.needs_testing)
        self.assertEqual([bug], kanban_board.needs_release)
        self.assertEqual([], kanban_board.released)

    def test_add_needs_release(self):
        """
        A L{Bug} in the 'Needs release' category is stored in the
        L{BugCollectionMixin.bugs} and the L{Story.needs_release} lists, in
        the default story.
        """
        bug = Bug("1", "kanban", MEDIUM, FIX_COMMITTED, "A title",
                  merge_proposal="url", merge_proposal_status=MERGED,
                  tags=["verified"])
        kanban_board = self.create_test_class()
        kanban_board.add(bug)
        self.assertEqual([bug], kanban_board.bugs)
        self.assertEqual([], kanban_board.queued)
        self.assertEqual([], kanban_board.in_progress)
        self.assertEqual([], kanban_board.needs_review)
        self.assertEqual([], kanban_board.needs_testing)
        self.assertEqual([bug], kanban_board.needs_release)
        self.assertEqual([], kanban_board.released)

    def test_add_released(self):
        """
        A L{Bug} in the 'Released' category is stored in the
        L{BugCollectionMixin.bugs} and the L{Story.released} lists, in the
        default story.
        """
        bug = Bug("1", "kanban", MEDIUM, FIX_RELEASED, "A title")
        kanban_board = self.create_test_class()
        kanban_board.add(bug)
        self.assertEqual([bug], kanban_board.bugs)
        self.assertEqual([], kanban_board.queued)
        self.assertEqual([], kanban_board.in_progress)
        self.assertEqual([], kanban_board.needs_review)
        self.assertEqual([], kanban_board.needs_testing)
        self.assertEqual([], kanban_board.needs_release)
        self.assertEqual([bug], kanban_board.released)


class StoryCollectionMixinTestBase(object):

    def test_add_bug_with_story_tag_creates_story(self):
        """
        If a L{Bug} with a C{story-<name>} tag is added to a
        L{StoryCollectionMixin}, and a L{Story} with a matching name doesn't
        exist, one will be created and the bug will be added to it.
        """
        bug = Bug("1", "kanban", MEDIUM, NEW, "A title", tags=["story-test"])
        kanban_board = self.create_test_class()
        kanban_board.add(bug)
        self.assertEqual([bug], kanban_board.bugs)
        self.assertEqual(1, len(kanban_board.stories))
        story = kanban_board.stories[0]
        self.assertIs("story-test", story.name)
        self.assertEqual([bug], story.queued)
        self.assertEqual([], story.in_progress)
        self.assertEqual([], story.needs_review)
        self.assertEqual([], story.needs_testing)
        self.assertEqual([], story.needs_release)
        self.assertEqual([], story.released)

    def test_add_bug_with_story_tag_adds_to_existing_story(self):
        """
        If a L{Story} already exists, and a L{Bug} with a matching tag is
        added to a L{StoryCollectionMixin}, it will be added to the existing
        story.
        """
        bug1 = Bug("1", "kanban", MEDIUM, NEW, "A title", tags=["story-test"])
        bug2 = Bug("2", "kanban", MEDIUM, NEW, "A title", tags=["story-test"])
        kanban_board = self.create_test_class()
        kanban_board.add(bug1)
        kanban_board.add(bug2)
        self.assertEqual(1, len(kanban_board.stories))
        story = kanban_board.stories[0]
        self.assertIs("story-test", story.name)
        self.assertEqual([bug1, bug2], story.queued)
        self.assertEqual([], story.in_progress)
        self.assertEqual([], story.needs_review)
        self.assertEqual([], story.needs_testing)
        self.assertEqual([], story.needs_release)
        self.assertEqual([], story.released)

    def test_add_bug_with_multiple_story_tags(self):
        """
        If a L{Bug} has more than one C{story-<name>} tag it will be added to
        multiple L{Story}s when its added to a L{StoryCollectionMixin}.
        """
        bug = Bug("1", "kanban", MEDIUM, NEW, "A title",
                  tags=["story-test1", "story-test2"])
        kanban_board = self.create_test_class()
        kanban_board.add(bug)
        self.assertEqual(2, len(kanban_board.stories))

        story1 = kanban_board.stories[0]
        self.assertIs("story-test1", story1.name)
        self.assertEqual([bug], story1.queued)

        story2 = kanban_board.stories[1]
        self.assertIs("story-test2", story2.name)
        self.assertEqual([bug], story2.queued)

    def test_stories_sorting(self):
        """
        The L{StoryCollectionMixin.stories} property sorts L{Story}s
        alphabetically.  The default L{Story} is always at the end of the
        list.
        """
        bug1 = Bug("1", "kanban", MEDIUM, NEW, "A title")
        bug2 = Bug("2", "kanban", MEDIUM, NEW, "A title",
                   tags=["story-test1", "story-test2"])
        kanban_board = self.create_test_class()
        kanban_board.add(bug1)
        kanban_board.add(bug2)
        self.assertEqual(["story-test1", "story-test2", None],
                         [story.name for story in kanban_board.stories])

    def test_add_considers_include_needs_testing(self):
        """
        If a L{Bug} with a C{story-<name>} tag is added to a
        L{StoryCollectionMixin} which is configured to include the 'Needs
        testing' category, the related L{Story}s will also be configured to
        include the 'Needs testing' category.
        """
        bug = Bug("1", "kanban", MEDIUM, NEW, "A title", tags=["story-test"])
        kanban_board = self.create_test_class(include_needs_testing=True)
        kanban_board.add(bug)
        self.assertEqual([bug], kanban_board.bugs)
        self.assertEqual(1, len(kanban_board.stories))
        story = kanban_board.stories[0]
        self.assertTrue(story.include_needs_testing)


class MilestoneBoardTest(BugCollectionMixinTestBase,
                         StoryCollectionMixinTestBase, TestCase):

    def create_test_class(self, include_needs_testing=None):
        """
        Create a L{MilestoneBoard} for use in L{BugCollectionMixinTestBase}
        and L{StoryCollectionMixinTestBase} tests.
        """
        return MilestoneBoard("project", "milestone",
                              include_needs_testing=include_needs_testing)

    def test_instantiate(self):
        """
        A L{MilestoneBoard} needs the name of the project and its own name
        when its instantiated.
        """
        kanban_board = MilestoneBoard("project", "milestone")
        self.assertEqual("project", kanban_board.project_name)
        self.assertEqual("milestone", kanban_board.name)
        self.assertEqual([], kanban_board.stories)


class PersonBoardTest(BugCollectionMixinTestBase, StoryCollectionMixinTestBase,
                      TestCase):

    def create_test_class(self, include_needs_testing=None):
        """
        Create a L{PersonBoard} for use in L{BugCollectionMixinTestBase} and
        L{StoryCollectionMixinTestBase} tests.
        """
        return PersonBoard("team", include_needs_testing=include_needs_testing)

    def test_instantiate(self):
        """
        A L{PersonBoard} needs the name of the person or team when its
        instantiated.
        """
        kanban_board = PersonBoard("person")
        self.assertEqual("person", kanban_board.name)
        self.assertEqual([], kanban_board.stories)


class StoryTest(BugCollectionMixinTestBase, TestCase):

    def create_test_class(self, include_needs_testing=None):
        """
        Create a L{Story} for use in L{BugCollectionMixinTestBase} tests.
        """
        return Story("name", include_needs_testing=include_needs_testing)


class CompareStoriesTest(TestCase):

    def test_sort_order(self):
        """
        The L{compare_stories} method sorts L{Story}s alphabetically.  The
        default story is always at the end of the list.
        """
        stories = [Story(None), Story("story-zebra"), Story("story-alpha")]
        self.assertEquals(list(reversed(stories)),
                          sorted(stories, compare_stories))
