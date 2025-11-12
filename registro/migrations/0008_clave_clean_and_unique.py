from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("registro", "0007"),  # la nueva 0007 que acabas de generar
    ]

    operations = [
        migrations.RunSQL(
            sql="UPDATE registro_participant SET clave = NULL WHERE clave = ''",
            reverse_sql="",
        ),
        migrations.AlterField(
            model_name="participant",
            name="clave",
            field=models.CharField(
                max_length=40,
                unique=True,
                null=True,
                blank=True,
                editable=False,
            ),
        ),
    ]
