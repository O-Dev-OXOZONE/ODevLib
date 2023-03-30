import warnings

from django_filters.rest_framework import DjangoFilterBackend  # type: ignore

import odevlib.drf_spectacular.ofilter_extension as ext

# Import for side effects
_ = ext


class OFilterBackend(DjangoFilterBackend):
    def get_schema_operation_parameters(self, view):
        try:
            queryset = view.get_queryset()
        except Exception:
            queryset = None
            warnings.warn(f"View {view.__class__} is not compatible with schema generation because it has no queryset")

        filterset_class = self.get_filterset_class(view, queryset)

        if not filterset_class:
            return []

        parameters = []
        for field_name, field in filterset_class.base_filters.items():
            parameter = {
                'name': field_name,
                'required': field.extra['required'],
                'in': 'query',
                'description': field.label if field.label is not None else field_name,
                'schema': {
                    'type': 'string',
                },
            }
            if field.extra and 'choices' in field.extra:
                parameter['schema']['enum'] = [c[0] for c in field.extra['choices']]
            parameters.append(parameter)
        return parameters
