# Generated by Django 3.1.1 on 2020-10-03 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JobAdds',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(default='')),
                ('phone', models.CharField(max_length=50)),
                ('heading', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=15)),
                ('user_since', models.CharField(max_length=50)),
                ('price', models.CharField(max_length=50)),
                ('link', models.SlugField()),
                ('time', models.CharField(default='10/03/2020', max_length=20)),
            ],
        ),
    ]
