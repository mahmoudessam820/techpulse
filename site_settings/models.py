from django.db import models

from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.admin.panels import FieldPanel 



@register_setting 
class FooterLinkes(BaseGenericSetting):
    """ For set footer links """
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)

    panels = [
        FieldPanel("linkedin"),
        FieldPanel("github"),
        FieldPanel("twitter")
    ]


@register_setting
class BrandSettings(BaseGenericSetting):
    """ For set brand images """
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel("logo")
    ]
