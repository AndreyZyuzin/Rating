# Generated by Django 4.2 on 2023-08-16 11:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kaggle', '0008_alter_shootout_numb_winner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shootout',
            old_name='numb_winner',
            new_name='choice_winner',
        ),
    ]