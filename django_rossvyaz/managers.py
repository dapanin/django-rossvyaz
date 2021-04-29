from django.db import models


class PhoneCodeManager(models.Manager):

    def by_phone(self, phone):
        first_code = phone[:3]
        last_code = phone[3:]
        return super().get_queryset().filter(
            first_code=first_code,
            to_code__gte=last_code,
            from_code__lte=last_code,
        ).order_by('block_size')
