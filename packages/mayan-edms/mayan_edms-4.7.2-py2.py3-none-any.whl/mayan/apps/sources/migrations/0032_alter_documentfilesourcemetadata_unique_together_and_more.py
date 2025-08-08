from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0090_alter_documentversion_active'),
        ('sources', '0031_alter_documentfilesourcemetadata_value')
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='documentfilesourcemetadata', unique_together={
                ('document_file', 'key')
            }
        ),
        migrations.RemoveField(
            model_name='documentfilesourcemetadata', name='source'
        )
    ]
