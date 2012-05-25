# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""BibRank Regression Test Suite."""

__revision__ = "$Id$"

import unittest
import re
from datetime import datetime
from subprocess import Popen
from mechanize import Browser

from invenio.config import CFG_SITE_URL, CFG_SITE_RECORD, CFG_BINDIR
from invenio.dbquery import run_sql
from invenio.testutils import make_test_suite, run_test_suite, \
                              test_web_page_content, merge_error_messages
from invenio.bibrank_bridge_utils import get_external_word_similarity_ranker
from invenio.bibsched import get_last_taskid

class BibRankWebPagesAvailabilityTest(unittest.TestCase):
    """Check BibRank web pages whether they are up or not."""

    def test_rank_by_word_similarity_pages_availability(self):
        """bibrank - availability of ranking search results pages"""

        baseurl = CFG_SITE_URL + '/search'

        _exports = ['?p=ellis&r=wrd']

        error_messages = []
        for url in [baseurl + page for page in _exports]:
            error_messages.extend(test_web_page_content(url))
        if error_messages:
            self.fail(merge_error_messages(error_messages))
        return

    def test_similar_records_pages_availability(self):
        """bibrank - availability of similar records results pages"""

        baseurl = CFG_SITE_URL + '/search'

        _exports = ['?p=recid%3A18&rm=wrd']

        error_messages = []
        for url in [baseurl + page for page in _exports]:
            error_messages.extend(test_web_page_content(url))
        if error_messages:
            self.fail(merge_error_messages(error_messages))
        return

class BibRankIntlMethodNames(unittest.TestCase):
    """Check BibRank I18N ranking method names."""

    def test_i18n_ranking_method_names(self):
        """bibrank - I18N ranking method names"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/collection/Articles%20%26%20Preprints?as=1',
                                               expected_text="times cited"))
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/collection/Articles%20%26%20Preprints?as=1',
                                               expected_text="journal impact factor"))

class BibRankWordSimilarityRankingTest(unittest.TestCase):
    """Check BibRank word similarity ranking tools."""

    def test_search_results_ranked_by_similarity(self):
        """bibrank - search results ranked by word similarity"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=ellis&rm=wrd&of=id',
                                               expected_text="[8, 10, 17, 11, 12, 13, 47, 16, 9, 14, 18, 15]"))

    def test_similar_records_link(self):
        """bibrank - 'Similar records' link"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=recid%3A77&rm=wrd&of=id',
                                               expected_text="[84, 96, 95, 85, 77]"))

class BibRankCitationRankingTest(unittest.TestCase):
    """Check BibRank citation ranking tools."""

    def test_search_results_ranked_by_citations(self):
        """bibrank - search results ranked by number of citations"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?cc=Articles+%26+Preprints&p=Klebanov&rm=citation&of=id',
                                               username="admin",
                                               expected_text="[85, 77, 84]"))

    def test_search_results_ranked_by_citations_verbose(self):
        """bibrank - search results ranked by number of citations, verbose output"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?cc=Articles+%26+Preprints&p=Klebanov&rm=citation&verbose=2',
                                               username="admin",
                                               expected_text="find_citations retlist [[85, 0], [77, 2], [84, 3]]"))

    def test_detailed_record_citations_tab(self):
        """bibrank - detailed record, citations tab"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/'+ CFG_SITE_RECORD +'/79/citations',
                                               expected_text=["Cited by: 1 records",
                                                              "Co-cited with: 2 records"]))

class BibRankExtCitesTest(unittest.TestCase):
    """Check BibRank citation ranking tools with respect to the external cites."""

    def _detect_extcite_info(self, extcitepubinfo):
        """
        Helper function to return list of recIDs citing given
        extcitepubinfo.  Could be move to the business logic, if
        interesting for other callers.
        """
        res = run_sql("""SELECT id_bibrec FROM rnkCITATIONDATAEXT
                          WHERE extcitepubinfo=%s""",
                      (extcitepubinfo,))
        return [int(x[0]) for x in res]

    def test_extcite_via_report_number(self):
        """bibrank - external cites, via report number"""
        # The external paper hep-th/0112258 is cited by 9 demo
        # records: you can find out via 999:"hep-th/0112258", and we
        # could eventually automatize this query, but it is maybe
        # safer to leave it manual in case queries fail for some
        # reason.
        test_case_repno = "hep-th/0112258"
        test_case_repno_cited_by = [77, 78, 81, 82, 85, 86, 88, 90, 91]
        self.assertEqual(self._detect_extcite_info(test_case_repno),
                         test_case_repno_cited_by)

    def test_extcite_via_publication_reference(self):
        """bibrank - external cites, via publication reference"""
        # The external paper "J. Math. Phys. 4 (1963) 915" does not
        # have any report number, and is cited by 1 demo record.
        test_case_pubinfo = "J. Math. Phys. 4 (1963) 915"
        test_case_pubinfo_cited_by = [90]
        self.assertEqual(self._detect_extcite_info(test_case_pubinfo),
                         test_case_pubinfo_cited_by)

    def test_intcite_via_report_number(self):
        """bibrank - external cites, no internal papers via report number"""
        # The internal paper hep-th/9809057 is cited by 2 demo
        # records, but it also exists as a demo record, so it should
        # not be found in the extcite table.
        test_case_repno = "hep-th/9809057"
        test_case_repno_cited_by = []
        self.assertEqual(self._detect_extcite_info(test_case_repno),
                         test_case_repno_cited_by)

    def test_intcite_via_publication_reference(self):
        """bibrank - external cites, no internal papers via publication reference"""
        # The internal paper #18 has only pubinfo, no repno, and is
        # cited by internal paper #96 via its pubinfo, so should not
        # be present in the extcite list:
        test_case_repno = "Phys. Lett., B 151 (1985) 357"
        test_case_repno_cited_by = []
        self.assertEqual(self._detect_extcite_info(test_case_repno),
                         test_case_repno_cited_by)


