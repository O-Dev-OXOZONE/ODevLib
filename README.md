# ODevLib

PyPi: https://pypi.org/project/odevlib/

---

Opinionated O.dev Django helper library.

Current features are:
- `OModel` — custom model with handy fields included and built-in history using Simple History.
- `OModelSerializer`/`OModelCreateSerializer` — serializers for OModel that handle handy fields.
- `OViewSet` — custom viewset that reiterates on Django built-in viewsets.
- `OModelViewSet` — like the above, but includes all REST methods (auto-generated).

And many more!

## Project status

The library is in active use/development by O.dev backend team. Currently, the API is not stable and may change from
release to release, so please pin versions when including dependency.

The nature of the library (internal use for project development) implies that no strict roadmap exists, however, it
is planned to stabilize API, so it may only be changed during major version release.
