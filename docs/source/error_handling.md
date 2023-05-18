# Error handling with ODevLib

ODevLib provides an `Error` model. It contains the following fields:
- error_code — the code akin HTTP status codes. API user may use this code to determine the kind of error and handle it appropriately.
- eng_description — technical description of the error, which may be used by developers to trace down the error.
- ui_description — user-friendly description of the error, which may be shown to the user on the website or in the app.

Unhandled ODevLib errors are automatically saved to the database by a middleware, so developers may spot them without user reports.

Of course, it is always better to handle errors in the code, so try to handle them as soon as possible.

