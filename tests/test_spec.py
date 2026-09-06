import unittest

from githood.spec import SpecError, parse

GOOD = """# Momentum Paper Trader
broker: robinhood
symbols: AAPL, MSFT
max_position: 10%
rules:
- buy the crossover
- sell the cross back
"""


class SpecTest(unittest.TestCase):
    def test_reads_the_basics(self):
        spec = parse(GOOD)
        self.assertEqual(spec.name, "Momentum Paper Trader")
        self.assertEqual(spec.slug, "momentum-paper-trader")
        self.assertEqual(spec.broker, "robinhood")
        self.assertEqual(spec.symbols, ("AAPL", "MSFT"))
        self.assertAlmostEqual(spec.max_position, 0.10)
        self.assertEqual(len(spec.rules), 2)

    def test_keeps_unknown_keys(self):
        spec = parse(GOOD + "owner: wast3\n")
        self.assertEqual(spec.extra["owner"], "wast3")

    def test_rules_are_required(self):
        with self.assertRaises(SpecError):
            parse("# No Rules\nbroker: paper\n")

    def test_unknown_broker_is_refused(self):
        with self.assertRaises(SpecError):
            parse(GOOD.replace("robinhood", "etrade"))

    def test_silly_risk_is_refused(self):
        with self.assertRaises(SpecError):
            parse(GOOD.replace("10%", "400%"))
