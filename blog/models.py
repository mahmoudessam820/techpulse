from django.contrib.auth.models import User
from django.db import models
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from wagtail import blocks
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page, Orderable 
from modelcluster.fields import ParentalKey
from wagtail.snippets.models import register_snippet



class BlogIndexPage(Page):
    max_count = 1 
    parent_page_types = ['home.HomePage']

    summary = models.TextField(blank=True, max_length=500)
    subscribe_url = models.URLField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('summary'),
        FieldPanel('subscribe_url')
    ]

    def get_context(self, request):
        context = super().get_context(request)
        posts = BlogPage.objects.live().public().order_by('-first_published_at')
        page = request.GET.get('page', 1)

        # Pagination
        paginator = Paginator(posts, 10)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context['posts'] = posts

        for post in context["posts"]:
            post.image = None
            for block in post.body:
                if block.block_type == 'image':
                    post.image = block.value

        return context


class BlogPage(Page):
    parent_page_types = ['blog.BlogIndexPage']

    intro = models.CharField(max_length=500, blank=True, null=True)
    body = StreamField([
        ("content", blocks.RichTextBlock(
            features=[
                "h3",
                "h4",
                "h5",
                "h6",
                "ol",
                "ul",
                "hr",
                "bold",
                "italic",
                "link",
                "code",
            ],
            template="blocks/richtext.html"
        )),
        ("image", ImageChooserBlock(
            template="blocks/image.html"
        )),
        ("quote", blocks.BlockQuoteBlock(
            template="blocks/quote.html"
        )),
        ("twitter_block", blocks.StructBlock([
            ("text", blocks.CharBlock()),
            ("author", blocks.CharBlock()),
        ], template="blocks/twitter_block.html")),
    ])
    author = models.ForeignKey(User, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blog_posts"
    )

    def get_context(self, request):
        context = super().get_context(request)
        context["posts"] = BlogPage.objects.live().public().order_by('-first_published_at')[:10]
        return context

    class Meta(Page.Meta):
        ordering = ['-first_published_at']  
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'


    content_panels = Page.content_panels + [
        InlinePanel('categories', label="Categories"),
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('author')
    ]


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(unique=True, max_length=80)
    color = models.CharField(choices=[
        ('blue', 'Blue'),
        ('green', 'Green'), 
        ('yellow', 'Yellow'),
        ('indigo', 'Indigo'), 
        ('purple', 'Purple'),
        ('pink', 'Pink')
    ], max_length=10, default='green', help_text='Color of the category')

    class Meta:
        verbose_name_plural = 'Blog Categories'

    def __str__(self):
        return f"{self.name} ({self.color})"


class BlogPageCategories(Orderable):
    page = ParentalKey(BlogPage, related_name='categories')
    category = models.ForeignKey(BlogCategory, related_name='+', on_delete=models.CASCADE)

    panels = [
        FieldPanel('category'),
    ]