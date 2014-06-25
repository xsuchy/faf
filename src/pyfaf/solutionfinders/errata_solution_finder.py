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

from pyfaf.solutionfinders import SolutionFinder, Solution
from pyfaf.problemtypes import problemtypes
from pyfaf.queries import get_errata_for_report, get_errata_for_report_hash


class ErrataSolutionFinder(SolutionFinder):
    name = "sf-errata"
    nice_name = "Errata Solution"

    def __init__(self, *args, **kwargs):
        super(ErrataSolutionFinder, self).__init__()

        self.load_config_to_self("advisory_url",
                                 "errata.erratatooladvisoryurlreadable")

    def _errata_to_solutions(self, errata):
        return [Solution(erratum.advisory_name,
                         self.advisory_url.format(erratum.id),
                         erratum.synopsis, erratum.synopsis)
                for erratum in errata]

    def find_solutions_ureport(self, db, ureport):
        problemplugin = problemtypes[ureport["problem"]["type"]]
        report_hash = problemplugin.hash_ureport(ureport["problem"])

        errata = get_errata_for_report_hash(db, report_hash).all()

        return self._errata_to_solutions(errata)

    def find_solutions_db_report(self, db, db_report, db_opsys=None):
        errata = get_errata_for_report(db, db_report).all()

        return self._errata_to_solutions(errata)
