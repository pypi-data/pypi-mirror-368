from django.urls import path

from django_admin_models_search.views import AdminModelSuggestionsView

urlpatterns = [
    path(
        "admin/model-suggestions/",
        AdminModelSuggestionsView.as_view(),
        name="model_suggestions",
    )
]
