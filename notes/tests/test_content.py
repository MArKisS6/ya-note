from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestHomePage(TestCase):
    """Тестируем главную страницу."""

    HOME_URL = reverse('notes:home')

    def test_home_page_has_no_notes_list(self):
        """На главной нет списка заметок."""
        response = self.client.get(self.HOME_URL)
        # TemplateView не передаёт object_list в контекст:
        self.assertNotIn(
            'object_list',
            response.context,
            'На главной не должно быть списка заметок'
        )


class TestNotesList(TestCase):
    """Тестируем страницу списка заметок."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        # Заметки автора:
        cls.note_1 = Note.objects.create(
            title='Заметка первая',
            text='Текст первой заметки',
            slug='note-1',
            author=cls.author,
        )
        cls.note_2 = Note.objects.create(
            title='Заметка вторая',
            text='Текст второй заметки',
            slug='note-2',
            author=cls.author,
        )
        # Заметка читателя:
        cls.note_reader = Note.objects.create(
            title='Заметка читателя',
            text='Текст заметки читателя',
            slug='note-reader',
            author=cls.reader,
        )

    def test_notes_list_contains_all_author_notes(self):
        """В списке — все заметки автора."""
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(
            self.note_1,
            object_list,
            'Своя заметка должна быть в списке'
        )
        self.assertIn(
            self.note_2,
            object_list,
            'Своя заметка должна быть в списке'
        )

    def test_notes_list_does_not_contain_other_users_notes(self):
        """В списке нет чужих заметок."""
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(
            self.note_reader,
            object_list,
            'Чужая заметка не должна быть в списке'
        )


class TestNoteDetail(TestCase):
    """Тестируем страницу отдельной заметки."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Заголовок заметки',
            text='Текст заметки',
            slug='test-note',
            author=cls.author,
        )

    def test_note_detail_shows_note_object(self):
        """В контексте — запрошенная заметка."""
        self.client.force_login(self.author)
        url = reverse('notes:detail', args=(self.note.slug,))
        response = self.client.get(url)
        # Проверяем, что объект заметки находится в контексте
        # под ожидаемым именем — названием модели:
        self.assertIn('note', response.context)
        # Проверяем, что это именно запрошенная заметка:
        self.assertEqual(
            response.context['note'],
            self.note,
            'В контексте должна быть запрошенная заметка'
        )
