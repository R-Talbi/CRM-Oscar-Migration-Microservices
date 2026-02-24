
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BillingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=255)),
                ('last_name', models.CharField(blank=True, max_length=255)),
                ('line1', models.CharField(max_length=255)),
                ('line2', models.CharField(blank=True, max_length=255)),
                ('line4', models.CharField(blank=True, max_length=255)),
                ('state', models.CharField(blank=True, max_length=255)),
                ('postcode', models.CharField(blank=True, max_length=64)),
                ('country', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name': 'Billing Address',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(db_index=True, max_length=128, unique=True)),
                ('customer_id', models.IntegerField(blank=True, null=True)),
                ('guest_email', models.EmailField(blank=True, max_length=254)),
                ('basket_id', models.IntegerField(blank=True, null=True)),
                ('currency', models.CharField(default='EUR', max_length=12)),
                ('total_incl_tax', models.DecimalField(decimal_places=2, max_digits=12)),
                ('total_excl_tax', models.DecimalField(decimal_places=2, max_digits=12)),
                ('shipping_incl_tax', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('shipping_excl_tax', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('shipping_tax_code', models.CharField(blank=True, max_length=64, null=True)),
                ('shipping_method', models.CharField(blank=True, max_length=128)),
                ('shipping_code', models.CharField(blank=True, max_length=128)),
                ('status', models.CharField(blank=True, max_length=100)),
                ('date_placed', models.DateTimeField(db_index=True)),
                ('billing_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.billingaddress')),
            ],
            options={
                'ordering': ['-date_placed'],
            },
        ),
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partner_name', models.CharField(blank=True, max_length=128)),
                ('partner_sku', models.CharField(max_length=128)),
                ('partner_line_reference', models.CharField(blank=True, max_length=128)),
                ('partner_line_notes', models.TextField(blank=True)),
                ('stockrecord_id', models.IntegerField(blank=True, null=True)),
                ('product_id', models.IntegerField(blank=True, null=True)),
                ('title', models.CharField(max_length=255)),
                ('upc', models.CharField(blank=True, max_length=128, null=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('line_price_incl_tax', models.DecimalField(decimal_places=2, max_digits=12)),
                ('line_price_excl_tax', models.DecimalField(decimal_places=2, max_digits=12)),
                ('line_price_before_discounts_incl_tax', models.DecimalField(decimal_places=2, max_digits=12)),
                ('line_price_before_discounts_excl_tax', models.DecimalField(decimal_places=2, max_digits=12)),
                ('unit_price_incl_tax', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('unit_price_excl_tax', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('tax_code', models.CharField(blank=True, max_length=64, null=True)),
                ('status', models.CharField(blank=True, max_length=255)),
                ('num_allocated', models.PositiveIntegerField(default=0)),
                ('allocation_cancelled', models.BooleanField(default=False)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='orders.order')),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='ShippingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=255)),
                ('last_name', models.CharField(blank=True, max_length=255)),
                ('line1', models.CharField(max_length=255)),
                ('line2', models.CharField(blank=True, max_length=255)),
                ('line3', models.CharField(blank=True, max_length=255)),
                ('line4', models.CharField(blank=True, max_length=255)),
                ('state', models.CharField(blank=True, max_length=255)),
                ('postcode', models.CharField(blank=True, max_length=64)),
                ('country', models.CharField(max_length=128)),
                ('phone_number', models.CharField(blank=True, max_length=32)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Shipping Address',
            },
        ),
        migrations.CreateModel(
            name='OrderStatusChange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_status', models.CharField(blank=True, max_length=100)),
                ('new_status', models.CharField(blank=True, max_length=100)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_changes', to='orders.order')),
            ],
            options={
                'ordering': ['-date_created'],
            },
        ),
        migrations.CreateModel(
            name='OrderNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.IntegerField(blank=True, null=True)),
                ('note_type', models.CharField(blank=True, max_length=128)),
                ('message', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='orders.order')),
            ],
            options={
                'ordering': ['-date_updated'],
            },
        ),
        migrations.CreateModel(
            name='OrderLineAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_name', models.CharField(max_length=128)),
                ('type', models.CharField(max_length=128)),
                ('value', models.JSONField()),
                ('line', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='orders.orderline')),
            ],
        ),
        migrations.CreateModel(
            name='OrderDiscount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('Basket', 'Basket'), ('Shipping', 'Shipping'), ('Deferred', 'Deferred')], default='Basket', max_length=64)),
                ('offer_id', models.PositiveIntegerField(blank=True, null=True)),
                ('offer_name', models.CharField(blank=True, db_index=True, max_length=128)),
                ('voucher_id', models.PositiveIntegerField(blank=True, null=True)),
                ('voucher_code', models.CharField(blank=True, db_index=True, max_length=128)),
                ('frequency', models.PositiveIntegerField(null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('message', models.TextField(blank=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discounts', to='orders.order')),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.shippingaddress'),
        ),
    ]
