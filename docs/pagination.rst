Pagination in ODevLib
=====================

Generally, there are two ways to implement pagination in a web application:

Limit-offset pagination
-----------------------
This type of pagination is easiest to implement, but it is also the least efficient and reliable. Basically, with this type of pagination you directly specify the database parameters to use when fetching data.

The problem with performance comes from the fact that when using offsets, database engine has to go all these skipped rows before it can return the requested data. This is especially problematic when you have a large number of rows in the table.

The problem with reliability comes from the fact that if you query a frequently mutated set of data, you will get duplicates and missing entries between API calls. ODevLib is built from the ground up to be used for high quality backend services, so we don't even consider unreliable practices and approaches.


Cursor pagination
-----------------
Cursor pagination is built on the principle of using a cursor to use current available data boundaries to fetch the surrounding data. It has its own disadvantages:
- Given that we can only fetch the surrounding data, we cannot jump to a random place in a dataset. This plays well with Single-Page Applications, which store the data on frontend, but it is not suitable for traditional multi-page applications.
- Logic of handling cursors is more complex than limit-offset pagination.

But in the end, when the client is implemented, we get a reliable way to keep our page with up-to-date information in realtime without ever needing to reload the page and load everything from scratch.

Okay, so how to work with the ODevLib cursor pagination?
--------------------------------------------------------

ODevLib provides OCursorPaginationListMixin as a drop-in replacement for OListMixin.

It has the following arguments:
- first_id — ID of the first row available on frontend. When specified, records older than this ID will be returned.
- last_id — ID of the last row available on frontend. When specified, records newer than this ID will be returned.
- count — maximum amount of records to return. Defaults to 50.

The response also includes a "X-ODEVLIB-HAS-MORE" header with "true" or "false" value, which tells if there are any more
records available in the database in the current direction.
