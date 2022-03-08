"""
Run with::

    grunt exec:test_server:test_modules_sponsorship_search.py
"""
import datetime
import unittest
import operator
import uuid

from gluon.globals import Request

from applications.OZtree.tests.unit import util

import sponsorship
import sponsorship_search

def parsed_ss(search_term, **kwargs):
    """Make a query, parse headers from results"""
    def parse(r, headers):
        """Turn a reservations result row into a dict matching (headers)"""
        out = {}
        for k, i in headers.items():
            out[k] = r[i]
        return out

    results = sponsorship_search.search_sponsor(search_term, **kwargs)
    return [parse(r, results['headers']) for r in results['reservations']]


class TestSponsorshipSearch(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        request = Request(dict())
        util.clear_unittest_sponsors()

        # Allow sponsorship by default
        util.set_allow_sponsorship(1)
        util.set_maintenance_mins(0)
        util.set_reservation_time_limit_mins(6)
        self.assertEqual(sponsorship.sponsorship_enabled(), True)

    def tearDown(self):
        util.clear_unittest_sponsors()
        # Remove anything created as part of tests
        db.rollback()

    def test_search_sponsor_noterm(self):
        """No search term returns {}"""
        out = sponsorship_search.search_sponsor("")
        self.assertEqual(out, {})

    def test_search_sponsor_expire(self):
        """Expired leaves don't show up"""
        search_term = str(uuid.uuid4())  # Something unique to search for
        ig = operator.itemgetter('OTT_ID', 'verified_name')

        # Can't find anything initially
        self.assertEqual(parsed_ss(search_term), [])

        # Buy an OTT with the search term, we see it
        user1, email1 = 'bettyunittestexamplecom', 'betty@unittest.example.com'
        r1 = util.purchase_reservation(basket_details=dict(
            e_mail=email1,
            user_donor_name=user1,
            user_sponsor_name=search_term,
            user_sponsor_kind='by',
        ))[0]
        self.assertEqual([ig(r) for r in parsed_ss(search_term)], [
            (r1.OTT_ID, search_term),
        ])

        # Move forward in time past expiry, still there.
        current.request.now = (current.request.now + datetime.timedelta(days=r1.sponsorship_duration_days + 10))
        self.assertEqual([ig(r) for r in parsed_ss(search_term)], [
            (r1.OTT_ID, search_term),
        ])

        # Expire it properly, it's not
        sponsorship.reservation_expire(r1)
        self.assertEqual(parsed_ss(search_term), [])

if __name__ == '__main__':
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(TestSponsorshipSearch))
    unittest.TextTestRunner(verbosity=2).run(suite)