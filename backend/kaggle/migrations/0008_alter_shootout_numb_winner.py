# Generated by Django 4.2 on 2023-08-16 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kaggle', '0007_alter_shootout_match'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shootout',
            name='numb_winner',
            field=models.SmallIntegerField(choices=[(0, 'Unknown'), (1, 'First'), (2, 'Second')], default=0, help_text='Победитель', verbose_name='Победитель'),
        ),
    ]