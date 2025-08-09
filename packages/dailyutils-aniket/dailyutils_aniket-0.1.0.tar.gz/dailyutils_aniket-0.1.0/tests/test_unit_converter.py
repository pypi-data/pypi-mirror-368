import unittest
from dailyutils.unit_converter import convert_length, convert_weight, convert_temperature

class TestUnitConverter(unittest.TestCase):

    def test_length_conversion(self):
        self.assertAlmostEqual(convert_length(1, 'km', 'm'), 1000)
        self.assertAlmostEqual(convert_length(12, 'inch', 'foot'), 1, places=2)

    def test_weight_conversion(self):
        self.assertAlmostEqual(convert_weight(1000, 'g', 'kg'), 1)
        self.assertAlmostEqual(convert_weight(1, 'lb', 'oz'), 16, delta=1)  

    def test_temperature_conversion(self):
        self.assertAlmostEqual(convert_temperature(0, 'C', 'F'), 32)
        self.assertAlmostEqual(convert_temperature(100, 'C', 'K'), 373.15)
        self.assertAlmostEqual(convert_temperature(32, 'F', 'C'), 0)

if __name__ == '__main__':
    unittest.main()
