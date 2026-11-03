from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.shortcuts import redirect, render


class LogoutView(BaseLogoutView):
    http_method_names = ("get", "post", "options")
    template_name = "accounts/logout_confirm.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        return render(request, self.template_name)
