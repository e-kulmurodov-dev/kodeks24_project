from django.db.models import Model, DateTimeField, CharField, SlugField
from django.utils.text import slugify


class TimeBaseModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SlugBaseModel(Model):
    name = CharField(max_length=255)
    slug = SlugField(max_length=255, unique=True, editable=False)

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.name)
        while self.__class__.objects.filter(slug=self.slug).exists():
            self.slug += '1'
        super().save(force_insert, force_update, using, update_fields)



# class BaseModel(TimeBaseModel, SlugBaseModel):
#     title = CharField(max_length=255)
#
#     def get_slug_source(self):
#         return self.title
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         abstract = True
