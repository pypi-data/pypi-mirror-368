DCP-CWGCs construction
======================

.. code-block:: python

   import codepub as cdp

.. _construction-bba-section:

BBA: quickstart
---------------

.. code-block:: python

   import codepub as cdp

   # number of pools
   m = 12
   # address weight (i.e. to how many pools one item is added)
   r = 4
   # number of items
   n = 200

   # arrangement and its balance
   balance, H = cdp.bba(m, r, n)

.. code-block:: python

    >>> balance
    [65, 67, 68, 68, 65, 66, 66, 67, 67, 68, 66, 67]

    >>> H[:10]
    [[0, 1, 2, 3], [1, 2, 3, 4], [1, 2, 4, 9], [1, 4, 9, 11],
    [4, 8, 9, 11], [8, 9, 10, 11], [5, 8, 10, 11], [5, 7, 8, 10],
    [5, 6, 7, 10], [0, 5, 6, 7]]

.. _construction-rcbba-section:

rcBBA: quickstart
-----------------

.. code-block:: python

   import codepub as cdp

   # number of pools
   m = 12
   # address weight (i.e. to how many pools one item is added)
   r = 4
   # number of item
   n = 200

   # arrangemement and its balance
   balance, H = cdp.rcbba(m, r, n)

.. code-block:: python

    >>> balance
    array([67, 66, 67, 69, 67, 67, 66, 68, 65, 66, 66, 66])

    >>> H[:10]
    [[2, 3, 4, 7], [0, 2, 3, 7], [0, 3, 7, 8], [0, 1, 3, 7],
    [0, 1, 3, 6], [0, 3, 4, 6], [2, 3, 4, 6], [2, 4, 6, 8],
    [1, 2, 4, 8], [1, 4, 7, 8]]

