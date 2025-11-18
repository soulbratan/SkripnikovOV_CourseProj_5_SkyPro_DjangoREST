from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from habtracker.permissions import IsPublicReadOnly, IsOwnerOrReadOnly, IsOwner
from users.models import User
from habtracker.models import Habit, HabitCompletion
from habtracker.validators import validate_habit

# ТЕСТЫ ДЛЯ МОДЕЛИ HABIT---------------------------------------
class HabitModelTest(TestCase):
    """Тесты для модели Habit"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create(
            email='test@example.com',
            password='testpass123'
        )

        # Создаем приятную привычку для тестов связей
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Приятная привычка',
            is_pleasant=True,
            duration=60,
            frequency=1
        )

    def test_habit_creation_basic(self):
        """Тест создания базовой привычки"""
        habit = Habit.objects.create(
            user=self.user,
            place='Парк',
            time='09:00:00',
            action='Бег',
            duration=120,
            frequency=1
        )

        self.assertEqual(habit.action, 'Бег')
        self.assertEqual(habit.place, 'Парк')
        self.assertEqual(habit.duration, 120)
        self.assertEqual(habit.frequency, 1)
        self.assertFalse(habit.is_pleasant)
        self.assertFalse(habit.is_public)
        self.assertEqual(habit.user, self.user)

    def test_habit_creation_with_reward(self):
        """Тест создания привычки с вознаграждением"""
        habit = Habit.objects.create(
            user=self.user,
            place='Спортзал',
            time='10:00:00',
            action='Тренировка',
            duration=90,
            frequency=2,
            reward='Смузи'
        )

        self.assertEqual(habit.reward, 'Смузи')
        self.assertIsNone(habit.related_habit)

    def test_habit_creation_with_related_habit(self):
        """Тест создания привычки со связанной привычкой"""
        habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='19:00:00',
            action='Вечерняя пробежка',
            duration=120,
            frequency=1,
            related_habit=self.pleasant_habit
        )

        self.assertEqual(habit.related_habit, self.pleasant_habit)
        self.assertIsNone(habit.reward)

    def test_habit_creation_pleasant(self):
        """Тест создания приятной привычки"""
        pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='20:00:00',
            action='Чтение книги',
            is_pleasant=True,
            duration=30,
            frequency=1
        )

        self.assertTrue(pleasant_habit.is_pleasant)
        self.assertIsNone(pleasant_habit.reward)
        self.assertIsNone(pleasant_habit.related_habit)

    def test_habit_creation_public(self):
        """Тест создания публичной привычки"""
        public_habit = Habit.objects.create(
            user=self.user,
            place='Парк',
            time='07:00:00',
            action='Утренняя йога',
            duration=60,
            frequency=1,
            is_public=True
        )

        self.assertTrue(public_habit.is_public)

    def test_habit_string_representation(self):
        """Тест строкового представления привычки"""
        habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Медитация',
            duration=15,
            frequency=1
        )

        expected_str = f"{self.user.email}: Медитация"
        self.assertEqual(str(habit), expected_str)


    def test_habit_ordering(self):
        """Тест порядка сортировки привычек"""
        # Создаем несколько привычек
        habit1 = Habit.objects.create(
            user=self.user,
            place='Место1',
            time='08:00:00',
            action='Первая привычка',
            duration=60,
            frequency=1
        )

        habit2 = Habit.objects.create(
            user=self.user,
            place='Место2',
            time='09:00:00',
            action='Вторая привычка',
            duration=60,
            frequency=1
        )

        habits = Habit.objects.all()
        # Должны быть отсортированы по убыванию created_at
        self.assertEqual(habits[0], habit2)
        self.assertEqual(habits[1], habit1)


# ТЕСТЫ ДЛЯ МОДЕЛИ HabitCompletion---------------------------------------
class HabitCompletionModelTest(TestCase):
    """Тесты для модели HabitCompletion"""

    def setUp(self):
        self.user = User.objects.create(
            email='test@example.com',
            password='testpass123'
        )

        self.habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Тестовая привычка',
            duration=60,
            frequency=1
        )

    def test_habit_completion_creation(self):
        """Тест создания отметки о выполнении"""
        completion = HabitCompletion.objects.create(
            habit=self.habit,
            is_successful=True
        )

        self.assertEqual(completion.habit, self.habit)
        self.assertTrue(completion.is_successful)
        self.assertIsNotNone(completion.completed_at)

    def test_habit_completion_default_successful(self):
        """Тест что is_successful по умолчанию True"""
        completion = HabitCompletion.objects.create(habit=self.habit)

        self.assertTrue(completion.is_successful)

    def test_habit_completion_unsuccessful(self):
        """Тест создания неуспешного выполнения"""
        completion = HabitCompletion.objects.create(
            habit=self.habit,
            is_successful=False
        )

        self.assertFalse(completion.is_successful)

    def test_habit_completion_string_representation(self):
        """Тест строкового представления выполнения"""
        completion = HabitCompletion.objects.create(habit=self.habit)

        expected_str = f"{self.habit.action} - {completion.completed_at.strftime('%Y-%m-%d %H:%M')}"
        self.assertEqual(str(completion), expected_str)

    def test_habit_completion_ordering(self):
        """Тест порядка сортировки выполненных привычек"""
        completion1 = HabitCompletion.objects.create(habit=self.habit)
        completion2 = HabitCompletion.objects.create(habit=self.habit)

        completions = HabitCompletion.objects.all()
        # Должны быть отсортированы по убыванию completed_at
        self.assertEqual(completions[0], completion2)
        self.assertEqual(completions[1], completion1)


# ТЕСТЫ ДЛЯ ВАЛИДАТОРОВ HABTRACKER---------------------------------------
class HabitValidatorTest(TestCase):
    """Тесты для валидаторов привычек"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create(
            email='test@example.com',
            password='testpass123'
        )

        # Создаем приятную привычку для тестов связей
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Приятная привычка',
            is_pleasant=True,
            duration=60,
            frequency=1
        )

        # Создаем полезную привычку
        self.useful_habit = Habit.objects.create(
            user=self.user,
            place='Парк',
            time='09:00:00',
            action='Полезная привычка',
            duration=120,
            frequency=1
        )

    def test_valid_habit_with_reward(self):
        """Тест валидной привычки с вознаграждением"""
        habit = Habit(
            user=self.user,
            place='Дом',
            time='10:00:00',
            action='Тест с наградой',
            duration=60,
            frequency=1,
            reward='Награда'
        )

        # Не должно вызывать ошибок
        try:
            validate_habit(habit)
        except ValidationError:
            self.fail("validate_habit вызвал ValidationError для валидной привычки")

    def test_valid_habit_with_related_habit(self):
        """Тест валидной привычки со связанной привычкой"""
        habit = Habit(
            user=self.user,
            place='Дом',
            time='10:00:00',
            action='Тест со связанной привычкой',
            duration=60,
            frequency=1,
            related_habit=self.pleasant_habit  # Приятная привычка
        )

        # Не должно вызывать ошибок
        try:
            validate_habit(habit)
        except ValidationError:
            self.fail("validate_habit вызвал ValidationError для валидной привычки")

    def test_invalid_related_habit_and_reward(self):
        """Тест: нельзя одновременно указывать связанную привычку и вознаграждение"""
        habit = Habit(
            user=self.user,
            place='Дом',
            time='10:00:00',
            action='Тест',
            duration=60,
            frequency=1,
            related_habit=self.pleasant_habit,
            reward='Награда'
        )

        with self.assertRaises(ValidationError) as context:
            validate_habit(habit)

        self.assertIn('__all__', context.exception.message_dict)
        error_message = context.exception.message_dict['__all__'][0]
        self.assertIn('связанную привычку и вознаграждение', error_message)

    def test_invalid_duration_too_long(self):
        """Тест: время выполнения не больше 120 секунд"""
        habit = Habit(
            user=self.user,
            place='Дом',
            time='10:00:00',
            action='Тест',
            duration=150,  # Слишком долго
            frequency=1
        )

        with self.assertRaises(ValidationError) as context:
            validate_habit(habit)

        self.assertIn('duration', context.exception.message_dict)
        error_message = context.exception.message_dict['duration'][0]
        self.assertIn('120 секунд', error_message)

    def test_invalid_related_habit_not_pleasant(self):
        """Тест: в связанные привычки могут попадать только приятные привычки"""
        habit = Habit(
            user=self.user,
            place='Дом',
            time='10:00:00',
            action='Тест',
            duration=60,
            frequency=1,
            related_habit=self.useful_habit  # Не приятная привычка!
        )

        with self.assertRaises(ValidationError) as context:
            validate_habit(habit)

        self.assertIn('related_habit', context.exception.message_dict)
        error_message = context.exception.message_dict['related_habit'][0]
        self.assertIn('только приятные привычки', error_message)

    def test_pleasant_habit_with_reward(self):
        """Тест: у приятной привычки не может быть вознаграждения"""
        habit = Habit(
            user=self.user,
            place='Дом',
            time='10:00:00',
            action='Тест',
            is_pleasant=True,
            duration=60,
            frequency=1,
            reward='Награда'  # Не должно быть у приятной привычки
        )

        with self.assertRaises(ValidationError) as context:
            validate_habit(habit)

        self.assertIn('reward', context.exception.message_dict)
        error_message = context.exception.message_dict['reward'][0]
        self.assertIn('не может быть вознаграждения', error_message)

    def test_pleasant_habit_with_related_habit(self):
        """Тест: у приятной привычки не может быть связанной привычки"""
        other_pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='11:00:00',
            action='Другая приятная привычка',
            is_pleasant=True,
            duration=60,
            frequency=1
        )

        habit = Habit(
            user=self.user,
            place='Дом',
            time='10:00:00',
            action='Тест',
            is_pleasant=True,
            duration=60,
            frequency=1,
            related_habit=other_pleasant_habit  # Не должно быть у приятной привычки
        )

        with self.assertRaises(ValidationError) as context:
            validate_habit(habit)

        self.assertIn('related_habit', context.exception.message_dict)
        error_message = context.exception.message_dict['related_habit'][0]
        self.assertIn('не может быть связанной привычки', error_message)

    def test_invalid_frequency_too_high(self):
        """Тест: периодичность не больше 7 дней"""
        habit = Habit(
            user=self.user,
            place='Дом',
            time='10:00:00',
            action='Тест',
            duration=60,
            frequency=10  # Слишком редко
        )

        with self.assertRaises(ValidationError) as context:
            validate_habit(habit)

        self.assertIn('frequency', context.exception.message_dict)
        error_message = context.exception.message_dict['frequency'][0]
        self.assertIn('1 раз в 7 дней', error_message)

    def test_cyclic_dependency(self):
        """Тест: циклические зависимости запрещены"""
        # Сначала создаем привычку, которая ссылается на pleasant_habit
        habit1 = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='10:00:00',
            action='Привычка 1',
            duration=60,
            frequency=1,
            related_habit=self.pleasant_habit
        )

        # Пытаемся создать привычку, которая ссылается на habit1, создавая цикл
        habit2 = Habit(
            user=self.user,
            place='Дом',
            time='11:00:00',
            action='Привычка 2',
            duration=60,
            frequency=1,
            related_habit=habit1
        )

        # Меняем related_habit у pleasant_habit на habit2, создавая цикл
        self.pleasant_habit.related_habit = habit2

        with self.assertRaises(ValidationError) as context:
            validate_habit(habit2)

        self.assertIn('related_habit', context.exception.message_dict)

    def test_foreign_user_related_habit(self):
        """Тест: нельзя использовать чужую привычку как связанную"""
        other_user = User.objects.create(
            email='other@example.com',
            password='otherpass123'
        )

        other_pleasant_habit = Habit.objects.create(
            user=other_user,  # Другой пользователь!
            place='Дом',
            time='08:00:00',
            action='Чужая приятная привычка',
            is_pleasant=True,
            duration=60,
            frequency=1
        )

        habit = Habit(
            user=self.user,
            place='Дом',
            time='10:00:00',
            action='Тест',
            duration=60,
            frequency=1,
            related_habit=other_pleasant_habit  # Чужая привычка!
        )

        with self.assertRaises(ValidationError) as context:
            validate_habit(habit)

        self.assertIn('related_habit', context.exception.message_dict)
        error_message = context.exception.message_dict['related_habit'][0]
        self.assertIn('чужую привычку', error_message)


