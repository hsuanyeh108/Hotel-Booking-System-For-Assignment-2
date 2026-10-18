from backend.services.PricingRuleFactory import PricingRuleFactory


def test_standard_price():
    rule = PricingRuleFactory.get_rule("standard")
    total = rule.apply(100, 3)
    assert total == 300


def test_long_stay_discount():
    rule = PricingRuleFactory.get_rule("long_stay")
    total = rule.apply(100, 7)
    assert total == 630