# Generated by Django 4.2 on 2023-08-18 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kaggle', '0008_alter_shootout_options'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='match',
            constraint=models.UniqueConstraint(fields=('date', 'team1', 'team2'), name='unique_match'),
        ),
    ]
