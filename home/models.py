from django.db import models
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from wagtail.models import Page
from wagtail.admin.panels import FieldPanel

from blog.models import BlogPage


class HomePage(Page):
    max_count = 1

    summary = models.TextField(blank=True, max_length=200)

    content_panels = Page.content_panels + [
        FieldPanel('summary'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        all_blog_posts = BlogPage.objects.live().public().order_by('-first_published_at')[:15]
        page = request.GET.get('page', 1)

        # Pagination
        paginator = Paginator(all_blog_posts, 10)  
        try:
            blog_posts = paginator.page(page)
        except PageNotAnInteger:
            blog_posts = paginator.page(1)
        except EmptyPage:
            blog_posts = paginator.page(paginator.num_pages)

        context["blog_posts"] = blog_posts

        for post in context["blog_posts"]:
            post.image = None
            for block in post.body:
                if block.block_type == 'image':
                    post.image = block.value

        return context