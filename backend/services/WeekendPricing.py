# Factory Pattern
# Using PricingRuleFactory choose new PricingRule subclass

#OOP
#Abstract class PricingRule 

class WeekendPricing:
    label = "Weekend Surcharge(20%)"
    description = "Add a 20% surcharge to the total stay"

    def apply(self, base_price, nights):
        return round(base_price * nights * 1.2, 2)