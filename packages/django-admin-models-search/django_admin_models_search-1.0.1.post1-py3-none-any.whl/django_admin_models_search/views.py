import django
import django.views
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.text import slugify


@method_decorator(staff_member_required, name="dispatch")
class AdminModelSuggestionsView(django.views.View):
    def get(self, request):
        query = request.GET.get("q", "").strip().lower()
        if len(query) < 2:
            return JsonResponse([], safe=False)

        suggestions = []

        for model in admin.site._registry.keys():
            opts = model._meta
            name = opts.verbose_name_plural
            name_slug = slugify(str(name))

            if query in name_slug or query in str(name).lower():
                suggestions.append(
                    {
                        "label": str(name),
                        "url": reverse(
                            "admin:%s_%s_changelist" % (opts.app_label, opts.model_name)
                        ),
                        "type": "model",
                        "app": opts.app_label,
                    }
                )

        suggestions.sort(
            key=lambda x: (
                0 if x["label"].lower().startswith(query) else 1,
                len(x["label"]),
            )
        )

        return JsonResponse(suggestions[:5], safe=False)
