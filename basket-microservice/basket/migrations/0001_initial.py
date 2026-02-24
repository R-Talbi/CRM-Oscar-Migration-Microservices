
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('Open', 'Open'), ('Merged', 'Merged'), ('Saved', 'Saved'), ('Frozen', 'Frozen'), ('Submitted', 'Submitted')], default='Open', max_length=128)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_merged', models.DateTimeField(blank=True, null=True)),
                ('date_submitted', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-date_created'],
            },
        ),
        migrations.CreateModel(
            name='BasketLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.IntegerField()),
                ('product_name', models.CharField(max_length=255)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('offer_id', models.IntegerField(blank=True, null=True)),
                ('basket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='basket.basket')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
