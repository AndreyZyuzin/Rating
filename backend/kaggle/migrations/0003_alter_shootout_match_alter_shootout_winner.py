# Generated by Django 4.2 on 2023-08-16 06:18

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kaggle', '0002_alter_match_goals1_alter_match_goals2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shootout',
            name='match',
            field=models.ForeignKey(help_text='Матч', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='kaggle.match', verbose_name='Матч'),
        ),
        migrations.AlterField(
            model_name='shootout',
            name='winner',
            field=models.SmallIntegerField(help_text='Победитель', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(2)], verbose_name='Победитель'),
        ),
    ]
