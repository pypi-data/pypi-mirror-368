import unittest
from min_distance import calculate_min_distance

class TestMinDistance(unittest.TestCase):

    def test_known_distance(self):
        # Distance between New York (40.7128° N, 74.0060° W)
        # and London (51.5074° N, 0.1278° W) approx 5570 km
        ny_lat, ny_lon = 40.7128, -74.0060
        london_lat, london_lon = 51.5074, -0.1278
        
        distance = calculate_min_distance(ny_lat, ny_lon, london_lat, london_lon)
        
        # Allow a small margin of error
        self.assertAlmostEqual(distance, 5570, delta=10)

    def test_zero_distance(self):
        # Same points should return 0
        distance = calculate_min_distance(0, 0, 0, 0)
        self.assertEqual(distance, 0)

if __name__ == "__main__":
    unittest.main()
