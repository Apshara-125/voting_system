from django.db import migrations

def create_voters(apps, schema_editor):
    Voter = apps.get_model("voting", "Voter")
    voters = [
        ("2312125", "Apshara"),
        ("2312126", "Rahul"),
        ("2312127", "Sneha"),
        ("2312128", "Arjun"),
    ]
    for reg_no, name in voters:
        Voter.objects.get_or_create(reg_no=reg_no, defaults={"name": name, "has_voted": False})

class Migration(migrations.Migration):

    dependencies = [
        ("voting", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_voters),
    ]
