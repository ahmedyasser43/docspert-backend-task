# Generated by Django 5.0.7 on 2024-07-15 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('balance', models.FloatField()),
                ('name', models.CharField(max_length=100)),
            ],
        ),
    ]
