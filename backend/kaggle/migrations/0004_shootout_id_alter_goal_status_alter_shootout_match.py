# Generated by Django 4.2 on 2023-08-17 11:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kaggle', '0003_goal_id_alter_goal_match'),
    ]

    operations = [
        migrations.AddField(
            model_name='shootout',
            name='id',
            field=models.BigAutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='goal',
            name='status',
            field=models.SmallIntegerField(choices=[(0, ''), (1, 'Penalty'), (2, 'Own goal')], default=0, help_text='Примечание', verbose_name='Прим.'),
        ),
        migrations.AlterField(
            model_name='shootout',
            name='match',
            field=models.OneToOneField(help_text='Матч', on_delete=django.db.models.deletion.CASCADE, related_name='shootout', to='kaggle.match', verbose_name='Матч'),
        ),
    ]
