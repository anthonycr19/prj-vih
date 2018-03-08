from django.views.generic import TemplateView

from apps.common.views import (EnfermeriaProtectedView, MedicoProtectedView,
                               MinsaLoginRequiredView, BrigadistaAdminProtectedView)


class DashboardHomeView(MinsaLoginRequiredView, TemplateView):
    template_name = 'dashboard/home.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.doesnt_need_role = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'rol': self.get_rol()
        })
        return context

    def get_rol(self):
        user_roles = set(self.get_roles())
        if user_roles.intersection(set(EnfermeriaProtectedView.auth_roles)):
            return 'psicologia'
        elif user_roles.intersection(set(MedicoProtectedView.auth_roles)):
            return 'medico'
        elif user_roles.intersection(set(BrigadistaAdminProtectedView.auth_roles)):
            return 'brigadista'
        return False
