import pytest

from django.urls import reverse


from news.models import Comment

from news.forms import BAD_WORDS, WARNING
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
    # предварительно подготовленные данные формы с текстом комментария.
    detail_url = reverse('news:detail', args=(news.id,))
    client.post(detail_url, data=form_data)
    # Считаем количество комментариев.
    comments_count = Comment.objects.count()
    # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author, news, form_data):
    """Авторизованный пользователь может отправить комментарий."""
    detail_url = reverse('news:detail', args=(news.id,))
    # Совершаем запрос через авторизованный клиент.
    response = author_client.post(detail_url, data=form_data)
    # Проверяем, что редирект привёл к разделу с комментами.
    assertRedirects(response, f'{detail_url}#comments')
    # Считаем количество комментариев.
    comments_count = Comment.objects.count()
    # Убеждаемся, что есть один комментарий.
    assert comments_count == 1
    # Получаем объект комментария из базы.
    comment = Comment.objects.get()
    # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    """Проверка стоп слов.

    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    detail_url = reverse('news:detail', args=(news.id,))
    response = author_client.post(detail_url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, form_data, news, comment):
    """Проверка.

    Авторизованный пользователь может редактировать
    свои комментарии.
    """
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'  # Адрес блока с комментариями.
    # Получаем адрес страницы редактирования заметки:
    edit_url = reverse('news:edit', args=(comment.id,))
    # URL для удаления комментария.
    # delete_url = reverse('news:delete', args=(comment.id,))

    # Выполняем запрос на редактирование от имени автора комментария.
    response = author_client.post(edit_url, data=form_data)
    # Проверяем, что сработал редирект.
    assertRedirects(response, url_to_comments)
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст комментария соответствует обновленному.
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_not_author_cant_edit(not_author_client, form_data, comment):
    """Проверка.

    Авторизованный пользователь не может редактировать
    чужие комментарии.
    """
    # news_url = reverse('news:detail', args=(news.id,))
    # url_to_comments = news_url + '#comments'  # Адрес блока с комментариями.
    # Получаем адрес страницы редактирования заметки:
    edit_url = reverse('news:edit', args=(comment.id,))
    # Выполняем запрос на редактирование от имени другого пользователя.
    response = not_author_client.post(edit_url, data=form_data)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст остался тем же, что и был.
    assert comment.text == comment.text


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, form_data, news, comment):
    """Проверка.

    Авторизованный пользователь может удалить
    свои комментарии.
    """
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'  # Адрес блока с комментариями.
    # URL для удаления комментария.
    delete_url = reverse('news:delete', args=(comment.id,))
    # От имени автора комментария отправляем DELETE-запрос на удаление.
    response = author_client.delete(delete_url)
    # Проверяем, что редирект привёл к разделу с комментариями.
    # Заодно проверим статус-коды ответов.
    assertRedirects(response, url_to_comments)
    # Считаем количество комментариев в системе.
    comments_count = Comment.objects.count()
    # Ожидаем ноль комментариев в системе.
    assert comments_count == 0


@pytest.mark.django_db
def test_not_author_cant_delete(not_author_client, form_data, news, comment):
    """Проверка.

    Авторизованный пользователь не может удалить
    чужие комментарии.
    """
    # URL для удаления комментария.
    delete_url = reverse('news:delete', args=(comment.id,))
    # Выполняем запрос на удаление от пользователя-читателя.
    response = not_author_client.delete(delete_url)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Убедимся, что комментарий по-прежнему на месте.
    comments_count = Comment.objects.count()
    assert comments_count == 1
