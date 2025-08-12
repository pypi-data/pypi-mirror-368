from django.contrib import admin
from django.contrib.auth.models import User
from django.test import LiveServerTestCase, RequestFactory, TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from django_admin_models_search.views import AdminModelSuggestionsView


class TestAdminModelSuggestionsView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_user = User.objects.create_superuser(
            username="admin", password="password", email="admin@example.com"
        )

        if not admin.site._registry:
            self.fail("No models are registered in the admin.")
        self.model = list(admin.site._registry.keys())[0]

    def test_no_query(self):
        """
        Given an admin user and no search query,
        When the user accesses the model suggestions endpoint,
        Then the response should be empty.
        """
        request = self.factory.get("/admin/model-suggestions/?q=")
        request.user = self.admin_user
        response = AdminModelSuggestionsView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [])

    def test_valid_query(self):
        """
        Given an admin user and a valid search query,
        When the user accesses the model suggestions endpoint,
        Then the response should contain the expected model suggestions.
        """
        request = self.factory.get(
            f"/admin/model-suggestions/?q={self.model._meta.verbose_name_plural}"
        )
        request.user = self.admin_user
        response = AdminModelSuggestionsView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            f"{self.model._meta.verbose_name_plural}", response.content.decode()
        )

    def test_permission_denied(self):
        """
        Given a non-admin user,
        When the user accesses the model suggestions endpoint,
        Then he is redirected to the login page.
        """
        request = self.factory.get(
            f"/admin/model-suggestions/?q={self.model._meta.verbose_name_plural}"
        )
        request.user = User.objects.create_user(username="user", password="password")
        response = AdminModelSuggestionsView.as_view()(request)
        # Should redirect to login page since user is not a staff member
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.headers["Location"])


class TestAdminSearchBar(LiveServerTestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", password="password", email="admin@example.com"
        )
        self.browser = webdriver.Chrome()
        if not admin.site._registry:
            self.fail("No models are registered in the admin.")
        self.model = list(admin.site._registry.keys())[0]

    def tearDown(self):
        self.browser.quit()

    def test_search_bar_suggestions(self):
        # login
        self.browser.get(f"{self.live_server_url}/admin/login/")
        self.browser.find_element(By.ID, "id_username").send_keys("admin")
        self.browser.find_element(By.ID, "id_password").send_keys("password")
        self.browser.find_element(By.XPATH, "//input[@type='submit']").click()

        self.browser.get(f"{self.live_server_url}/admin/")

        # use search bar
        search_bar = self.browser.find_element(By.ID, "admin-search-bar")
        search_bar.send_keys(f"{self.model._meta.verbose_name}")

        # Wait for suggestions to appear
        suggestions = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-suggestions"))
        )
        # Check that suggestions appear
        self.assertTrue(suggestions.is_displayed())
        self.assertIn(f"{self.model._meta.verbose_name_plural}", suggestions.text)
