# conftest.py
import pytest
from django.conf import settings
# Импортируем класс клиента.
from django.test.client import Client
from datetime import datetime, timedelta
# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import News, Comment

from django.utils import timezone


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    """Создаем объект - автор."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Создаем объект - не автор."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    """Создаем клиент - автор."""
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    """Создаем клиент-не автор."""
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news():
    """Создаем объект новости."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
        # slug='note-slug',
        # author=author,
    )
    return news


@pytest.fixture
def comment(author, news):
    """Создаем комментарий."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def testhomepage(db):
    """Создаем количество новостей — более 10."""
    today = datetime.now()
    all_news = [
        News(title=f'Новость {index}',
             text='Просто текст.',
             date=today - timedelta(days=index)
             )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comments_quantity(author, news, db):
    """Создаем несколько комментариев."""
    now = timezone.now()
    comments = []
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author,
            text=f'Tекст {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def form_data():
    """Фикстура формы комментария."""
    return {
        # 'title': 'Новый заголовок',
        'text': 'Новый текст',
        # 'slug': 'new-slug'
    }
