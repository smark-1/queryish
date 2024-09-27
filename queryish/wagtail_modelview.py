try:
    from wagtail.admin.viewsets.base import ViewSet
    from django.urls import path
    from wagtail.permission_policies import ModelPermissionPolicy
    from wagtail.admin.views.generic.models import IndexView, InspectView
except ImportError:
    raise ImportError("Wagtail must be installed to use QueryishModelViewSet")


class ViewModelPermissionPolicy(ModelPermissionPolicy):
    def user_has_permission(self, *args, **kwargs):
        return True

    def users_with_any_permission(self, actions):
        return True

    def user_has_any_permission(self, user, *args, **kwargs):
        return True


class QueryishModelViewSet(ViewSet):
    model = None
    
    inspect_view_enabled = True
    list_display = []

    def get_list_display(self):
        if len(self.list_display) == 0:
            return self.model._meta.fields
        else:
            return self.list_display

    list_filter = []
    inspect_view_fields = []
    inspect_view_fields_exclude = []

    def get_inspect_view_kwargs(self, **kwargs):
        return {
            "template_name": "wagtailadmin/generic/inspect.html",
            "fields": self.inspect_view_fields,
            "fields_exclude": self.inspect_view_fields_exclude,
            **kwargs,
        }

    def index(self, request):
        return self.construct_view(IndexView, **self.get_index_view_kwargs())(request)
    
    @property
    def inspect_view(self):
        return self.construct_view(
            InspectView, **self.get_inspect_view_kwargs()
        )


    def get_common_view_kwargs(self, **kwargs):
        view_kwargs = super().get_common_view_kwargs(
            **{
                "model": self.model,
                "permission_policy": ViewModelPermissionPolicy,
                "index_url_name": self.get_url_name("index"),
                "history_url_name": self.get_url_name("history"),
                "usage_url_name": self.get_url_name("usage"),
                "header_icon": self.icon,
                "_show_breadcrumbs": True,
                **kwargs,
            }
        )

        if self.inspect_view_enabled:
            view_kwargs["inspect_url_name"] = self.get_url_name("inspect")
        return view_kwargs

    def get_index_view_kwargs(self, **kwargs):
        view_kwargs = {
            "template_name": "wagtailadmin/generic/index.html",
            "results_template_name": "wagtailadmin/generic/index_results.html",
            "list_display": self.get_list_display(),
            "list_filter": self.list_filter,
            "list_export": [],
            "export_headings": {},
            "export_filename": "file",
            "filterset_class": None,
            "search_fields": [],
            "search_backend_name": "default",
            "paginate_by": 20,
            **kwargs,
        }
        return view_kwargs

    def get_urlpatterns(self):
        url_patterns =  [
            path("", self.index, name="index"),
            
        ]
        
        if self.inspect_view_enabled:
            url_patterns.append(
                path("inspect/<str:pk>/", self.inspect_view, name="inspect")
            )
        return url_patterns
 