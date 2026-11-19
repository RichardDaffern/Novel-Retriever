"""Synthetic offline tests for the one-time 58-book Yup continuation."""
from __future__ import annotations

import copy
import unittest

from tools import overnight_queue as q
from tools.yup_remaining_resume import prepare_remaining


def example_reports():
    yup = [
        {"title": f"Yup Book {i:03d}",
         "url": q.candidate_urls(f"Yup Book {i:03d}")[0],
         "tier": "Yup", "evidence": "public_listing_exact_title"}
        for i in range(108)
    ]
    idk = [
        {"title": f"Idk Book {i:03d}",
         "url": q.candidate_urls(f"Idk Book {i:03d}")[0],
         "tier": "Idk", "evidence": "public_listing_exact_title"}
        for i in range(50)
    ]
    source = {"version": 1, "campaign": q.CAMPAIGN,
              "verified": yup + idk,
              "summary": {"verified": 158, "global_exclusions_checked": 90}}
    previous = {"version": 1, "campaign": q.CAMPAIGN, "tier": "Yup",
                "approved_source_count": 108,
                "reason": "overnight_dispatch_budget_exhausted",
                "submitted": [
                    {"titles": [r["title"] for r in yup[n:n + 2]],
                     "urls": [r["url"] for r in yup[n:n + 2]]}
                    for n in range(0, 50, 2)
                ], "held": yup[50:]}
    return source, previous


class RemainingYupTests(unittest.TestCase):
    def test_only_58_originally_held_records_are_emitted(self):
        source, previous = example_reports()
        planned = prepare_remaining(source, previous, set())
        self.assertEqual(len(planned["verified"]), 58)
        self.assertEqual(planned["verified"], previous["held"])
        self.assertEqual(planned["already_known_skipped"], 0)
        self.assertNotIn(source["verified"][0], planned["verified"])
        self.assertTrue(all(r["tier"] == "Yup" for r in planned["verified"]))

    def test_completed_title_is_skipped_without_force(self):
        source, previous = example_reports()
        completed = q.norm(previous["held"][0]["title"])
        planned = prepare_remaining(source, previous, {completed})
        self.assertEqual(len(planned["verified"]), 57)
        self.assertEqual(planned["already_known_skipped"], 1)
        self.assertNotIn(previous["held"][0], planned["verified"])

    def test_rejects_unverified_forged_and_duplicate_entries(self):
        source, previous = example_reports()
        cases = []
        forged = copy.deepcopy(previous)
        forged["held"][0]["url"] = q.candidate_urls("Other Title")[0]
        cases.append((source, forged))
        duplicated = copy.deepcopy(previous)
        duplicated["held"][0] = duplicated["held"][1]
        cases.append((source, duplicated))
        missing = copy.deepcopy(previous)
        missing["held"] = missing["held"][:-1]
        cases.append((source, missing))
        changed_source = copy.deepcopy(source)
        changed_source["verified"][55]["url"] = q.candidate_urls("Wrong Book")[0]
        cases.append((changed_source, previous))
        tampered = copy.deepcopy(previous)
        tampered["submitted"][0]["urls"][0] = q.candidate_urls("Fake Book")[0]
        cases.append((source, tampered))
        for source_case, previous_case in cases:
            with self.subTest(kind=str(previous_case["held"][0])[:35]):
                with self.assertRaises(q.QueueError):
                    prepare_remaining(source_case, previous_case, set())


if __name__ == "__main__":
    unittest.main()
