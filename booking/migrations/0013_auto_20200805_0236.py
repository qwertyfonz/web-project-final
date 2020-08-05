# Generated by Django 3.0.7 on 2020-08-05 02:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0012_hotel_image'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Trip',
            new_name='FlightBooking',
        ),
        migrations.CreateModel(
            name='HotelBooking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('totalAmount', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('hotel', models.ManyToManyField(to='booking.Hotel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]