# Copyright (C) 2014  ABRT Team
# Copyright (C) 2014  Red Hat, Inc.
#
# This file is part of faf.
#
# faf is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# faf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with faf.  If not, see <http://www.gnu.org/licenses/>.

import os
from collections import namedtuple
from pyfaf.common import FafError, Plugin, import_dir, load_plugins
from pyfaf.storage import Report, getDatabase
from pyfaf.ureport_compat import ureport1to2

solution_finders = {}

Solution = namedtuple("Solution", ["cause", "url", "note_text", "note_html"])


class SolutionFinder(Plugin):
    name = "abstract_solution_finder"

    def __init__(self, *args, **kwargs):
        """
        The superclass constructor does not really need to be called, but it
        enables a few useful features (like unified logging). If not called
        by the child, it just makes sure that SolutionFinder class is not
        instantiated directly.
        """

        if self.__class__.__name__ == "SolutionFinder":
            raise FafError("You need to subclass the SolutionFinder class "
                           "in order to implement a solution finder plugin.")

        super(SolutionFinder, self).__init__()

        # Lower number means higher priority
        self.load_config_to_self("solution_priority", "{0}.solution_priority"
                                 .format(self.name), 100, callback=int)

    def find_solutions_ureport(self, db, ureport):
        return []

    def find_solutions_db_report(self, db, db_report):
        return []

import_dir(__name__, os.path.dirname(__file__))
load_plugins(SolutionFinder, solution_finders)


def find_solutions(report, db=None, finders=None):
    """
    Check whether Solution objects exist for a report (pyfaf.storage.Report or
    uReport dict). Return an array of Solution objects in ascending order by
    priority (i.e. highest priority first).
    """

    if db is None:
        db = getDatabase()

    if finders is None:
        finders = solution_finders.keys()

    solutions = []

    if isinstance(report, Report):
        for finder_name in finders:
            solution_finder = solution_finders[finder_name]
            finder_solutions = solution_finder.find_solutions_db_report(db,
                                                                        report)
            solutions += [(solution_finder.solution_priority, solution)
                          for solution in finder_solutions]

    elif isinstance(report, dict):
        if "ureport_version" in report and report["ureport_version"] == 1:
            report = ureport1to2(report)
        for finder_name in finders:
            solution_finder = solution_finders[finder_name]
            finder_solutions = solution_finder.find_solutions_ureport(db, report)
            solutions += [(solution_finder.solution_priority, solution)
                          for solution in finder_solutions]

    else:
        raise ValueError("`report` must be an instance of either "
                         "pyfaf.storage.Report or dict")

    return [solution for (priority, solution) in
            sorted(solutions, key=lambda solution: solution[0])]


def find_solution(report, db=None, finders=None):
    """
    Check whether a Solution exists for a report (pyfaf.storage.Report or
    uReport dict). Return Solution object for the
    solution with the highest priority (i.e. lowest number) or None.
    """
    solutions = find_solutions(report, db, finders)

    if isinstance(solutions, list) and len(solutions) > 0:
        return solutions[0]
    return None
