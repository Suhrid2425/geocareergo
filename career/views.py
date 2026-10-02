from django.shortcuts import render, get_object_or_404

from .models import Article


def career_home(request):
    articles = Article.objects.filter(is_published=True)

    return render(
        request,
        "career/career_home.html",
        {"articles": articles},
    )


def article_detail(request, slug):
    article = get_object_or_404(
        Article,
        slug=slug,
        is_published=True,
    )

    related_articles = (
        Article.objects
        .filter(
            is_published=True,
            category=article.category,
        )
        .exclude(id=article.id)[:3]
    )

    return render(
        request,
        "career/article_detail.html",
        {
            "article": article,
            "related_articles": related_articles,
        },
    )