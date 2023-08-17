# Generated by Django 4.2 on 2023-08-17 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kaggle', '0005_remove_shootout_id_alter_shootout_match'),
    ]

    operations = [
        migrations.AddField(
            model_name='shootout',
            name='id',
            field=models.BigAutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='shootout',
            name='match',
            field=models.OneToOneField(help_text='Матч', on_delete=django.db.models.deletion.CASCADE, related_name='shootout', to='kaggle.match', verbose_name='Матч'),
        ),
    ]
