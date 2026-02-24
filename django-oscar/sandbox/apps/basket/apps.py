from oscar.apps.basket.apps import BasketConfig as CoreBasketConfig

class BasketConfig(CoreBasketConfig):
    name = 'apps.basket'
    label = 'basket'
