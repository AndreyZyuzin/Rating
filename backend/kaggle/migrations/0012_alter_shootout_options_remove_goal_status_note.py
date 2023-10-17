# Generated by Django 4.2 on 2023-10-17 09:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kaggle', '0011_remove_shootout_caption'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shootout',
            options={'verbose_name': 'Послематчевые пенальти', 'verbose_name_plural': 'Пенальти'},
        ),
        migrations.RemoveField(
            model_name='goal',
            name='status',
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.SmallIntegerField(choices=[(0, 'None'), (1, 'Penalty'), (2, 'Own goal')], default=0, help_text='Примечание', verbose_name='Прим.')),
                ('goal', models.OneToOneField(help_text='Гол', on_delete=django.db.models.deletion.CASCADE, related_name='goal', to='kaggle.goal', verbose_name='Голы')),
            ],
        ),
    ]