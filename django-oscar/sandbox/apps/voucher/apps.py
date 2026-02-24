from oscar.apps.voucher.apps import VoucherConfig as CoreVoucherConfig


class VoucherConfig(CoreVoucherConfig):
    name = "apps.voucher"
    label = "voucher"
    
    def ready(self):
        super().ready()
