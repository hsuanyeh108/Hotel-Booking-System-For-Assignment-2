# Factory Pattern
# Using PricingRuleFactory choose new PricingRule subclass

#OOP
#Abstract class PricingRule 

class LongStayPricing:
    label = "Long Stay Discount(7+ nights: -10%)"
    description = "10% off the total when staying 7 nights or more."

    def apply(self, base_price, nights):

        total = base_price * nights
        if nights >= 7:
            total = total *0.9
            return round(total, 2)
            