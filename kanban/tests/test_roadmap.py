from datetime import datetime, timedelta
from json import dumps

from testtools import TestCase

from kanban.roadmap import Roadmap, TimePeriod, Story, load_roadmap, QUEUED


class RoadmapTest(TestCase):

    def test_instantiate(self):
        """A name must be provided when a L{Roadmap} is instantiated."""
        roadmap = Roadmap("project-name")
        self.assertEqual("project-name", roadmap.project)
        self.assertEqual([], roadmap.time_periods)

    def test_add(self):
        """L{Roadmap.add} adds a L{TimePeriod} to a roadmap."""
        roadmap = Roadmap("project-name")
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        time_period = TimePeriod("name", start_date, end_date)
        roadmap.add(time_period)
        self.assertEqual([time_period], roadmap.time_periods)

    def test_tracks_without_time_periods(self):
        """
        L{Roadmap.tracks} is a C{list} of tracks that L{Story}s in
        L{TimePeriod}s are members of.  An empty list is returned if no time
        periods are available.
        """
        roadmap = Roadmap("project-name")
        self.assertEqual([], roadmap.tracks)

    def test_tracks(self):
        """
        The tracks exposed with the L{Roadmap.tracks} property are sorted by
        name.
        """
        roadmap = Roadmap("project-name")
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        time_period1 = TimePeriod("name1", start_date, end_date)
        time_period1.add(Story("name1", "description", "track1", QUEUED))
        time_period1.add(Story("name2", "description", "track2", QUEUED))
        time_period2 = TimePeriod("name2", start_date, end_date)
        time_period2.add(Story("name3", "description", "track3", QUEUED))
        roadmap.add(time_period1)
        roadmap.add(time_period2)
        self.assertEqual(["track1", "track2", "track3"],
                         roadmap.tracks)


class TimePeriodTest(TestCase):

    def test_instantiate(self):
        """
        A name, start date and end date must be provided when a L{TimePeriod}
        is instantiated.
        """
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        time_period = TimePeriod("name", start_date, end_date)
        self.assertEqual("name", time_period.name)
        self.assertEqual(start_date, time_period.start_date)
        self.assertEqual(end_date, time_period.end_date)
        self.assertEqual([], time_period.stories)

    def test_add(self):
        """L{TimePeriod.add} adds a L{Story} to a time period."""
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        time_period = TimePeriod("name", start_date, end_date)
        story = Story("name", "description", "track", QUEUED)
        time_period.add(story)
        self.assertEqual([story], time_period.stories)

    def test_tracks_without_stories(self):
        """
        L{TimePeriod.tracks} is a C{list} of tracks that L{Story}s are members
        of.  An empty list is returned if no stories has been added to the
        time period.
        """
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        time_period = TimePeriod("name", start_date, end_date)
        self.assertEqual([], time_period.tracks)

    def test_tracks(self):
        """
        The tracks exposed with the L{TimePeriod.tracks} property are sorted
        by name.
        """
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        time_period = TimePeriod("name", start_date, end_date)
        time_period.add(Story("name1", "description", "track2", QUEUED))
        time_period.add(Story("name2", "description", "track1", QUEUED))
        self.assertEqual(["track1", "track2"], time_period.tracks)

    def test_get_stories_by_track(self):
        """
        L{TimePeriod.get_stories_by_track} returns all L{Story}s in the time
        period that are in the specified track.  The stories are returned in
        the order they were added to the time period.
        """
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        time_period = TimePeriod("name", start_date, end_date)
        time_period.add(Story("name", "description", "track2", QUEUED))
        story1 = Story("name1", "description", "track1", QUEUED)
        story2 = Story("name2", "description", "track1", QUEUED)
        time_period.add(story1)
        time_period.add(story2)
        self.assertEqual([story1, story2],
                         time_period.get_stories_by_track("track1"))

    def test_get_stories_by_track_without_matches(self):
        """
        L{TimePeriod.get_stories_by_track} returns an empty C{list} if no
        L{Story}s match the specified track.
        """
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        time_period = TimePeriod("name", start_date, end_date)
        time_period.add(Story("name", "description", "track1", QUEUED))
        self.assertEqual([], time_period.get_stories_by_track("track2"))


