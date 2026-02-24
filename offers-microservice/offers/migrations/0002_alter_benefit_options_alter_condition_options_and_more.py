
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='benefit',
            options={'verbose_name': 'Benefit'},
        ),
        migrations.AlterModelOptions(
            name='condition',
            options={'verbose_name': 'Condition'},
        ),
        migrations.AlterModelOptions(
            name='conditionaloffer',
            options={'ordering': ['-priority', 'pk']},
        ),
        migrations.AlterModelOptions(
            name='range',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='benefit',
            name='proxy_class',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='condition',
            name='proxy_class',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='conditionaloffer',
            name='exclusive',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='conditionaloffer',
            name='max_basket_applications',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conditionaloffer',
            name='max_discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='conditionaloffer',
            name='max_user_applications',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conditionaloffer',
            name='num_orders',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='conditionaloffer',
            name='redirect_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='range',
            name='excluded_product_ids',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='benefit',
            name='type',
            field=models.CharField(blank=True, choices=[('Percentage', 'Discount is a percentage off of the product value'), ('Absolute', 'Discount is a fixed amount off of the basket total'), ('Fixed', 'Discount is a fixed amount off of the product value'), ('Multibuy', 'Cheapest product for free'), ('Fixed price', 'Products for a fixed price'), ('Shipping absolute', 'Fixed amount off shipping'), ('Shipping fixed price', 'Fixed price shipping'), ('Shipping percentage', 'Percentage off shipping')], max_length=128),
        ),
        migrations.AlterField(
            model_name='condition',
            name='type',
            field=models.CharField(blank=True, choices=[('Count', 'Depends on number of items in basket'), ('Value', 'Depends on value of items in basket'), ('Coverage', 'Needs distinct items from range')], max_length=128),
        ),
        migrations.AlterField(
            model_name='condition',
            name='value',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='conditionaloffer',
            name='benefit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='offers.benefit'),
        ),
        migrations.AlterField(
            model_name='conditionaloffer',
            name='condition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='offers.condition'),
        ),
        migrations.AlterField(
            model_name='conditionaloffer',
            name='name',
            field=models.CharField(max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name='conditionaloffer',
            name='offer_type',
            field=models.CharField(choices=[('Site', 'Site offer - available to all users'), ('Voucher', 'Voucher offer - only with voucher code'), ('User', 'User offer - available to certain users'), ('Session', 'Session offer - temporary offer')], default='Site', max_length=128),
        ),
        migrations.AlterField(
            model_name='conditionaloffer',
            name='priority',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='range',
            name='name',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
