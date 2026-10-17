# Factory Pattern
# Using PricingRuleFactory choose new PricingRule subclass

#OOP
#Abstract class PricingRule 

from StandardPricing import StandardPricing
from WeekendPricing import WeekendPricing
from LongStayPricing import LongStayPricing

class PricingRuleFactory:
    @staticmethod
    def get_rule(rule_type):
        if rule_type == "standard":
            return StandardPricing
        elif rule_type == "weekend":
            return WeekendPricing
        elif rule_type == "long_stay":
            return LongStayPricing
        else:
            raise ValueError(f"Unkown pricing rule '{rule_type}'")

    @staticmethod
    def list_rule(rule_type):
        rules = []
        for type in ["standard", "weeken", "long_stay"]:
            rule = PricingRuleFactory.get_rule(type)
            rules.append({"type":type, "label": rule.label, "description": rule.description})
        return rules