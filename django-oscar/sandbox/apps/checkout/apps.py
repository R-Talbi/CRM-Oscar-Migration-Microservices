from oscar.apps.checkout.apps import CheckoutConfig as CoreCheckoutConfig

class CheckoutConfig(CoreCheckoutConfig):
    name = "apps.checkout"
    label = "checkout"
