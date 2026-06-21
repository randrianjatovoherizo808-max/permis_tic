"""
INSTRUCTIONS :
Supprimez le fichier 0001_initial.py existant et remplacez-le par ce fichier,
puis lancez :
    python manage.py migrate
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parametres',
            fields=[
                ('id',        models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('nom',       models.CharField(default='PERMIS TIC', max_length=200)),
                ('adresse',   models.TextField(blank=True)),
                ('telephone', models.CharField(blank=True, max_length=30)),
                ('email',     models.EmailField(blank=True, max_length=254)),
            ],
            options={'verbose_name_plural': 'Paramètres'},
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id',        models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('nom',       models.CharField(max_length=200)),
                ('adresse',   models.TextField(blank=True)),
                ('telephone', models.CharField(blank=True, max_length=30)),
                ('email',     models.EmailField(blank=True)),
                ('actif',     models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Formation',
            fields=[
                ('id',          models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('nom',         models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('niveau',      models.CharField(choices=[('A', 'Niveau A'), ('B', 'Niveau B'), ('C', 'Niveau C')], max_length=1)),
                ('duree',       models.IntegerField(default=20)),
                ('places',      models.IntegerField(default=30)),
                ('coefficient', models.IntegerField(default=2)),
                ('cree_le',     models.DateTimeField(auto_now_add=True)),
                ('formateur',   models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='formations_enseignees', to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='Lecon',
            fields=[
                ('id',         models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('titre',      models.CharField(max_length=200)),
                ('contenu',    models.TextField(blank=True)),
                ('ordre',      models.IntegerField(default=0)),
                ('ressources', models.TextField(blank=True)),
                ('formation',  models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lecons', to='api.formation')),
            ],
            options={'ordering': ['ordre']},
        ),
        migrations.CreateModel(
            name='Inscription',
            fields=[
                ('id',               models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('statut',           models.CharField(choices=[('en_attente', 'En attente'), ('confirme', 'Confirmé'), ('rejete', 'Rejeté')], default='en_attente', max_length=20)),
                ('motif_rejet',      models.TextField(blank=True)),
                ('telephone',        models.CharField(blank=True, max_length=30)),
                ('date_inscription', models.DateTimeField(auto_now_add=True)),
                ('formation',        models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inscriptions', to='api.formation')),
                ('utilisateur',      models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inscriptions', to='auth.user')),
            ],
            options={'unique_together': {('utilisateur', 'formation')}},
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id',         models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('date_debut', models.DateField()),
                ('date_fin',   models.DateField()),
                ('heure',      models.TimeField(blank=True, null=True)),
                ('notes',      models.TextField(blank=True)),
                ('formation',  models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='api.formation')),
                ('site',       models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.site')),
                ('formateur',  models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sessions_animees', to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id',          models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('valeur',      models.DecimalField(decimal_places=2, max_digits=5)),
                ('commentaire', models.TextField(blank=True)),
                ('date',        models.DateField(auto_now_add=True)),
                ('apprenant',   models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='auth.user')),
                ('formation',   models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='api.formation')),
            ],
        ),
        migrations.CreateModel(
            name='Certificat',
            fields=[
                ('id',              models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('numero',          models.CharField(max_length=50, unique=True)),
                ('date_delivrance', models.DateField(auto_now_add=True)),
                ('mention',         models.CharField(blank=True, max_length=50)),
                ('apprenant',       models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificats', to='auth.user')),
                ('formation',       models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificats', to='api.formation')),
            ],
        ),
        migrations.CreateModel(
            name='Profil',
            fields=[
                ('id',        models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('telephone', models.CharField(blank=True, max_length=30)),
                ('role',      models.CharField(choices=[('admin', 'Admin'), ('formateur', 'Formateur'), ('etudiant', 'Étudiant')], default='etudiant', max_length=20)),
                ('user',      models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profil', to='auth.user')),
            ],
        ),
    ]
