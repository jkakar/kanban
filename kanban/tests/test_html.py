from datetime import datetime

from testtools import TestCase

from kanban.board import Bug, MEDIUM, CRITICAL, IN_PROGRESS, NEEDS_REVIEW
from kanban.html import (
    branch_name, branch_url, importance_css_class, status_css_class, warn)
from kanban.roadmap import QUEUED


class BranchNameTest(TestCase):

    def test_branch_name(self):
        """
        The L{branch_name} filter takes a branch URL and returns the branch
        name.
        """
        self.assertEqual("branch", branch_name("lp:~username/project/branch"))


class BranchURLTest(TestCase):

    def test_branch_url(self):
        """
        The L{branch_url} filter returns the URL for the branch page in
        Launchpad for a L{Bug}'s branch.
        """
        now = datetime.utcnow()
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title", "jkakar", now,
                  "lp:~username/project/branch")
        self.assertEqual("https://code.launchpad.net/~username/project/branch",
                         branch_url(bug))

    def test_branch_url_with_merge_proposal(self):
        """
        The L{branch_url} filter returns the merge proposal URL for branches
        that have one.
        """
        now = datetime.utcnow()
        bug = Bug(
            "1", "kanban", MEDIUM, IN_PROGRESS, "A title", "jkakar", now,
            "lp:~username/project/branch",
            "https://code.launchpad.net/~username/project/branch/+merge/1234",
            NEEDS_REVIEW, now)
        self.assertEqual(
            "https://code.launchpad.net/~username/project/branch/+merge/1234",
            branch_url(bug))


class ImportanceCSSTest(TestCase):

    def test_importance_css_class(self):
        """
        The L{importance_css_class} filter takes a string representation of an
        importance status and generates a CSS class name for it.
        """
        self.assertEqual("critical-importance", importance_css_class(CRITICAL))


class StatusCSSTest(TestCase):

    def test_status_css_class(self):
        """
        The L{status_css_class} filter takes a string representation of a
        roadmap task status and generates a CSS class name for it.
        """
        self.assertEqual("queued-status", status_css_class(QUEUED))


class WarnTest(TestCase):

    def test_in_progress_without_warning(self):
        """
        L{warn} returns C{False} if a L{Bug} has been in progress for less
        than the specified threshold.
        """
        now = datetime.utcnow()
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title", "jkakar", now)
        self.assertFalse(warn(bug, 3, 1))

    def test_in_progress_with_warning(self):
        """
        L{warn} returns C{False} if a L{Bug} has been in progress for less
        than the specified threshold.
        """
        in_progress_date = datetime(2011, 1, 31)
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title", "jkakar",
                  in_progress_date)
        now = datetime(2011, 2, 4)
        self.assertTrue(warn(bug, 3, 1, now))

    def test_in_progress_skips_weekends(self):
        """
        When L{warn} calculates the warning threshold date, it doesn't include
        weekends.
        """
        in_progress_date = datetime(2011, 2, 4)
        bug = Bug("1", "kanban", MEDIUM, IN_PROGRESS, "A title", "jkakar",
                  in_progress_date)
        # With the weekend, 3 days have passed, but the 2 weekend days are not
        # counted, so this bug isn't in a warning state yet.
        now = datetime(2011, 2, 7)
        self.assertFalse(warn(bug, 3, 1, now))

    def test_needs_review_without_warning(self):
        """
        L{warn} returns C{False} if a L{Bug} has been in progress for less
        than the specified threshold.
        """
        now = datetime.utcnow()
        bug = Bug(
            "1", "kanban", MEDIUM, IN_PROGRESS, "A title", "jkakar", now,
            "lp:~username/project/branch",
            "https://code.launchpad.net/~username/project/branch/+merge/1234",
            NEEDS_REVIEW, now)
        self.assertFalse(warn(bug, 3, 1))

    def test_needs_review_with_warning(self):
        """
        L{warn} returns C{False} if a L{Bug} has been in progress for less
        than the specified threshold.
        """
        needs_review_date = datetime(2011, 1, 31)
        bug = Bug(
            "1", "kanban", MEDIUM, IN_PROGRESS, "A title", "jkakar",
            needs_review_date, "lp:~username/project/branch",
            "https://code.launchpad.net/~username/project/branch/+merge/1234",
            NEEDS_REVIEW, needs_review_date)
        now = datetime(2011, 2, 4)
        self.assertTrue(warn(bug, 3, 1, now))

    def test_needs_review_skips_weekends(self):
        """
        When L{warn} calculates the warning threshold date, it doesn't include
        weekends.
        """
        needs_review_date = datetime(2011, 2, 4)
        bug = Bug(
            "1", "kanban", MEDIUM, IN_PROGRESS, "A title", "jkakar",
            needs_review_date, "lp:~username/project/branch",
            "https://code.launchpad.net/~username/project/branch/+merge/1234",
            NEEDS_REVIEW, needs_review_date)
        # With the weekend, 3 days have passed, but the 2 weekend days are not
        # counted, so this bug isn't in a warning state yet.
        now = datetime(2011, 2, 7)
        self.assertFalse(warn(bug, 3, 1, now))

    def test_other_category(self):
        """
        L{warn} returns C{False} if a L{Bug} isn't in the 'In progress' or
        'Need review' categories.
        """
        bug = Bug("1", "kanban", MEDIUM, QUEUED, "A title", "jkakar")
        self.assertFalse(warn(bug, 3, 1))
