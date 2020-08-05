# Generated by Django 3.0.7 on 2020-08-04 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0010_auto_20200804_1249'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=64)),
                ('address', models.CharField(max_length=100)),
                ('price', models.IntegerField(default=0)),
            ],
        ),
        migrations.RemoveField(
            model_name='flight',
            name='capacity',
        ),
        migrations.RemoveField(
            model_name='flight',
            name='numOfPassengers',
        ),
    ]