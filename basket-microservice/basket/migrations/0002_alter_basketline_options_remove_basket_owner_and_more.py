
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('basket', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='basketline',
            options={'ordering': ['date_created', 'pk']},
        ),
        migrations.RemoveField(
            model_name='basket',
            name='owner',
        ),
        migrations.AddField(
            model_name='basket',
            name='customer_email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.AddField(
            model_name='basket',
            name='customer_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='basket',
            name='voucher_codes',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='basketline',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='basketline',
            name='date_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='basketline',
            name='discount_value',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12),
        ),
        migrations.AddField(
            model_name='basketline',
            name='line_reference',
            field=models.SlugField(default='', max_length=128),
        ),
        migrations.AddField(
            model_name='basketline',
            name='price_currency',
            field=models.CharField(default='EUR', max_length=12),
        ),
        migrations.AddField(
            model_name='basketline',
            name='price_excl_tax',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='basketline',
            name='price_incl_tax',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='basketline',
            name='product_title',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='basketline',
            name='stockrecord_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='basketline',
            name='tax_code',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='basket',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='basket',
            name='status',
            field=models.CharField(choices=[('Open', 'Open - currently active'), ('Merged', 'Merged - superceded by another basket'), ('Saved', 'Saved - for items to be purchased later'), ('Frozen', 'Frozen - cannot be modified'), ('Submitted', 'Submitted - has been ordered')], default='Open', max_length=128),
        ),
        migrations.AlterUniqueTogether(
            name='basketline',
            unique_together={('basket', 'line_reference')},
        ),
        migrations.CreateModel(
            name='BasketLineAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_name', models.CharField(max_length=128)),
                ('value', models.JSONField()),
                ('line', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='basket.basketline')),
            ],
            options={
                'verbose_name': 'Basket Line Attribute',
            },
        ),
        migrations.RemoveField(
            model_name='basketline',
            name='price',
        ),
        migrations.RemoveField(
            model_name='basketline',
            name='product_name',
        ),
    ]
