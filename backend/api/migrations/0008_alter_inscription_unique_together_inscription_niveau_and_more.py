from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_remove_inscription_unique_together'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Ajouter niveau EN PREMIER
        migrations.AddField(
            model_name='inscription',
            name='niveau',
            field=models.CharField(
                choices=[('A', 'Niveau A'), ('B', 'Niveau B'), ('C', 'Niveau C')],
                default='A',
                max_length=1,
            ),
            preserve_default=False,
        ),

        # 2. Supprimer formation
        migrations.RemoveField(
            model_name='inscription',
            name='formation',
        ),

        # 3. Supprimer les doublons (garder la plus récente par utilisateur+niveau)
        migrations.RunSQL(
            sql="""
                DELETE FROM api_inscription
                WHERE id NOT IN (
                    SELECT MAX(id)
                    FROM api_inscription
                    GROUP BY utilisateur_id, niveau
                );
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        # 4. unique_together EN DERNIER (après dédoublonnage)
        migrations.AlterUniqueTogether(
            name='inscription',
            unique_together={('utilisateur', 'niveau')},
        ),
    ]