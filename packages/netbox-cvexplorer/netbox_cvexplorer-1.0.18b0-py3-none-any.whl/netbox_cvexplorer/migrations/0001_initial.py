from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CVE',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cve_number', models.CharField(max_length=20, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('score', models.DecimalField(decimal_places=1, max_digits=4)),
                ('status', models.IntegerField(choices=[(0, 'Offen'), (1, 'Erledigt')])),
                ('date_imported', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
