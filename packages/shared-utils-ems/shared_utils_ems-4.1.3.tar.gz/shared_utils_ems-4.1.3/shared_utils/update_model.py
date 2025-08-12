from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError


def model_update(instance, fields, data, auto_updated_at=True):
    """
    Safely update a Django model instance with validation.

    - Ensures only valid fields are updated.
    - Skips updating unchanged values.
    - Properly handles ManyToMany relationships.
    - Auto-updates 'updated_at' field if enabled.
    """

    has_updated = False
    m2m_data = {}
    update_fields = []

    model_fields = {field.name for field in instance._meta.get_fields()}

    for field in fields:
        if field not in data:
            continue

        model_field = instance._meta.get_field(field)

        if isinstance(model_field, models.ManyToManyField):
            m2m_data[field] = data[field]
            continue

        if getattr(instance, field) != data[field]:
            setattr(instance, field, data[field])
            update_fields.append(field)
            has_updated = True

    if not has_updated and not m2m_data:
        raise ValidationError(code="no_content")

    if has_updated:
        if auto_updated_at and "updated_at" in model_fields and "updated_at" not in update_fields:
            update_fields.append("updated_at")
            instance.updated_at = timezone.now()

    if update_fields:
        instance.full_clean()
        instance.save(update_fields=update_fields)

    for field_name, value in m2m_data.items():
        related_manager = getattr(instance, field_name)
        related_manager.set(value)
        has_updated = True

    return instance
