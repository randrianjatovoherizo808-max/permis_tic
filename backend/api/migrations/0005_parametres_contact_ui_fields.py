from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_parametres_photo_url_profil_photo_url_site_photo_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='parametres',
            name='whatsapp',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AddField(
            model_name='parametres',
            name='whatsapp_nom',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='parametres',
            name='slogan',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='parametres',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='parametres',
            name='facebook',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='parametres',
            name='footer_texte',
            field=models.CharField(blank=True, default='Centre de Formation Professionnelle', max_length=255),
        ),
    ]