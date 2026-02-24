from oscar.apps.order.apps import OrderConfig as CoreOrderConfig

class OrderConfig(CoreOrderConfig):
    name = 'apps.order'
    label = 'order'
