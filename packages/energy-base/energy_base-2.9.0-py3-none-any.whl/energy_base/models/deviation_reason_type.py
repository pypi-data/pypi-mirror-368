from django.db import models


class DeviationReasonType(models.TextChoices):
    PLANNED = 'planned', 'Плановое отключение'
    NO_CONNECTION = 'no_connection', 'Нет связи'
    OTHER = 'other', 'Другое'
