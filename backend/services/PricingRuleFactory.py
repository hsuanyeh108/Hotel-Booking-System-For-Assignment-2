# Factory Pattern
# Using PricingRuleFactory choose new PricingRule subclass

#OOP
#Abstract class PricingRule 

from backend.services.StandardPricing import StandardPricing
from backend.services.WeekendPricing import WeekendPricing
from backend.services.LongStayPricing import LongStayPricing

class PricingRuleFactory:
    @staticmethod
    def get_rule(rule_type):
        if rule_type == "standard":
            return StandardPricing()
        elif rule_type == "weekend":
            return WeekendPricing()
        elif rule_type == "long_stay":
            return LongStayPricing()
        else:
            raise ValueError(f"Unkown pricing rule '{rule_type}'")

    @staticmethod
    def list_rule():
        rules = []
        for type in ["standard", "weekend", "long_stay"]:
            rule = PricingRuleFactory.get_rule(type)
            rules.append({"type":type, "label": rule.label, "description": rule.description})
        return rules