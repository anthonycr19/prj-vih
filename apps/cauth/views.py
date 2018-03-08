# coding: utf-8
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse
from django.views.generic import RedirectView, FormView
from .models import User
from .forms import ChangePasswordForm


class Logout(RedirectView):

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        auth.logout(self.request)
        return reverse('login')


class ChangePasswordView(FormView):

    form_class = ChangePasswordForm

    def form_valid(self, form):
        self.request.user.set_password(form.cleaned_data['new_password'])
        self.request.user.save()
        return super(ChangePasswordView, self).form_valid(form)


def medicos(request, servicio):
    result = []
    items = User.objects.filter(servicio=servicio)
    for item in items:
        result.append({
            'id': item.id,
            'nombre': item.get_full_name()
        })
    return JsonResponse(result, safe=False)
