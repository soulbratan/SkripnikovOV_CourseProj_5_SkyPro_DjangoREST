from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from users.serializers import UserSerializer, PublicUserSerializer
from rest_framework.exceptions import ErrorDetail

User = get_user_model()

# ТЕСТИРОВАНИЕ МОДЕЛИ USER---------------------------------------------------
class UserModelTest(TestCase):
    """Тесты для модели User"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': 'John',
            'last_name': 'Doe',
        }

    def test_create_user(self):
        """Тест создания обычного пользователя"""
        user = User.objects.create(**self.user_data)

        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        superuser = User.objects.create(
            email='admin@example.com',
            password='adminpassword123',
            is_staff=True,
            is_superuser=True
        )

        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_email_unique_constraint(self):
        """Тест уникальности email"""
        User.objects.create(**self.user_data)
        self.assertRaises(IntegrityError)

    def test_username_is_none(self):
        """Тест что поле username равно None"""
        user = User.objects.create(**self.user_data)
        self.assertIsNone(user.username)

    def test_optional_fields(self):
        """Тест опциональных полей"""
        user_data_with_optional = {
            **self.user_data,
            'phone': '+79991234567',
            'tg_id': '123456789',
            'token': 'test_token_123',
        }
        user = User.objects.create(**user_data_with_optional)

        self.assertEqual(user.phone, '+79991234567')
        self.assertEqual(user.tg_id, '123456789')
        self.assertEqual(user.token, 'test_token_123')

    def test_blank_optional_fields(self):
        """Тест что опциональные поля могут быть пустыми"""
        user = User.objects.create(**self.user_data)

        self.assertIsNone(user.phone)
        self.assertIsNone(user.tg_id)
        self.assertIsNone(user.token)

    def test_user_string_representation(self):
        """Тест строкового представления пользователя"""
        user = User.objects.create(**self.user_data)
        self.assertEqual(str(user), self.user_data['email'])

    def test_verbose_names(self):
        """Тест verbose names модели"""
        user = User.objects.create(**self.user_data)

        self.assertEqual(user._meta.verbose_name, "Пользователь")
        self.assertEqual(user._meta.verbose_name_plural, "Пользователи")

    def test_email_required(self):
        """Тест что email обязателен для заполнения"""
        User.objects.create(email='', password='testpassword123')
        self.assertRaises(ValueError)


    def test_password_required(self):
        """Тест что пароль обязателен для заполнения"""
        User.objects.create(email='test2@example.com', password='')
        self.assertRaises(ValueError)


    def test_user_ordering(self):
        """Тест порядка сортировки пользователей"""
        user1 = User.objects.create(
            email='user1@example.com',
            password='password123'
        )
        user2 = User.objects.create(
            email='user2@example.com',
            password='password123'
        )

        users = User.objects.all()
        self.assertEqual(users[0], user1)
        self.assertEqual(users[1], user2)

    def test_phone_max_length(self):
        """Тест максимальной длины поля phone"""
        user = User.objects.create(
            email='phone_test@example.com',
            password='password123',
            phone='1' * 35  # Максимальная длина
        )
        self.assertEqual(len(user.phone), 35)

    def test_tg_id_max_length(self):
        """Тест максимальной длины поля tg_id"""
        user = User.objects.create(
            email='tg_test@example.com',
            password='password123',
            tg_id='1' * 50  # Максимальная длина
        )
        self.assertEqual(len(user.tg_id), 50)

    def test_token_max_length(self):
        """Тест максимальной длины поля token"""
        user = User.objects.create(
            email='token_test@example.com',
            password='password123',
            token='1' * 100  # Максимальная длина
        )
        self.assertEqual(len(user.token), 100)

    def test_user_permissions(self):
        """Тест базовых разрешений пользователя"""
        user = User.objects.create(**self.user_data)

        # Обычный пользователь не должен иметь особых разрешений
        self.assertFalse(user.has_perm('auth.add_user'))
        self.assertFalse(user.has_perm('auth.change_user'))
        self.assertFalse(user.has_perm('auth.delete_user'))

    def test_superuser_permissions(self):
        """Тест разрешений суперпользователя"""
        superuser = User.objects.create(
            email='super@example.com',
            password='superpassword123',
            is_staff=True,
            is_superuser=True
        )

        # Суперпользователь должен иметь все разрешения
        self.assertTrue(superuser.has_perm('auth.add_user'))
        self.assertTrue(superuser.has_perm('auth.change_user'))
        self.assertTrue(superuser.has_perm('auth.delete_user'))
        self.assertTrue(superuser.has_perm('some_nonexistent_permission'))


# ТЕСТИРОВАНИЕ СЕРИАЛИЗАТОРОВ USER---------------------------------------------------
class UserSerializerTest(TestCase):
    """Тесты для сериализаторов пользователя"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+79991234567',
            'tg_id': '123456789'
        }
        self.user = User.objects.create(**self.user_data)

    def test_user_serializer_valid_data(self):
        """Тест валидных данных для UserSerializer"""
        serializer = UserSerializer(data={
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'phone': '+79997654321'
        })

        self.assertTrue(serializer.is_valid())
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['email'], 'new@example.com')
        self.assertEqual(validated_data['first_name'], 'Jane')

    def test_user_serializer_invalid_email(self):
        """Тест невалидного email для UserSerializer"""
        serializer = UserSerializer(data={
            'email': 'invalid-email',
            'password': 'test123'
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_user_serializer_missing_email(self):
        """Тест отсутствия email для UserSerializer"""
        serializer = UserSerializer(data={
            'password': 'test123'
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_user_serializer_password_write_only(self):
        """Тест что пароль только для записи"""
        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertNotIn('password', data)

    def test_user_serializer_read_only_fields(self):
        """Тест read_only полей"""
        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertIn('id', data)
        # ID должно быть read-only
        update_data = {'id': 999}
        serializer = UserSerializer(self.user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        # ID не должно измениться
        updated_user = serializer.save()
        self.assertNotEqual(updated_user.id, 999)

    def test_public_user_serializer_fields(self):
        """Тест полей PublicUserSerializer"""
        serializer = PublicUserSerializer(self.user)
        data = serializer.data

        # Проверяем наличие ожидаемых полей
        expected_fields = ['id', 'email', 'first_name', 'phone', 'tg_id', 'avatar']
        for field in expected_fields:
            self.assertIn(field, data)

        # Проверяем отсутствие приватных полей
        self.assertNotIn('last_name', data)
        self.assertNotIn('password', data)
        self.assertNotIn('token', data)

    def test_public_user_serializer_all_fields_read_only(self):
        """Тест что все поля PublicUserSerializer только для чтения"""
        serializer = PublicUserSerializer(self.user)
        data = serializer.data

        # Попытка изменить данные через сериализатор
        update_data = {'first_name': 'Hacked'}
        serializer = PublicUserSerializer(self.user, data=update_data, partial=True)

        # Должен быть валидным, но поля не изменятся из-за read_only
        self.assertTrue(serializer.is_valid())
        # Но при сохранении изменения не применятся
        if serializer.is_valid():
            updated_user = serializer.save()
            # original first_name не должен измениться
            self.user.refresh_from_db()
            self.assertEqual(self.user.first_name, 'John')