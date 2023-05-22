# ODevLib provided models

## `OModel`

ODevLib provides a general-purpose `OModel` class as a drop-in replacement for `models.Model`.

It adds the following fields:
- `created_at` — datetime of object creation
- `updated_at` — datetime of object update
- `created_by` — user who created the object
- `updated_by` — user who updated the object

Additionally, it ads simple_history support with `history` field, so you don't find yourself in a situation where you need to audit object update history and suddenly realize that you forgot to add history support there. Believe, it happened to us :)
