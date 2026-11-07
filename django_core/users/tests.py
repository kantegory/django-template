import io
from http import HTTPStatus
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from dmr.test import DMRClient

from users.constants import AuthErrorCode
from users.tasks import example_task

User = get_user_model()


class UserAuthAPITests(TestCase):
    def setUp(self):
        self.client = DMRClient()
        self.username = "testuser"
        self.password = "StrongPass123!"
        self.email = "testuser@example.com"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email,
            first_name="Test",
            last_name="User",
        )

    def test_register_success(self):
        payload = {
            "username": "newuser",
            "password": "Password123!",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "Person",
        }
        response = self.client.post("/api/auth/register/", data=payload)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        data = response.json()
        self.assertEqual(data["username"], "newuser")
        self.assertEqual(data["email"], "newuser@example.com")
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_duplicate_username(self):
        payload = {
            "username": self.username,
            "password": "Password123!",
            "email": "different@example.com",
        }
        response = self.client.post("/api/auth/register/", data=payload)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        error = response.json()["detail"][0]
        self.assertEqual(error["type"], AuthErrorCode.USERNAME_EXISTS)
        self.assertEqual(error["loc"], ["parsed_body", "username"])

    def test_register_duplicate_email(self):
        payload = {
            "username": "uniquename",
            "password": "Password123!",
            "email": self.email,
        }
        response = self.client.post("/api/auth/register/", data=payload)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        error = response.json()["detail"][0]
        self.assertEqual(error["type"], AuthErrorCode.EMAIL_EXISTS)
        self.assertEqual(error["loc"], ["parsed_body", "email"])

    def test_login_success(self):
        payload = {
            "username": self.username,
            "password": self.password,
        }
        response = self.client.post("/api/auth/login/", data=payload)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)

    def test_login_invalid_credentials(self):
        payload = {
            "username": self.username,
            "password": "wrongpassword",
        }
        response = self.client.post("/api/auth/login/", data=payload)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_me_endpoint_with_valid_token(self):
        login_resp = self.client.post(
            "/api/auth/login/",
            data={"username": self.username, "password": self.password},
        )
        access_token = login_resp.json()["access_token"]

        response = self.client.get(
            "/api/auth/me/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(data["username"], self.username)
        self.assertEqual(data["email"], self.email)
        self.assertEqual(data["id"], self.user.id)

    def test_me_endpoint_without_token(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_refresh_token_with_rotation(self):
        login_resp = self.client.post(
            "/api/auth/login/",
            data={"username": self.username, "password": self.password},
        )
        initial_refresh = login_resp.json()["refresh_token"]

        refresh_resp = self.client.post(
            "/api/auth/jwt/refresh/",
            data={"refresh_token": initial_refresh},
        )
        self.assertEqual(refresh_resp.status_code, HTTPStatus.OK)
        rotated_data = refresh_resp.json()
        self.assertIn("access_token", rotated_data)
        self.assertIn("refresh_token", rotated_data)

        # Old refresh token should now be blacklisted due to rotation
        reuse_resp = self.client.post(
            "/api/auth/jwt/refresh/",
            data={"refresh_token": initial_refresh},
        )
        self.assertEqual(reuse_resp.status_code, HTTPStatus.UNAUTHORIZED)
        error = reuse_resp.json()["detail"][0]
        self.assertEqual(error["type"], AuthErrorCode.TOKEN_BLACKLISTED)

    def test_token_blacklist_logout(self):
        login_resp = self.client.post(
            "/api/auth/login/",
            data={"username": self.username, "password": self.password},
        )
        refresh_token = login_resp.json()["refresh_token"]

        blacklist_resp = self.client.post(
            "/api/auth/jwt/blacklist/",
            data={"refresh_token": refresh_token},
        )
        self.assertEqual(blacklist_resp.status_code, HTTPStatus.OK)
        self.assertIn("detail", blacklist_resp.json())

        # Attempt to use blacklisted refresh token
        retry_resp = self.client.post(
            "/api/auth/jwt/refresh/",
            data={"refresh_token": refresh_token},
        )
        self.assertEqual(retry_resp.status_code, HTTPStatus.UNAUTHORIZED)
        error = retry_resp.json()["detail"][0]
        self.assertEqual(error["type"], AuthErrorCode.TOKEN_BLACKLISTED)

    def test_token_blacklist_invalid_token(self):
        blacklist_resp = self.client.post(
            "/api/auth/jwt/blacklist/",
            data={"refresh_token": "invalid.jwt.token"},
        )
        self.assertEqual(blacklist_resp.status_code, HTTPStatus.BAD_REQUEST)
        error = blacklist_resp.json()["detail"][0]
        self.assertEqual(error["type"], AuthErrorCode.INVALID_TOKEN)

    def test_verify_token(self):
        login_resp = self.client.post(
            "/api/auth/login/",
            data={"username": self.username, "password": self.password},
        )
        access_token = login_resp.json()["access_token"]

        # Valid token returns 204 No Content
        verify_resp = self.client.post(
            "/api/auth/jwt/verify/",
            data={"access_token": access_token},
        )
        self.assertEqual(verify_resp.status_code, HTTPStatus.NO_CONTENT)

        # Invalid token returns 401 Unauthorized
        invalid_resp = self.client.post(
            "/api/auth/jwt/verify/",
            data={"access_token": "invalid.jwt.token"},
        )
        self.assertEqual(invalid_resp.status_code, HTTPStatus.UNAUTHORIZED)


class DramatiqTasksTests(TestCase):
    def test_example_task_execution(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            example_task.fn("custom message")
            output = mock_out.getvalue()
        self.assertIn("[Dramatiq] Task executed: custom message", output)

    def test_example_task_default_argument(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            example_task.fn()
            output = mock_out.getvalue()
        self.assertIn("[Dramatiq] Task executed: Hello from Dramatiq", output)
