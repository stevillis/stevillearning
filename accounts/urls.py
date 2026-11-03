from django.contrib.auth import views as auth_views
from django.urls import path

from .views import LogoutView

app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
]
