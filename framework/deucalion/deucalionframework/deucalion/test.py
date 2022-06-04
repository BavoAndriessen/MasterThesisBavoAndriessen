import unittest
from prometheus_client.parser import text_string_to_metric_families, text_fd_to_metric_families


# run tests with: python -m unittest deucalionframework/PrometheusTargetScraper.py
class TestScraper(unittest.TestCase):
    def testFile(self):
        file = open('prom_exposition_example.txt', 'r')
        metrics = text_fd_to_metric_families(file)
        count = 0
        for family in metrics:
            for sample in family.samples:
                count += 1
        self.assertEqual(count, 20)


if __name__ == '__main__':
    unittest.main()
