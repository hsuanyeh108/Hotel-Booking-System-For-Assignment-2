from backend.services.PricingRuleFactory import PricingRuleFactory


def test_standard_price():
    rule = PricingRuleFactory.get_rule("standard")
    total = rule.apply(150, 3)
    assert total == 450

def test_weekend_price():
    rule = PricingRuleFactory.get_rule("weekend")
    total = rule.apply(150, 3)
    assert total == 540


def test_long_stay_discount():
    rule = PricingRuleFactory.get_rule("long_stay")
    total = rule.apply(150, 7)
    assert total == 945


# polymorphism the same rule.apply() call should have different result
def test_polymorphism():
    expected = {"standard": 1050, "weekend": 1260, "long_stay": 945}
    for rule_type in ["standard", "weekend", "long_stay"]:
        rule = PricingRuleFactory.get_rule(rule_type)
        assert rule.apply(150, 7) == expected[rule_type]