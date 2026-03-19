# Generated custom migration

from django.db import migrations, models
import django.db.models.deletion


def create_default_position(apps, schema_editor):
    """Create a default 'General' position for existing candidates"""
    Position = apps.get_model('voting', 'Position')
    Position.objects.create(
        id=1,
        name='General Election',
        description='Default position for existing candidates',
        is_active=True
    )


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0004_alter_candidate_department_alter_candidate_votes_and_more'),
    ]

    operations = [
        # 1. Create Position model first
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        
        # 2. Create the default position
        migrations.RunPython(create_default_position, migrations.RunPython.noop),
        
        # 3. Add new fields to Candidate (nullable first)
        migrations.AddField(
            model_name='candidate',
            name='position',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='candidates', to='voting.position'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='manifesto',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='candidates/'),
        ),
        
        # 4. Set default position for existing candidates
        migrations.RunSQL(
            "UPDATE voting_candidate SET position_id = 1 WHERE position_id IS NULL",
            migrations.RunSQL.noop
        ),
        
        # 5. Make position field non-nullable
        migrations.AlterField(
            model_name='candidate',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidates', to='voting.position'),
        ),
        
        # 6. Update Candidate meta options
        migrations.AlterModelOptions(
            name='candidate',
            options={'ordering': ['position', 'name']},
        ),
        
        # 7. Add voted_positions to Voter
        migrations.AddField(
            model_name='voter',
            name='voted_positions',
            field=models.ManyToManyField(blank=True, related_name='voters_who_voted', to='voting.position'),
        ),
        
        # 8. Create Vote model
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voted_at', models.DateTimeField(auto_now_add=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voting.candidate')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voting.position')),
                ('voter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voting.voter')),
            ],
            options={
                'unique_together': {('voter', 'position')},
            },
        ),
    ]