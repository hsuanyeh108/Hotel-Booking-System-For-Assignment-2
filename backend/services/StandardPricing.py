# Factory Pattern
# Using PricingRuleFactory choose new PricingRule subclass

#OOP
#Abstract class PricingRule 

class StandardPricing:
    label = "Standard Rate"
    description = "Base price x number of nights, no surcharge or discount."

    def apply(self, base_price, nights):
        return round(base_price * nights, 2)
    