#ТЕСТЫ ДЛЯ permissions habtracker------------------------------

class PermissionsTest(TestCase):
    """Тесты для кастомных разрешений habtracker"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.factory = APIRequestFactory()

        self.user = User.objects.create(
            email='owner@example.com',
            password='testpass123'
        )

        self.other_user = User.objects.create(
            email='other@example.com',
            password='otherpass123'
        )

        # Создаем привычки для тестов
        self.private_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Приватная привычка',
            duration=60,
            frequency=1,
            is_public=False
        )

        self.public_habit = Habit.objects.create(
            user=self.user,
            place='Парк',
            time='09:00:00',
            action='Публичная привычка',
            duration=120,
            frequency=1,
            is_public=True
        )

        self.other_user_habit = Habit.objects.create(
            user=self.other_user,
            place='Офис',
            time='10:00:00',
            action='Привычка другого пользователя',
            duration=90,
            frequency=2
        )

    def test_is_owner_permission_owner(self):
        """Тест IsOwner разрешения для владельца объекта"""
        permission = IsOwner()
        request = self.factory.get('/')
        request.user = self.user

        # Владелец имеет доступ к своей привычке
        self.assertTrue(permission.has_object_permission(request, None, self.private_habit))

    def test_is_owner_permission_non_owner(self):
        """Тест IsOwner разрешения для не-владельца"""
        permission = IsOwner()
        request = self.factory.get('/')
        request.user = self.other_user

        # Чужой пользователь не имеет доступ к привычке
        self.assertFalse(permission.has_object_permission(request, None, self.private_habit))

    def test_is_owner_or_read_only_safe_methods_owner(self):
        """Тест IsOwnerOrReadOnly для безопасных методов (владелец)"""
        permission = IsOwnerOrReadOnly()

        # Тестируем безопасные методы для владельца
        safe_methods = ['GET', 'HEAD', 'OPTIONS']
        for method in safe_methods:
            request = self.factory.get('/')
            request.method = method
            request.user = self.user

            # Владелец имеет доступ для безопасных методов
            self.assertTrue(permission.has_object_permission(request, None, self.private_habit))

    def test_is_owner_or_read_only_safe_methods_non_owner(self):
        """Тест IsOwnerOrReadOnly для безопасных методов (не-владелец)"""
        permission = IsOwnerOrReadOnly()

        # Тестируем безопасные методы для не-владельца
        safe_methods = ['GET', 'HEAD', 'OPTIONS']
        for method in safe_methods:
            request = self.factory.get('/')
            request.method = method
            request.user = self.other_user

            # Не-владелец имеет доступ только для чтения
            self.assertTrue(permission.has_object_permission(request, None, self.private_habit))

    def test_is_owner_or_read_only_unsafe_methods_owner(self):
        """Тест IsOwnerOrReadOnly для небезопасных методов (владелец)"""
        permission = IsOwnerOrReadOnly()

        # Тестируем небезопасные методы для владельца
        unsafe_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
        for method in unsafe_methods:
            request = self.factory.get('/')
            request.method = method
            request.user = self.user

            # Владелец имеет доступ для небезопасных методов
            self.assertTrue(permission.has_object_permission(request, None, self.private_habit))

    def test_is_owner_or_read_only_unsafe_methods_non_owner(self):
        """Тест IsOwnerOrReadOnly для небезопасных методов (не-владелец)"""
        permission = IsOwnerOrReadOnly()

        # Тестируем небезопасные методы для не-владельца
        unsafe_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
        for method in unsafe_methods:
            request = self.factory.get('/')
            request.method = method
            request.user = self.other_user

            # Не-владелец не имеет доступ для небезопасных методов
            self.assertFalse(permission.has_object_permission(request, None, self.private_habit))

    def test_is_public_read_only_public_habit_safe_methods(self):
        """Тест IsPublicReadOnly для публичных привычек и безопасных методов"""
        permission = IsPublicReadOnly()

        # Тестируем безопасные методы
        safe_methods = ['GET', 'HEAD', 'OPTIONS']
        for method in safe_methods:
            request = self.factory.get('/')
            request.method = method

            # Имеем доступ к публичной привычке для чтения
            self.assertTrue(permission.has_object_permission(request, None, self.public_habit))

    def test_is_public_read_only_private_habit_safe_methods(self):
        """Тест IsPublicReadOnly для приватных привычек и безопасных методов"""
        permission = IsPublicReadOnly()

        # Тестируем безопасные методы для приватной привычки
        safe_methods = ['GET', 'HEAD', 'OPTIONS']
        for method in safe_methods:
            request = self.factory.get('/')
            request.method = method

            # Не имеем доступ к приватной привычке
            self.assertFalse(permission.has_object_permission(request, None, self.private_habit))

    def test_is_public_read_only_unsafe_methods(self):
        """Тест IsPublicReadOnly для небезопасных методов"""
        permission = IsPublicReadOnly()

        # Тестируем небезопасные методы
        unsafe_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
        for method in unsafe_methods:
            request = self.factory.get('/')
            request.method = method

            # Не имеем доступ для небезопасных методов даже к публичной привычке
            self.assertFalse(permission.has_object_permission(request, None, self.public_habit))

    def test_is_public_read_only_has_permission_method(self):
        """Тест метода has_permission для IsPublicReadOnly"""
        permission = IsPublicReadOnly()

        # Проверяем безопасные методы
        safe_request = self.factory.get('/')
        safe_request.method = 'GET'
        self.assertTrue(permission.has_permission(safe_request, None))

        # Проверяем небезопасные методы
        unsafe_request = self.factory.post('/')
        unsafe_request.method = 'POST'
        self.assertFalse(permission.has_permission(unsafe_request, None))