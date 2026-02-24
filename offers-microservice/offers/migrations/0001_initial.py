
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Benefit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Percentage', 'Percentage discount'), ('Absolute', 'Fixed amount discount'), ('Fixed', 'Fixed price'), ('Multibuy', 'Multibuy offer'), ('FixedPrice', 'Fixed product price')], max_length=128)),
                ('value', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('max_affected_items', models.PositiveIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Count', 'Anzahl Produkte'), ('Value', 'Warenkorbwert'), ('Coverage', 'Produktabdeckung')], max_length=128)),
                ('value', models.DecimalField(decimal_places=2, max_digits=12)),
            ],
        ),
        migrations.CreateModel(
            name='Range',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('slug', models.SlugField(max_length=128, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_public', models.BooleanField(default=False)),
                ('includes_all_products', models.BooleanField(default=False)),
                ('included_product_ids', models.JSONField(blank=True, default=list)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ConditionalOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('slug', models.SlugField(max_length=128, unique=True)),
                ('description', models.TextField(blank=True)),
                ('offer_type', models.CharField(choices=[('Site', 'Site Offer'), ('Voucher', 'Voucher Offer'), ('User', 'User Offer'), ('Session', 'Session Offer')], max_length=128)),
                ('status', models.CharField(choices=[('Open', 'Open'), ('Suspended', 'Suspended'), ('Consumed', 'Consumed')], default='Open', max_length=64)),
                ('priority', models.IntegerField(default=0)),
                ('start_datetime', models.DateTimeField(blank=True, null=True)),
                ('end_datetime', models.DateTimeField(blank=True, null=True)),
                ('max_global_applications', models.PositiveIntegerField(blank=True, null=True)),
                ('num_applications', models.PositiveIntegerField(default=0)),
                ('total_discount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('benefit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='offers.benefit')),
                ('condition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='offers.condition')),
            ],
            options={
                'ordering': ['-priority', 'name'],
            },
        ),
        migrations.AddField(
            model_name='condition',
            name='range',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='offers.range'),
        ),
        migrations.AddField(
            model_name='benefit',
            name='range',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='offers.range'),
        ),
    ]
