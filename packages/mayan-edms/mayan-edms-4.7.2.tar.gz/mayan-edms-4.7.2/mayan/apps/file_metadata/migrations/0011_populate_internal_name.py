from django.db import migrations

from mayan.apps.common.utils import convert_to_internal_name


def code_populate_internal_name(apps, schema_editor):
    DocumentFileDriverEntry = apps.get_model(
        app_label='file_metadata', model_name='DocumentFileDriverEntry'
    )
    FileMetadataEntry = apps.get_model(
        app_label='file_metadata', model_name='FileMetadataEntry'
    )

    for document_file_driver_entry in DocumentFileDriverEntry.objects.using(alias=schema_editor.connection.alias).all():
        for file_metadata_entry in document_file_driver_entry.entries.all():
            internal_name = convert_to_internal_name(
                value=file_metadata_entry.key
            )

            queryset_siblings = FileMetadataEntry.objects.using(
                alias=schema_editor.connection.alias
            ).filter(
                document_file_driver_entry=document_file_driver_entry
            ).exclude(pk=file_metadata_entry.pk)

            queryset_duplicated = queryset_siblings.filter(
                internal_name=internal_name
            )

            if queryset_duplicated.exists():
                internal_name = '{}_{}'.format(
                    internal_name, queryset_duplicated.count()
                )

            file_metadata_entry.internal_name = internal_name
            file_metadata_entry.save()


class Migration(migrations.Migration):
    dependencies = [
        ('file_metadata', '0010_add_internal_name')
    ]

    operations = [
        migrations.RunPython(
            code=code_populate_internal_name,
            reverse_code=migrations.RunPython.noop
        )
    ]
