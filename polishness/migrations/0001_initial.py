# Generated by Django 5.1.2 on 2024-10-11 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Monument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('library_id', models.CharField(max_length=100)),
                ('security_form', models.CharField(max_length=100)),
                ('location_accuracy', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('chronology', models.CharField(max_length=100)),
                ('function', models.CharField(max_length=100)),
                ('documents', models.CharField(max_length=100)),
                ('registration_date', models.CharField(max_length=100)),
                ('voivodeship', models.CharField(max_length=100)),
                ('county', models.CharField(max_length=100)),
                ('parish', models.CharField(max_length=100)),
                ('locality', models.CharField(max_length=100)),
                ('street', models.CharField(max_length=100)),
                ('address_number', models.CharField(max_length=100)),
                ('latitude', models.CharField(max_length=100)),
                ('longitude', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ('-name',),
            },
        ),
    ]