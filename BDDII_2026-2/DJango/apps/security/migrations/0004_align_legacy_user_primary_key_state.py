from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("security", "0003_user_auth_user"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="user",
                    name="id",
                    field=models.AutoField(
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
        ),
    ]
