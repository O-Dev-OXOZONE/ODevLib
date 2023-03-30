# RBAC-based Permission System

ODevLib provides an implementation of RBAC-based permission system. You can read
more about the theory of it
at [Wikipedia](https://en.wikipedia.org/wiki/Role-based_access_control).

This permission system goes deeper than Django/DRF one and Simple Permission
System of ODevLib. It allows for access control on a field level.

## Core concepts

**S** = Subject — a Django user (auth_user);

**R** = Role — a role object that is stored in the database and can be
configured by the moderator or administrator;

**P** = Permission — a virtual approval of accessing resource (view/field) for
certain mode of access. Does not have database entry, as it is derived from
the code at runtime.

**SA** = Subject Assignment. Many-to-many relation between subject (user) and
role.

**PA** = Permission Assignment. Many-to-many relation between role and
permission. Implemented as a HStore field in a Role object.

**RH** = Partially ordered Role Hierarchy. Many-to-many relation between role
and role stating that one role inherits all properties of another role. This is
useful when pairs of read-access/write-access roles should be created — in this
case, there's no need to explicitly specify read permissions for the
write-access role.
**Parent inherits all children's permissions** (order matters).

## Backend-view on RBAC API

Roles may be created by migrations, via API and via Django admin panel. The
primary key `id` of a role is of integer type for performance reasons, but the
actual key used throughout the code is `name` — it is of text type and is
immutable. The only way to set `name` is to create a new role. This minimizes
the risk of messing everything up by inexperienced users having raw access to
the database 🌚. There's also a `ui_name` field used to display the current role
in website/apps.

The preferred way to name roles is the same as naming model tables in
Django: `{app_name}_{role_name}`.

Views may be assigned to a specific role using decorator:

```python
@rbac("appname_rolename")
def view(request: Request, *args, **kwargs):
    ...
```

OViewSet can use roles as well:

```python
class MyViewSet(OModelViewSet):
    rbac_role = "myapp_myrole"
    ...
```

## Role internals

As stated earlier, the role consists of 4 fields:

- `id` — integer primary key;
- `name` — immutable text key used in code;
- `ui_name` — text name used in UI of website/apps;
- `permissions` — HStore field that stores list of allowed permissions.

Scopes of permissions are not limited, they may give access to any model in the
project, both read and write, and can go deeper to give permissions on specific
fields of the models.

The example of permissions value is:

```json5
{
  'auth__user': 'r',
  // Read access to the entire auth_user model
  'core_profile': 'rwd',
  // Read/write/delete access to the entire core_profile model
  'auth__user__first_name': 'w'
  // Write access to the first_name field of auth_user model
}
```

You can see that key consists of 2 or 3 parts: first part is the app name,
second part is the model name, and the third, optional, part is the field name.

### Turning this into instance-level access control

From the above declarations, it can be clearly seen that subject may be given
access to a particular resource. In the above case, resources are views or
fields. But what if we make instances resource as well? We may include
primary key of the instance in model part of the permission to make it work
only on an instance with a particular primary key. The examples of such
permissions are: `odevlib__rbacrole[1]`, `odevlib__rbacrole[1]__ui_name`.

This of course only makes sense when correct hierarchy of roles and models
are set up.


## RBAC under the hood

Under the hood, RBAC has the following basic operations:

### Get user's roles
Returns direct role assignments of the user. Should not be used by the business logic of the application, since role
hierarchy is a thing. This is mostly internal operation, which is used by other operations.

### Get user's roles with children
Returns direct role assignments of the user and all roles that inherit from them. This operation may be used when
obtaining complete permissions of the user. Frontend may cache this when traversing UI components.

> Keep in mind that parent role inherits all of its children's permissions.

### Get user's roles with parents
??? When do we need this? ???

### Get user's instance-level roles
Returns direct role assignments of the user for a particular model instance. Should not be used by the business logic
of the application, since role hierarchy is a thing. This is mostly internal operation, which is used by other 
operations.

### Get user's instance-level roles with children
Returns direct role assignments of the user for a particular model instance and all roles that inherit from them. This
operation may be used when obtaining complete permissions of the user. Frontend may cache this when traversing UI **FOR
A PARTICULAR INSTANCE**, but keep in mind that these permissions are invalid outside the provided model instance.

> Keep in mind that parent role inherits all of its children's permissions.

### Get user's instance-level roles with parents
??? When do we need this? ???



## Frontend-view on RBAC API

RBAC API provides a way to list permissions of the caller on the requested view,
or even fields of the serializer attached to the requested view. This may be
helpful to remove or disable form fields on a website.

### GET `/odl/rbac/list_permissions/?view={view_url}`

Responses of that view have the following structure:

#### 200 OK

Returned in case given view exists and has RBAC attached.

`fields` field is optional and has value only if the view is configured to allow
different serializer fields depending on the role. Otherwise, the value will
be `null`.

```json5
{
  "able_to_call": "bool",
  "role": {
    "id": "int",
    // Database ID of the current role
    "name": "string",
    // Role name
  },
  "fields": [
    {
      "name": "string",
      // Name of the field in a serializer (typically — derived from a Django model)
      "get": "bool",
      // Used for LIST/GET requests of a ViewSet
      "create": "bool",
      // Used to POST request of a ViewSet
      "update": "bool",
      // Used for PATCH/PUT requests of a ViewSet
    },
    "..."
  ]
}  
```

#### 404 Not Found

If view with provided URL does not exist:

```json
{
  "error_code": 5,
  "eng_description": "Endpoint with provided URL \"{view_url}\" does not exist",
  "ui_description": "Эндпоинта с URL \"{view_url}\" не существует"
}  
```

#### 400 Invalid Request

If view with provided URL exists, but has no RBAC attached:

```json
{
  "error_code": 6,
  "eng_description": "Endpoint with provided URL \"{view_url}\" does not use RBAC permission system",
  "ui_description": "Эндпоинт с URL \"{view_url}\" не использует систему прав RBAC"
}  
```

