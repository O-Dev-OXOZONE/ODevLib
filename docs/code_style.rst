Code style recommendations
==========================

Exit point minimization
+++++++++++++++++++++++

The more exit points you make in your function, the more difficult it is to
understand.  Try to minimize the number of exit points in your functions.

This also applies to loop. For example, instead of

.. code-block:: python

    transactions = []
    errors = []
    for task in asyncio.as_completed(asyncio_tasks):
        result = await task
        if isinstance(result, Error):
            errors.append(result)
            continue
        transactions.extend(result)
    return transactions, errors

you can do

.. code-block:: python

    transactions = []
    errors = []
    for task in asyncio.as_completed(asyncio_tasks):
        result = await task
        if isinstance(result, Error):
            errors.append(result)
        else:
            transactions.extend(result)
    return transactions, errors

while in this example it doesn't make much difference, in more complex
and lengthy functions you may spend hours debugging exit points configuration,
especially in a someone else's code.
