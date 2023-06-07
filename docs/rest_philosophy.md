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

## How to name serializers

The convention used by ODevLib is to name serializers as:
- `<Model>Serializer` for retrieve serializer;
- `<Model>CreateSerializer` for create serializer;
- `<Model>UpdateSerializer` for update serializer.

You can have a subset of these serializers, but you will always have retrieve serializer, as it is used as response for
ANY endpoints (GET, PATCH, POST, all of them).

## How to name endpoints

The convention used by ODevLib is to name endpoints as:
- `/api/<subsystem>/<model>/` for ViewSet;
- `/api/<subsystem>/<model>/<pk>/<action>/` for actions.

You can also have function-based views, which are not covered by any convention, as they are specific for each task.
