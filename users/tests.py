from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from users.serializers import UserSerializer, PublicUserSerializer
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.urls import reverse
from users.permissions import IsOwner, IsOwnerOrReadOnly

User = get_user_model()


# ТЕСТИРОВАНИЕ МОДЕЛИ USER---------------------------------------------------
class UserModelTest(TestCase):
    """Тесты для модели User"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe",
        }

    def test_create_user(self):
        """Тест создания обычного пользователя"""
        user = User.objects.create(**self.user_data)

        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.first_name, self.user_data["first_name"])
        self.assertEqual(user.last_name, self.user_data["last_name"])
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        superuser = User.objects.create(
            email="admin@example.com",
            password="adminpassword123",
            is_staff=True,
            is_superuser=True
        )

        self.assertEqual(superuser.email, "admin@example.com")
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
            "phone": "+79991234567",
            "tg_id": "123456789",
            "token": "test_token_123",
        }
        user = User.objects.create(**user_data_with_optional)

        self.assertEqual(user.phone, "+79991234567")
        self.assertEqual(user.tg_id, "123456789")
        self.assertEqual(user.token, "test_token_123")

    def test_blank_optional_fields(self):
        """Тест что опциональные поля могут быть пустыми"""
        user = User.objects.create(**self.user_data)

        self.assertIsNone(user.phone)
        self.assertIsNone(user.tg_id)
        self.assertIsNone(user.token)

    def test_user_string_representation(self):
        """Тест строкового представления пользователя"""
        user = User.objects.create(**self.user_data)
        self.assertEqual(str(user), self.user_data["email"])

    def test_verbose_names(self):
        """Тест verbose names модели"""
        user = User.objects.create(**self.user_data)

        self.assertEqual(user._meta.verbose_name, "Пользователь")
        self.assertEqual(user._meta.verbose_name_plural, "Пользователи")

    def test_email_required(self):
        """Тест что email обязателен для заполнения"""
        User.objects.create(email="", password="testpassword123")
        self.assertRaises(ValueError)

    def test_password_required(self):
        """Тест что пароль обязателен для заполнения"""
        User.objects.create(email="test2@example.com", password="")
        self.assertRaises(ValueError)

    def test_user_ordering(self):
        """Тест порядка сортировки пользователей"""
        user1 = User.objects.create(
            email="user1@example.com",
            password="password123"
        )
        user2 = User.objects.create(
            email="user2@example.com",
            password="password123"
        )

        users = User.objects.all()
        self.assertEqual(users[0], user1)
        self.assertEqual(users[1], user2)

    def test_phone_max_length(self):
        """Тест максимальной длины поля phone"""
        user = User.objects.create(
            email="phone_test@example.com",
            password="password123",
            phone="1" * 35  # Максимальная длина
        )
        self.assertEqual(len(user.phone), 35)

    def test_tg_id_max_length(self):
        """Тест максимальной длины поля tg_id"""
        user = User.objects.create(
            email="tg_test@example.com",
            password="password123",
            tg_id="1" * 50  # Максимальная длина
        )
        self.assertEqual(len(user.tg_id), 50)

    def test_token_max_length(self):
        """Тест максимальной длины поля token"""
        user = User.objects.create(
            email="token_test@example.com",
            password="password123",
            token="1" * 100  # Максимальная длина
        )
        self.assertEqual(len(user.token), 100)

    def test_user_permissions(self):
        """Тест базовых разрешений пользователя"""
        user = User.objects.create(**self.user_data)

        # Обычный пользователь не должен иметь особых разрешений
        self.assertFalse(user.has_perm("auth.add_user"))
        self.assertFalse(user.has_perm("auth.change_user"))
        self.assertFalse(user.has_perm("auth.delete_user"))

    def test_superuser_permissions(self):
        """Тест разрешений суперпользователя"""
        superuser = User.objects.create(
            email="super@example.com",
            password="superpassword123",
            is_staff=True,
            is_superuser=True
        )

        # Суперпользователь должен иметь все разрешения
        self.assertTrue(superuser.has_perm("auth.add_user"))
        self.assertTrue(superuser.has_perm("auth.change_user"))
        self.assertTrue(superuser.has_perm("auth.delete_user"))
        self.assertTrue(superuser.has_perm("some_nonexistent_permission"))


# ТЕСТИРОВАНИЕ СЕРИАЛИЗАТОРОВ USER---------------------------------------------------
class UserSerializerTest(TestCase):
    """Тесты для сериализаторов пользователя"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+79991234567",
            "tg_id": "123456789"
        }
        self.user = User.objects.create(**self.user_data)

    def test_user_serializer_valid_data(self):
        """Тест валидных данных для UserSerializer"""
        serializer = UserSerializer(data={
            "email": "new@example.com",
            "password": "newpass123",
            "first_name": "Jane",
            "last_name": "Smith",
            "phone": "+79997654321"
        })

        self.assertTrue(serializer.is_valid())
        validated_data = serializer.validated_data
        self.assertEqual(validated_data["email"], "new@example.com")
        self.assertEqual(validated_data["first_name"], "Jane")

    def test_user_serializer_invalid_email(self):
        """Тест невалидного email для UserSerializer"""
        serializer = UserSerializer(data={
            "email": "invalid-email",
            "password": "test123"
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_user_serializer_missing_email(self):
        """Тест отсутствия email для UserSerializer"""
        serializer = UserSerializer(data={
            "password": "test123"
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_user_serializer_password_write_only(self):
        """Тест что пароль только для записи"""
        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertNotIn("password", data)

    def test_user_serializer_read_only_fields(self):
        """Тест read_only полей"""
        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertIn("id", data)
        # ID должно быть read-only
        update_data = {"id": 999}
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
        expected_fields = ["id", "email", "first_name", "phone", "tg_id", "avatar"]
        for field in expected_fields:
            self.assertIn(field, data)

        # Проверяем отсутствие приватных полей
        self.assertNotIn("last_name", data)
        self.assertNotIn("password", data)
        self.assertNotIn("token", data)

    def test_public_user_serializer_all_fields_read_only(self):
        """Тест что все поля PublicUserSerializer только для чтения"""
        serializer = PublicUserSerializer(self.user)
        serializer.data

        # Попытка изменить данные через сериализатор
        update_data = {"first_name": "Hacked"}
        serializer = PublicUserSerializer(self.user, data=update_data, partial=True)

        # Должен быть валидным, но поля не изменятся из-за read_only
        self.assertTrue(serializer.is_valid())
        # Но при сохранении изменения не применятся
        if serializer.is_valid():
            serializer.save()
            # original first_name не должен измениться
            self.user.refresh_from_db()
            self.assertEqual(self.user.first_name, "John")


# ТЕСТЫ ДЛЯ ПРЕДСТАВЛЕНИЙ -----------------------------------------------
class UserViewsTest(APITestCase):
    """Тесты для представлений пользователя"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "John",
            "last_name": "Doe"
        }
        self.user = User.objects.create(**self.user_data)

        self.other_user = User.objects.create(
            email="other@example.com",
            password="otherpass123",
            first_name="Other"
        )

    def test_user_registration_success(self):
        """Тест успешной регистрации пользователя"""
        url = reverse("users:user-create")
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "phone": "+79991234567"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

        # Проверяем что пароль хешируется
        new_user = User.objects.get(email="newuser@example.com")
        self.assertTrue(new_user.check_password("newpass123"))
        self.assertNotEqual(new_user.password, "newpass123")  # Пароль должен быть хеширован

    def test_user_registration_invalid_data(self):
        """Тест регистрации с невалидными данными"""
        url = reverse("users:user-create")
        data = {
            "email": "invalid-email",
            "password": "123"  # Слишком короткий пароль
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_user_login_success(self):
        """Тест успешного входа пользователя"""
        # Сначала регистрируем.
        url_reg = reverse("users:user-create")
        # Потом логин
        url = reverse("users:login")
        data = {
            "email": "login@example.com",
            "password": "loginpass123"
        }

        self.client.post(url_reg, data)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_invalid_credentials(self):
        """Тест входа с неверными учетными данными"""

        url = reverse("users:login")
        data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_own_profile_authenticated(self):
        """Тест получения своего профиля аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-retrieve", args=[self.user.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["first_name"], self.user.first_name)
        # Должны видеть все свои данные (UserSerializer)
        self.assertIn("last_name", response.data)

    def test_get_other_user_profile_authenticated(self):
        """Тест получения чужого профиля аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-retrieve", args=[self.other_user.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.other_user.email)
        # Должны видеть только публичные данные (PublicUserSerializer)
        self.assertNotIn("last_name", response.data)

    def test_get_profile_unauthenticated(self):
        """Тест получения профиля без аутентификации"""
        url = reverse("users:user-retrieve", args=[self.user.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_own_profile(self):
        """Тест обновления своего профиля"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-update", args=[self.user.id])
        data = {
            "first_name": "UpdatedName",
            "phone": "+79998887766"
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "UpdatedName")
        self.assertEqual(self.user.phone, "+79998887766")

    def test_update_other_user_profile(self):
        """Тест попытки обновления чужого профиля"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-update", args=[self.other_user.id])
        data = {"first_name": "Hacked"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_profile(self):
        """Тест удаления своего профиля"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-delete", args=[self.user.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_other_user_profile(self):
        """Тест попытки удаления чужого профиля"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-delete", args=[self.other_user.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_authenticated(self):
        """Тест получения списка пользователей аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должны видеть только публичные данные всех пользователей
        users_data = response.data["results"]  # Учитываем пагинацию
        self.assertTrue(len(users_data) >= 2)  # Как минимум 2 пользователя

        for user_data in users_data:
            self.assertIn("email", user_data)
            self.assertIn("first_name", user_data)
            self.assertNotIn("last_name", user_data)  # Приватные данные скрыты

    def test_list_users_unauthenticated(self):
        """Тест получения списка пользователей без аутентификации"""
        url = reverse("users:user-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ТЕСТЫ ДЛЯ ПЕРМИШИНОВ -----------------------------------------------
class PermissionsTest(TestCase):
    """Тесты для кастомных разрешений"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.factory = APIRequestFactory()
        self.user = User.objects.create(
            email="test@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create(
            email="other@example.com",
            password="otherpass123"
        )

    def test_is_owner_permission_same_user(self):
        """Тест IsOwner разрешения для владельца объекта"""
        permission = IsOwner()
        request = self.factory.get("/")
        request.user = self.user

        # Для модели User
        self.assertTrue(permission.has_object_permission(request, None, self.user))

    def test_is_owner_permission_different_user(self):
        """Тест IsOwner разрешения для чужого пользователя"""
        permission = IsOwner()
        request = self.factory.get("/")
        request.user = self.other_user

        # Для модели User - другой пользователь
        self.assertFalse(permission.has_object_permission(request, None, self.user))

    def test_is_owner_or_read_only_safe_methods(self):
        """Тест IsOwnerOrReadOnly для безопасных методов"""
        permission = IsOwnerOrReadOnly()

        # Тестируем безопасные методы
        safe_methods = ["GET", "HEAD", "OPTIONS"]
        for method in safe_methods:
            request = self.factory.get("/")
            request.method = method
            request.user = self.other_user  # Чужой пользователь

            # Должен иметь доступ для безопасных методов
            self.assertTrue(permission.has_object_permission(request, None, self.user))

    def test_is_owner_or_read_only_unsafe_methods_owner(self):
        """Тест IsOwnerOrReadOnly для небезопасных методов владельцем"""
        permission = IsOwnerOrReadOnly()

        # Тестируем небезопасные методы для владельца
        unsafe_methods = ["POST", "PUT", "PATCH", "DELETE"]
        for method in unsafe_methods:
            request = self.factory.get("/")
            request.method = method
            request.user = self.user  # Владелец

            # Должен иметь доступ для небезопасных методов
            self.assertTrue(permission.has_object_permission(request, None, self.user))

    def test_is_owner_or_read_only_unsafe_methods_non_owner(self):
        """Тест IsOwnerOrReadOnly для небезопасных методов не-владельцем"""
        permission = IsOwnerOrReadOnly()

        # Тестируем небезопасные методы для не-владельца
        unsafe_methods = ["POST", "PUT", "PATCH", "DELETE"]
        for method in unsafe_methods:
            request = self.factory.get("/")
            request.method = method
            request.user = self.other_user  # Не владелец

            # Не должен иметь доступ для небезопасных методов
            self.assertFalse(permission.has_object_permission(request, None, self.user))
