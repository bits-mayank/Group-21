# Generated by Django 3.1.6 on 2021-02-15 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0007_quiz_isshuffle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiztakers',
            name='completed',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]