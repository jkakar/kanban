from datetime import datetime
from json import loads


# Story status states
QUEUED = "Queued"
ACTIVE = "Active"
DONE = "Done"


class Roadmap(object):
    """A high-level project plan representing stories broken into phases.

    @param project: The name of the project in Launchpad.
    """

    def __init__(self, project):
        self.project = project
        self.time_periods = []

    def add(self, time_period):
        """Add a L{TimePeriod} to this roadmap."""
        self.time_periods.append(time_period)

    @property
    def tracks(self):
        """A C{list} of tracks the L{Story}s in this roadmap belong to."""
        tracks = set()
        for time_period in self.time_periods:
            for track in time_period.tracks:
                tracks.add(track)
        return sorted(tracks)


class TimePeriod(object):
    """A window time in which stories are scheduled to be completed.

    @param name: The name of the time period.
    @param start_date: The start date for the time period.
    @param end_date: The end date for the time period.
    """

    def __init__(self, name, start_date, end_date):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.stories = []
        self._tracks = {}

    def add(self, story):
        """Add a L{Story} to this time period."""
        self.stories.append(story)
        self._tracks.setdefault(story.track, [])
        self._tracks[story.track].append(story)

    @property
    def tracks(self):
        """
        A C{list} of tracks the L{Story}s in this time period belong to.
        """
        return sorted(self._tracks.iterkeys())

    def get_stories_by_track(self, track):
        """
        Get a C{list} of L{Story}s in this time period that are in C{track}.
        """
        return self._tracks.get(track, [])


class Story(object):
    """A story.

    @param name: The name of the story.
    @param description: The description of the story.
    @param track: The track this story belongs to.
    @param status: The story status.
    @param link: Optionally, a link to a document providing details about this
        story.
    @param assignees: Optionally, a C{list} of people working on this story.
    """

    def __init__(self, name, description, track, status, link=None,
                 assignees=None):
        self.name = name
        self.description = description
        self.track = track
        self.status = status
        self.link = link
        self.assignees = sorted(assignees) if assignees else []


def load_roadmap(json):
    """Build a L{Roadmap} from a JSON document.

    See L{topic_tutorial}'s docstring for information about the JSON document
    format.

    @param json: A JSON string representing a L{Roadmap}.
    """
    document = loads(json)
    project = document["project"]
    roadmap = Roadmap(project)
    for item in document["time_periods"]:
        start_date = datetime.strptime(item["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(item["end_date"], "%Y-%m-%d")
        time_period = TimePeriod(item["name"], start_date, end_date)
        roadmap.add(time_period)

        for subitem in item["stories"]:
            story = Story(subitem["name"], subitem["description"],
                          subitem["track"], subitem["status"],
                          subitem.get("link"), subitem.get("assignees"))
            time_period.add(story)
    return roadmap
