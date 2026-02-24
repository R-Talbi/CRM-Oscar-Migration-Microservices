from oscar.apps.payment.apps import PaymentConfig as CorePaymentConfig

class PaymentConfig(CorePaymentConfig):
    name = 'apps.payment'
    label = 'payment'
