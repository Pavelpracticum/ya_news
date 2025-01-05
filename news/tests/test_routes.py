# тесты библиотека pytest
# test_routes.py
import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


# cls.news = News.objects.create(title='Заголовок', text='Текст')
@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_availability_for_anonymous_user(client, name):
    """Проверка.

    Анонимному пользователю доступна главная страница проекта,
    логина, логаута, регистрации.
    """
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


def test_pages_availability_for_auth_user(not_author_client, news):
    """Анонимному пользователю доступна отдельная страница новости."""
    url = reverse('news:detail', args=(news.id,))
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    # parametrized_client - название параметра,
    # в который будут передаваться фикстуры;
    # Параметр expected_status - ожидаемый статус ответа.
    'param_client, status',
    # В кортеже с кортежами передаём значения для параметров:
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_dif_users_comm_edit_and_delete(param_client, name, comment, status):
    """Проверка.

    Страницы удаления и редактирования комментария
    доступны автору комментария.
    """
    url = reverse(name, args=(comment.id,))
    # Делаем запрос от имени клиента parametrized_client:
    response = param_client.get(url)
    # Ожидаем ответ страницы, указанный в expected_status:
    assert response.status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    # Вторым параметром передаём comment_object
    'name, comment_object',
    (
        ('news:edit', pytest.lazy_fixture('comment')),
        ('news:delete', pytest.lazy_fixture('comment')),
    ),
)
def test_redirects(client, name, comment_object):
    """Проверка.

    При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    # Формируем URL в зависимости от того, передан ли объект заметки:
    url = reverse(name, args=(comment_object.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    # Ожидаем, что со всех проверяемых страниц анонимный клиент
    # будет перенаправлен на страницу логина:
    assertRedirects(response, expected_url)
