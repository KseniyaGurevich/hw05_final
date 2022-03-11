from django.db import models


class PubDateModel(models.Model):
    pub_date = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True


class CreateModel(models.Model):
    created = models.DateTimeField(
        verbose_name='Дата создания комментария',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True