class StoryTest(TestCase):

    def test_instantiate(self):
        """
        A name, description, track and status must be provided when a L{Story}
        is instantiated.
        """
        story = Story("name", "description", "track", QUEUED)
        self.assertEqual("name", story.name)
        self.assertEqual("description", story.description)
        self.assertEqual("track", story.track)
        self.assertEqual(QUEUED, story.status)
        self.assertIs(None, story.link)
        self.assertEqual([], story.assignees)

    def test_instantiate_with_link(self):
        """
        A link to a document providing information about a story can
        optionally be provided when a L{Story} is instantiated.
        """
        story = Story("name", "description", "track", QUEUED,
                      "http://example.com")
        self.assertEqual("http://example.com", story.link)

    def test_instantiate_with_assignees(self):
        """
        A C{list} of assignees working on a story can optionally be provided
        when a L{Story} is instantiated.  The provided list will be sorted
        alphabetically.
        """
        story = Story("name", "description", "track", QUEUED,
                      assignees=["bob", "anne"])
        self.assertEqual(["anne", "bob"], story.assignees)


class LoadRoadmapTest(TestCase):

    def test_load_empty_roadmap(self):
        """
        L{load_roadmap} creates an empty L{Roadmap} if no time period data is
        provided.
        """
        json = dumps({"project": "project-name", "time_periods": []})
        roadmap = load_roadmap(json)
        self.assertEqual("project-name", roadmap.project)
        self.assertEqual([], roadmap.time_periods)

    def test_load_roadmap(self):
        """
        L{load_roadmap} creates a L{Roadmap} with L{TimePeriod}s and L{Stories}
        from a JSON document.
        """
        json = dumps({"project": "project-name",
                      "time_periods": [
                          {"name": "time-period-name",
                           "start_date": "2011-01-29",
                           "end_date": "2011-02-28",
                           "stories": [
                               {"name": "story-name",
                                "description": "story-description",
                                "track": "story-track",
                                "status": "In progress"}]}]})
        roadmap = load_roadmap(json)
        self.assertEqual("project-name", roadmap.project)
        [time_period] = roadmap.time_periods
        self.assertEqual("time-period-name", time_period.name)
        self.assertEqual(datetime(2011, 1, 29), time_period.start_date)
        self.assertEqual(datetime(2011, 2, 28), time_period.end_date)
        [story] = time_period.stories
        self.assertEqual("story-name", story.name)
        self.assertEqual("story-description", story.description)
        self.assertEqual("story-track", story.track)
        self.assertEqual("In progress", story.status)

    def test_load_roadmap_maintains_time_period_order(self):
        """
        L{load_roadmap} creates a L{Roadmap} with L{TimePeriod}s in the same
        order they're represented in the JSON document.
        """
        json = dumps({"project": "project-name",
                      "time_periods": [
                          {"name": "time-period-1",
                           "start_date": "2011-01-01",
                           "end_date": "2011-01-31",
                           "stories": []},
                          {"name": "time-period-2",
                           "start_date": "2011-02-01",
                           "end_date": "2011-02-28",
                           "stories": []}]})
        roadmap = load_roadmap(json)
        self.assertEqual("project-name", roadmap.project)
        [time_period1, time_period2] = roadmap.time_periods
        self.assertEqual("time-period-1", time_period1.name)
        self.assertEqual("time-period-2", time_period2.name)

    def test_load_roadmap_maintains_story_order(self):
        """
        L{load_roadmap} creates a L{Roadmap} with L{Story}s in a L{TimePeriod}
        in the same order they're represented in the JSON document.
        """
        json = dumps({"project": "project-name",
                      "time_periods": [
                          {"name": "time-period-1",
                           "start_date": "2011-01-01",
                           "end_date": "2011-01-31",
                           "stories": [
                               {"name": "story-1",
                                "description": "story-description1",
                                "track": "story-track1",
                                "status": "In progress"},
                               {"name": "story-2",
                                "description": "story-description2",
                                "track": "story-track2",
                                "status": "In progress"}]}]})
        roadmap = load_roadmap(json)
        self.assertEqual("project-name", roadmap.project)
        [time_period] = roadmap.time_periods
        [story1, story2] = time_period.stories
        self.assertEqual("story-1", story1.name)
        self.assertEqual("story-2", story2.name)
