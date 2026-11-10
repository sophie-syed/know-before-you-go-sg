import unittest
from unittest.mock import Mock, patch

from kbyg.core import STARTING_AREAS, haversine_km, load_places, plan_route, visit_status
from kbyg.onemap import walking_route
from kbyg.ui import REQUIRED_DISCLAIMER


class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.places = load_places()

    def test_loads_both_official_datasets(self):
        self.assertEqual(len(self.places), 177)
        self.assertEqual(
            {place.place_type for place in self.places},
            {"National monument", "Historic site"},
        )

    def test_damaged_apostrophes_are_repaired(self):
        self.assertFalse(any("�" in place.description for place in self.places))
        oxley = next(place for place in self.places if place.name == "38 Oxley Road")
        self.assertIn("Singapore’s transition", oxley.description)

    def test_haversine_zero(self):
        point = STARTING_AREAS["Telok Ayer"]
        self.assertAlmostEqual(haversine_km(point, point), 0.0)

    def test_route_respects_limits(self):
        route = plan_route(
            self.places,
            "Telok Ayer",
            available_minutes=120,
            max_walking_km=2.5,
            interests=["Multicultural history", "Architecture"],
        )
        self.assertGreaterEqual(len(route.stops), 2)
        self.assertLessEqual(route.estimated_minutes, 120)
        self.assertLessEqual(route.total_distance_km, 2.5)

    def test_route_is_repeatable(self):
        kwargs = dict(
            places=self.places,
            start_name="Civic District",
            available_minutes=90,
            max_walking_km=2.0,
            interests=["Civic and political history"],
        )
        first = plan_route(**kwargs)
        second = plan_route(**kwargs)
        self.assertEqual(
            [stop.place.place_id for stop in first.stops],
            [stop.place.place_id for stop in second.stops],
        )

    def test_required_disclaimer_is_present(self):
        self.assertIn("IMPORTANT NOTICE", REQUIRED_DISCLAIMER)
        self.assertIn("prototype developed for educational purposes only", REQUIRED_DISCLAIMER)
        self.assertIn("LLM may generate inaccurate or incorrect information", REQUIRED_DISCLAIMER)

    def test_explicit_historic_site_statuses_are_distinguished(self):
        by_name = {place.name: place for place in self.places}
        self.assertTrue(visit_status(by_name["National Theatre"]).startswith("Commemorative site"))
        self.assertTrue(visit_status(by_name["Pondok Peranakan Gelam Club"]).startswith("Former location"))
        self.assertIn("No separate", visit_status(by_name["Al-Abrar Mosque"]))

    @patch("kbyg.onemap._secret", return_value="test-token")
    @patch("kbyg.onemap.requests.get")
    def test_onemap_aggregates_walking_legs(self, mocked_get, _mocked_secret):
        first_response = Mock()
        first_response.raise_for_status.return_value = None
        first_response.json.return_value = {
            "route_summary": {"total_distance": 400, "total_time": 300}
        }
        second_response = Mock()
        second_response.raise_for_status.return_value = None
        second_response.json.return_value = {
            "route_summary": {"total_distance": 600, "total_time": 420}
        }
        mocked_get.side_effect = [first_response, second_response]

        result = walking_route(STARTING_AREAS["Telok Ayer"], self.places[:2])
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result.distance_km, 1.0)
        self.assertEqual(result.duration_minutes, 12)


if __name__ == "__main__":
    unittest.main()

