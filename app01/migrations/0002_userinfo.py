# Generated by Django 3.2.9 on 2021-11-23 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Userinfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openid', models.CharField(max_length=255)),
                ('ipname', models.CharField(max_length=255)),
                ('gender', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'userinfo',
                'managed': False,
            },
        ),
    ]
