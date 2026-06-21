from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_parametres_niveau_a_desc_parametres_niveau_a_items_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='inscription',
            unique_together=set(),
        ),
    ]