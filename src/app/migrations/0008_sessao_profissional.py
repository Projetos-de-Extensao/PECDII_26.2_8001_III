import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0007_merge_20261102_2241"),
    ]

    operations = [
        migrations.AddField(
            model_name="sessao",
            name="profissional",
            field=models.ForeignKey(
                to="app.profissional",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="sessoes",
                null=True,
                blank=True,
            ),
        ),
    ]
