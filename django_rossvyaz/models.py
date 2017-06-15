from django.db import models


class PhoneCode(models.Model):

    PHONE_TYPE_DEF = 'def'

    PHONE_TYPE_CHOICES = [
        (PHONE_TYPE_DEF, PHONE_TYPE_DEF),
    ]

    first_code = models.CharField(max_length=16)
    from_code = models.CharField(max_length=16)
    to_code = models.CharField(max_length=16)
    block_size = models.PositiveIntegerField()
    operator = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    phone_type = models.CharField(max_length=16, choices=PHONE_TYPE_CHOICES)
