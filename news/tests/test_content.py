# тесты библиотека pytest
# test_content.py
import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_home_page_news_no_more_ten(client, testhomepage):
    """Проверка.

    Rоличество новостей на главной странице — не более 10.
    """
    # News.objects.bulk_create(
    #         News(title=f'Новость {index}', text='Просто текст.')
    #         for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    #     )
    # Загружаем главную страницу.
    response = client.get(reverse('news:home'))
    # Получаем список объектов из словаря контекста.
    object_list = response.context['object_list']
    # Определяем количество записей в списке.
    news_count = object_list.count()
    # Проверяем, что на странице именно 10 новостей.
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    """Проверка сортировки новостей.

    Новости отсортированы от самой свежей к самой старой.
    """
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(author_client, news, comments_quantity):
    """Проверка сортировки комментариев.

    Комментарии на странице отдельной новости отсортированы:
    старые в начале списка, новые — в конце.
    """
    detail_url = reverse('news:detail', args=(news.id,))
    response = author_client.get(detail_url)
    # Проверяем, что объект новости находится в словаре контекста
    # под ожидаемым именем - названием модели
    assert 'news' in response.context
    # Получаем объект новости.
    news = response.context['news']
    # Получаем все комментарии к новости.
    all_comments = news.comment_set.all()
    # Собираем временные метки всех комментариев.
    all_timestamps = [comment.created for comment in all_comments]
    # Сортируем временные метки, менять порядок сортировки не надо.
    sorted_timestamps = sorted(all_timestamps)
    # Проверяем, что временные метки отсортированы правильно.
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
@pytest.mark.django_db
@pytest.mark.parametrize("some_client, has_form", [
    (pytest.lazy_fixture('client'), False),
    (pytest.lazy_fixture('author_client'), True),
])
def test_client_has_access_to_form(some_client, news, has_form):
    """Проверка доступности формы для добавления комментариев."""
    detail_url = reverse('news:detail', args=(news.id,))
    response = some_client.get(detail_url)
    if has_form:
        # Пытаемся получить объект формы из контекста
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
    else:
        assert 'form' not in response.context
# def test_anonymous_client_has_no_form(client, news):
#     """Проверка доступности формы.

#     Анонимному пользователю недоступна форма для отправки комментария
#     на странице отдельной новости, а авторизованному доступна.
#     """
#     detail_url = reverse('news:detail', args=(news.id,))
#     response = client.get(detail_url)
#     assert 'form' not in response.context


# @pytest.mark.django_db
# def test_authorized_client_has_form(author_client, news):
#     # Авторизуем клиент при помощи ранее созданного пользователя.
#     detail_url = reverse('news:detail', args=(news.id,))
#     response = author_client.get(detail_url)
#     assert 'form' in response.context
#     # Проверим, что объект формы соответствует нужному классу формы.
#     assert isinstance(response.context['form'], CommentForm)
