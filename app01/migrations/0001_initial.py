# Generated by Django 3.2.9 on 2021-11-22 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_collation='utf8_general_ci', max_length=10)),
            ],
            options={
                'db_table': 'test',
                'managed': False,
            },
        ),
    ]