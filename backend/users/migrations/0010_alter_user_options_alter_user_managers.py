# Generated by Django 4.1.6 on 2023-03-02 20:01

from django.db import migrations
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_subscription_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['username'], 'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', users.models.CustomUserManager()),
            ],
        ),
    ]
