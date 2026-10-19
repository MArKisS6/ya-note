from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тестируем маршруты проекта."""

    @classmethod
    def setUpTestData(cls):
        # Создаём автора и читателя:
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        # Создаём заметку от имени автора:
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='test-note',
            author=cls.author,
        )

    def test_pages_availability_for_anonymous(self):
        """Страницы, доступные анонимному пользователю."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Страница {name} должна быть доступна анониму'
                )

    def test_logout_available_for_all(self):
        """Страница выхода доступна всем пользователям."""
        url = reverse('users:logout')
        response = self.client.post(url)
        self.assertIn(
            response.status_code,
            (HTTPStatus.OK, HTTPStatus.FOUND),
            'Страница выхода должна быть доступна'
        )

    def test_pages_availability_for_author(self):
        """Страницы, доступные авторизованному пользователю."""
        self.client.force_login(self.author)
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Страница {name} должна быть доступна автору'
                )

    def test_note_detail_availability(self):
        """Детальная заметка доступна только автору."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        url = reverse('notes:detail', args=(self.note.slug,))
        for user, status in users_statuses:
            self.client.force_login(user)
            with self.subTest(user=user):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    status,
                    f'{user} на странице notes:detail'
                )

    def test_edit_delete_availability_for_author(self):
        """Edit/delete доступны автору, чужой → 404."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(
                        response.status_code,
                        status,
                        f'{user} на странице {name}'
                    )

    def test_redirect_for_anonymous_client(self):
        """Аноним при попытке зайти на страницы заметок → на логин."""
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    redirect_url,
                    msg_prefix=f'Аноним на {name}'
                )
