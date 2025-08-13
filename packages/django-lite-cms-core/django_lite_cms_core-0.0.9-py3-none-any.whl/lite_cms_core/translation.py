from modeltranslation.translator import register, TranslationOptions
from lite_cms_core.models import BaseEntity, ContentFieldMixin


@register(BaseEntity)
class TranslatedBaseEntity(TranslationOptions):
    fields = ('title', )


@register(ContentFieldMixin)
class TranslatedContentFieldMixin(TranslationOptions):
    fields = ('content', )
