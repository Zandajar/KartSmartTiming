import unittest
from Data_Classes.driver import Driver


class TestDriver(unittest.TestCase):

    def setUp(self):
        self.driver = Driver(place=1, name="Max Verstappen", kart_id=33)

    def test_initialization(self):
        self.assertEqual(self.driver.get_place(), 1)
        self.assertEqual(self.driver.get_name(), "Max Verstappen")
        self.assertEqual(self.driver.get_kart_id(), 33)
        self.assertEqual(self.driver.get_lap_time(), [])

    def test_set_place(self):
        self.driver.set_place(2)
        self.assertEqual(self.driver.get_place(), 2)
        self.driver.set_place(3)
        self.assertEqual(self.driver.get_place(), 3)

    def test_set_new_kart_id(self):
        self.driver.set_new_kart_id(1)
        self.assertEqual(self.driver.get_kart_id(), 1)
        self.driver.set_new_kart_id(99)
        self.assertEqual(self.driver.get_kart_id(), 99)

    def test_add_time(self):
        self.assertEqual(self.driver.get_lap_time(), [])
        self.driver.add_time(60.5)
        self.assertEqual(self.driver.get_lap_time(), [60.5])
        self.driver.add_time(59.8)
        self.driver.add_time(61.2)
        self.assertEqual(self.driver.get_lap_time(), [60.5, 59.8, 61.2])

    def test_get_methods(self):
        self.assertEqual(self.driver.get_name(), "Max Verstappen")
        self.assertEqual(self.driver.get_kart_id(), 33)
        self.assertEqual(self.driver.get_lap_time(), [])

    def test_edge_cases(self):
        driver = Driver(1, "", 0)
        self.assertEqual(driver.get_name(), "")
        driver = Driver(None, None, 0)
        self.assertIsNone(driver.get_place())
        self.assertIsNone(driver.get_name())
        driver.add_time(None)
        self.assertEqual(driver.get_lap_time(), [None])