class BibRankAverageScoreRankingTest(unittest.TestCase):
    """Check bibrank average score ranking tools."""

    def setUp(self):
        # Test records from Article collection.
        test_scores = {86: [5, 5, 4, 3, 1, 1, 2, 5, 4, 4, 2],
                       87: [1, 2, 2, 5, 5, 5, 4, 3, 3, 3, 4, 5, 5, 1, 2],
                       91: [5, 5, 1, 1, 2, 3],
                       89: [5, 4, 1, 1, 4, 5, 2, 2],
                       90: [4, 4, 4, 3, 2, 1],
                       92: [4, 4, 4, 3, 3, 1, 5, 1],
                       94: [5, 5, 5, 5, 3],
                       95: [1, 2, 3, 4, 5, 3, 4, 4, 2],
                       96: [4, 3, 5, 5, 5, 2, 4],
                       97: [2, 3, 5, 5, 4, 4, 4, 3, 2, 4, 5, 1, 3]}

        # Clean tables before test starts.
        run_sql("delete from cmtRECORDCOMMENT")
        # Clean rank method data.
        run_sql("DELETE from rnkMETHODDATA WHERE id_rnkMETHOD in (SELECT id from rnkMETHOD WHERE name = 'average_score')")

        # Construct test table with test scores.
        query = "INSERT into cmtRECORDCOMMENT(id_bibrec, id_user, star_score) VALUES(%s, 1, %s)"
        for recid in test_scores:
            star_scores = test_scores[recid]
            for score in star_scores:
                run_sql(query, (recid, score,))

        command = "%s/bibrank" % CFG_BINDIR
        proc = Popen([command, "-u", "admin"])
        proc.wait()

        # Manually run the bibrank task! Just imitate bibsched's operations.
        task_id = get_last_taskid()
        proc = Popen([command, str(task_id)])
        proc.wait()

    def tearDown(self):
        query = "DELETE from cmtRECORDCOMMENT"
        run_sql(query)

    def test_search_results_ranked_by_average_score(self):
        """bibrank - search results ranked by average score"""

        expected_result = ['94', '96', '97', '87', '86', '92', '95', '90',
                           '89', '91']
        browser = Browser()
        browser.open(CFG_SITE_URL + "/search?ln=en&cc=Articles&rm=average_score&rg=10&of=hx")
        search_response = browser.response().read()

        regex = re.compile("@article{[\w]*:([\d]+),")
        search_results = regex.findall(search_response)

        if expected_result != search_results:
            self.fail("Expected to see in order %s, got %s." % \
                      (expected_result, search_results))


class BibRankRecordViewRankingTest(unittest.TestCase):
    """Check bibrank record view ranking tools."""

    def setUp(self):
        # Test records from Article collection.
        dummy_client = 3140802413
        test_records = {94: 10,
                        96: 12,
                        97: 19,
                        87: 5,
                        86: 23,
                        92: 14,
                        95: 19,
                        90: 28,
                        89: 18,
                        91: 9}

        # Clean tables before test starts.
        run_sql("DELETE from rnkPAGEVIEWS")
        # Clean rank method data.
        run_sql("DELETE from rnkMETHODDATA WHERE id_rnkMETHOD in (SELECT id from rnkMETHOD WHERE name = 'record_view')")

        # Construct test table with test scores.
        query = "insert into rnkPAGEVIEWS(id_bibrec, id_user, client_host, view_time) values(%s, 1, %s, %s)"
        for recid in test_records:
            for elem in range(0, test_records[recid]):
                cur_time = str(datetime.now())
                run_sql(query, (recid, dummy_client, cur_time))
                dummy_client = dummy_client + 1

        command = "%s/bibrank" % CFG_BINDIR
        proc = Popen([command, "-u", "admin"])
        proc.wait()

        # Manually run the bibrank task! Just imitate bibsched's operations.
        task_id = get_last_taskid()
        proc = Popen([command, str(task_id)])
        proc.wait()

    def tearDown(self):
        query = "DELETE from rnkPAGEVIEWS"
        run_sql(query)

    def test_search_results_ranked_by_view_count(self):
        """bibrank - search results ranked by view count"""

        expected_result = ['90', '86', '97', '95', '89', '92', '96', '94',
                           '91', '87']
        browser = Browser()
        browser.open(CFG_SITE_URL + "/search?ln=en&cc=Articles+%26+Preprints&rm=record_view&rg=10&of=hx")
        search_response = browser.response().read()

        regex = re.compile("@article{[\w]*:([\d]+),")
        search_results = regex.findall(search_response)

        if expected_result != search_results:
            self.fail("Expected to see in order %s, got %s." % \
                      (expected_result, search_results))


TESTS = [BibRankWebPagesAvailabilityTest,
         BibRankIntlMethodNames,
         BibRankCitationRankingTest,
         BibRankExtCitesTest,
         BibRankAverageScoreRankingTest,
         BibRankRecordViewRankingTest]


if not get_external_word_similarity_ranker():
    TESTS.append(BibRankWordSimilarityRankingTest)


TEST_SUITE = make_test_suite(*TESTS)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE, warn_user=True)
