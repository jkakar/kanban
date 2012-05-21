Kanban is a simple tool to generate a kanban board from Launchpad bugs
or GitHub issues.


License
-------

Kanban is a simple tool to generate a kanban board from data in
Launchpad.  Copyright (C) 2010-2012 Jamshed Kakar.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.


On Ubuntu systems, the complete text of the GNU General Public
version 3 License is in `/usr/share/common-licenses/GPL-3`.


Dependencies
------------

Kanban requires Python 2.6+ and has the following package
dependencies:

- `python-commandant`
- `python-jinja2`
- `python-launchpadlib`
- `python-testtools` (to run the test suite)

The `python-commandant` package is available from a PPA:

  https://launchpad.net/~jkakar/+archive/commandant


Using Kanban
------------

Run the following command to learn how to use Kanban in more detail:

    bin/kanban help tutorial | less
