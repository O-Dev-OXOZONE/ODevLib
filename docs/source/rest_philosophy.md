# REST API philosophy in ODevLib

## ODevLib flavor of REST API

Usually, single view in DRF uses single serializer. But in ODL, we have two or three serializers:

- Retrieve serializer. Used in ALL responses.
- Create serializer. Used in request bodies of POST requests, and in PUT/PATCH, if update serializer is not specified.
- Optional update serializer. If specified, used in bodies of PUT/PATCH requests.

For example, POST endpoint uses create serializer as a request body and retrieve serializer as response body. Note that
data you send to server differs from data you receive from server.

Usually, though, you get the same fields in retrieve/create/update serializers, plus some extra fields in retrieve
serializers, i.e. primary keys in `id` field, and some computed stuff.