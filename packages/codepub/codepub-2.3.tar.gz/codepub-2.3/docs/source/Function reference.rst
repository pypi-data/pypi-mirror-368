==================
Function reference
==================


.. _rsearch-section:

R search
--------

.. function:: factorial(num) -> int

   :param num: The number for which the factorial is calculated.
   :type num: int
   :return: The factorial of the given number.
   :rtype: int

   .. code-block:: python

      >>> factorial(5)
      120

.. function:: combination(m, k) -> int

      :param m: Total number of items (pools).
      :type m: int
      :param k: Number of items to choose (address weight).
      :type k: int
      :return: Number of possible combinations for choosing k items from m items.
      :rtype: int

      .. code-block:: python

         >>> cdp.combination(10, 3)
         120

.. function:: find_possible_k_values(m, n) -> collections.Counter

      :param m: number of pools
      :type m: int
      :param n: number of peptides
      :type n: int
      :return: list of possible peptide occurrences given number of pools and number of peptides.
      :rtype: collections.Counter

      .. code-block:: python

         >>> cdp.find_possible_k_values(12, 250)
         [4, 5, 6, 7, 8]

.. _reference-bba-section:

BBA functions
-------------

.. function:: union_address(address, union) -> list

      :param address: address (binary format)
      :type address: string
      :param union: previous union in the arrangement (binary format)
      :type union: string
      :return: unions in Adj(address)
      :rtype: list

      .. code-block:: python

         >>> cdp.union_address('110000', '111000')
         ['110100', '110010', '110001

.. function:: address_union(address, union) -> list

      :param address: previous address in the arrangement (binary format)
      :type address: string
      :param union: union (binary format)
      :type union: string
      :return: addresses in Adj(union)
      :rtype: list

      .. code-block:: python

         >>> cdp.address_union('011000', '111000')
         ['110000', '101000']

.. function:: searchpath(n, point, t, unions, H = None, W_des = None) -> list

      .. note:: This function is recursive. It is a core function for :func:`cdp.bba`, though it can work globally.

      :param n: required length of the arrangement
      :type n: int
      :param point: point to add
      :type point: string
      :param t: type of the point ('a' for address, 'u' for union)
      :type t: 'a' or 'u'
      :param unions: unions in the arrangement
      :type unions: list
      :param H: addresses in the arrangement
      :type H: list
      :param W_des: desired balance for the arrangement, optional
      :type W_des: list
      :return: resulting arrangement of the length n
      :rtype: list

      .. code-block:: python

         >>> cdp.searchpath(n=10, point = '110000', t = 'a', unions = ['111000'])
         ['110000', '100100', '000110', '000011', '001001', '010001', '010010', '011000', '001100', '101000']

.. function:: variance_score(bit_sums, s, W_des = None) -> float

      :param bit_sums: current balance of the arrangement
      :type bit_sums: list
      :param s: point to add
      :type s: string
      :param W_des: desired balance, optional
      :type s: list
      :return: penalty for the point based on how much less balanced the arrangement becomes after it is added
      :rtype: float

      .. code-block:: python

         >>> cdp.variance_score([2, 4, 4, 3, 3, 4], '110001')
         0.25

.. function:: return_address_message(code, mode) -> string or list

      :param code: an address in the index format (for example, [0, 1, 2]) or address in the binary format (for example, '111000')
      :type code: list of string
      :param mode: indicates whether an address has index or binary format if latter, than second letter (N) indicates number of pools
      :type mode: 'a' or 'mN'
      :return: corresponding address in the binary format ('111000') or in index format ([0, 1, 2])
      :rtype: string or list

      .. code-block:: python

         >>> cdp.return_address_message([1, 2, 4], 'm7')
         '0110100'
         >>> cdp.return_address_message('0111100', 'a')
         [1, 2, 3, 4]

.. function:: sum_bits(arr) -> list

      :param arr: arrangement with addresses
      :type arr: list
      :return: balance of the arrangement
      :rtype: list

      .. code-block:: python

         >>> cdp.sum_bits(['110001', '100101', '000111', '001110', '011010', '010110', '110100', '101100', '101001'])
         [5, 4, 4, 6, 4, 4]

.. function:: starts(m, r, start = None) -> dict

      :param m: number of pools in the arrangement
      :type m: int
      :param r: address weight in the arrangement, i.e. to how many pools one item is added
      :type r: int
      :param start: desired first address in binary format, optional
      :type start: str
      :return: possible pairs of addresses and unions in the dictionary, where addresses are keys, and unions are values
      :rtype: list

      .. code-block:: python

         >>> cdp.starts(5, 3)
         {'11100': ['11110', '11101'],
         '11010': ['11110', '11011'],
         '11001': ['11101', '11011'],
         '10110': ['11110', '10111'],
         '10101': ['11101', '10111'],
         '10011': ['11011', '10111'],
         '01110': ['11110', '01111'],
         '01101': ['11101', '01111'],
         '01011': ['11011', '01111'],
         '00111': ['10111', '01111']}
          >>> cdp.starts(5, 2, start = '11000')
         {'11000': ['11100', '11010', '11001']}

.. function:: bba(m, r, n, start_a = None, W_des = None) -> list, list

      .. note:: Search for arrangement may take some time, especially with large parameters. This function is **slower** than :func:`cdp.rcbba`, but is more reliable.

      :param m: number of pools
      :type m: int
      :param r: address weight, i.e. to how many pools one item is added
      :type r: int
      :param n: number of items
      :type n: int
      :param start_a: desired first address of the arrangement, optional
      :type start_a: str
      :param W_des: desired balance for the resulting arrangement
      :type W_des: 
      :return:
         1) list with number of item in each pool, i.e. balance;
         2) list with address arrangement
      :rtype: list, list

      .. code-block:: python

         >>> b, H = cdp.bba(n_pools=12, iters=4, len_lst=250)
         >>> b
         [81, 85, 85, 85, 81, 82, 87, 81, 85, 81, 84, 83]
         >>> H
         [[0, 1, 2, 3],[0, 1, 3, 6],[0, 1, 6, 8],[1, 6, 8, 9],[6, 8, 9, 11], ... ]

.. _reference-rcbba-section:

rcBBA functions
---------------

.. function:: item_per_pool(addresses, m) -> numpy array

      :param addresses: matrix with addresses
      :type addresses: numpy array
      :param m: number of pools
      :type m: int
      :return: balance of the arrangement
      :rtype: numpy array

      .. code-block:: python

         >>> cdp.item_per_pool([[2, 3, 4, 7], [0, 2, 3, 7], [0, 3, 7, 8], [0, 1, 3, 7], [0, 1, 3, 6], [0, 3, 4, 6], [2, 3, 4, 6], [2, 4, 6, 8], [1, 2, 4, 8], [1, 4, 7, 8]], 10)
         array([5, 4, 5, 7, 6, 0, 4, 5, 4])

.. function:: list_union(address_matrix) -> numpy array

      :param address_matrix: matrix with addresses
      :type address_matrix: numpy array
      :return: matrix with unions
      :rtype: numpy array

      .. code-block:: python

         >>> cdp.item_per_pool(np.array([[2, 3, 4, 7], [0, 2, 3, 7], [0, 3, 7, 8], [0, 1, 3, 7], [0, 1, 3, 6], [0, 3, 4, 6], [2, 3, 4, 6], [2, 4, 6, 8], [1, 2, 4, 8], [1, 4, 7, 8]]))
         array([[0, 2, 3, 4, 7], [0, 2, 3, 7, 8], [0, 1, 3, 7, 8], [0, 1, 3, 6, 7], [0, 1, 3, 4, 6], [0, 2, 3, 4, 6], [2, 3, 4, 6, 8], [1, 2, 4, 6, 8], [1, 2, 4, 7, 8]])

.. function:: bAU_search(address_matrix, m, I_res) -> list

      :param address_matrix: matrix with addresses
      :type address_matrix: numpy array
      :param m: number of pools
      :type m: int
      :param I_res: residual index set
      :type I_res: list
      :return: list of possible b's
      :rtype: list of lists

      .. code-block:: python

         >>> cdp.bAU_search(np.array([[0, 1, 2, 3, 9], [0, 1, 2, 4, 9], [1, 2, 4, 8, 9], [2, 4, 7, 8, 9], [4, 6, 7, 8, 9]]), 10, [0, 1, 2, 3, 4, 5, 6, 7, 8])
         array([[0, 1, 2, 3, 5], [0, 1, 2, 3, 6], [0, 1, 2, 3, 7], [0, 1, 2, 3, 8]])

.. function:: permutation_map(address_matrix, k, b, m, I_res, p=-1) -> numpy array

      :param address_matrix: matrix with addresses
      :type address_matrix: numpy array
      :param k: row index
      :type k: int
      :param b: target address
      :type b: list
      :param m: number of pools
      :type m: int
      :param I_res: residual index set
      :type I_res: list
      :return: matrix with addresses permuted acccording to found map
      :rtype: numpy array

      .. code-block:: python

         >>> cdp.permutation_map(np.array([[0, 1, 8], [1, 2, 8], [2, 3, 8], [3, 4, 8], [4, 6, 8], [6, 7, 8], [5, 7, 8], [0, 5, 8], [1, 5, 8], [4, 5, 8], [0, 4, 8], [0, 2, 8], [0, 3, 8], [3, 7, 8], [3, 6, 8], [2, 6, 8], [2, 7, 8], [1, 7, 8], [1, 6, 8], [5, 6, 8], [3, 5, 8], [2, 5, 8], [2, 4, 8]]), -1, (0, 1, 3), 9, [0, 1, 2, 3, 4, 5, 6, 7, 8])
         array([[2, 3, 4], [0, 3, 4], [0, 3, 5], [1, 3, 5], [1, 3, 7], [3, 7, 8], [3, 6, 8], [2, 3, 6], [3, 4, 6], [1, 3, 6], [1, 2, 3], [0, 2, 3], [2, 3, 5], [3, 5, 8], [3, 5, 7], [0, 3, 7], [0, 3, 8], [3, 4, 8], [3, 4, 7], [3, 6, 7], [3, 5, 6], [0, 3, 6], [0, 1, 3]])

.. function:: gen_elementary_sequence(m, r, I_res, w, b = None) -> numpy array, list

      :param m: number of pools
      :type m: int
      :param r: address weight, i.e. number of pools to which one item is added
      :type r: int
      :param I_res: residual index set
      :type I_res: list
      :param w: required length of the component
      :type w: int
      :param b: required first address of the permuted sequence, optional
      :type b: list
      :return:
         1) generated component
         2) updated residual index set
      :rtype: numpy array, list

      .. code-block:: python

         >>> component, I_res_new = cdp.gen_elementary_sequence(9, 3, [0, 1, 2, 3, 4, 5, 6, 7, 8], 23, (0, 1, 4))
         >>> component
         array([[2, 3, 4], [0, 3, 4], [0, 4, 7], [4, 5, 7], [4, 5, 6], [1, 4, 6], [1, 4, 8], [2, 4, 8], [0, 2, 4], [2, 4, 7], [2, 4, 5], [1, 4, 5], [1, 3, 4], [3, 4, 8], [4, 6, 8], [0, 4, 6], [4, 6, 7], [1, 4, 7], [3, 4, 7], [3, 4, 5], [0, 4, 5], [0, 4, 8], [0, 1, 4]])
         >>> I_res_new
         array([0, 1, 2, 3, 5, 6, 7, 8]))

.. function:: permute(start, b, m, I_res) -> dict

      :param start: an address that needs to be permuted
      :type start: list
      :param b: target address, i.e. how start should look like after the permutation
      :type b: list
      :param m: number of pools
      :type m: int
      :param I_res: available residual index set for the permutation map
      :type I_res: list
      :return: permutation map
      :rtype: dict 

      .. code-block:: python

         >>> cdp.permute([0, 1, 2], (0, 1, 4), 6, [0, 1, 2, 4, 5, 8])
         {2: 4, 0: 0, 1: 1, 3: 2, 4: 5, 5: 8}

.. function:: balancing_weights(arr) -> numpy array

      :param arr: residual balance vector
      :type arr: numpy array
      :return: residual balance vector without negative numbers
      :rtype: numpy array 

      .. code-block:: python

         >>> cdp.balancing_weights(np.array([8, 7, 0, 9, 10, 10, 0, -1, 13, 0]))
         array([ 8,  8,  0,  9, 10, 10,  0,  0, 13,  0])

.. function:: AU_balance(new_weights, perm_vec) -> numpy array

      :param new_weights: residual balance vector
      :type new_weights: numpy array
      :param perm_vec: permutation map
      :type perm_vec: dict
      :return: permuted residual balance vector
      :rtype: numpy array 

      .. code-block:: python

         >>> cdp.AU_balance(np.array([8, 9, 9, 0, 10, 9, 0, 0, 12, 0]), {2: 4, 0: 0, 1: 1, 3: 2, 4: 5, 5: 8})
         array([ 8,  9, 10,  9,  9, 12])

.. function:: reccom(j, r, n, I_res, weights, w_check = None, H = None) -> numpy array

      :param j: number of pools, iteration counter
      :type j: int
      :param r: address weight, i.e. to how many pools one item is added
      :type r: int
      :param n: number of items
      :type n: int
      :param I_res: residual index set
      :type I_res: list
      :param weights: residual balance vector
      :type weights: numpy array
      :param w_check: residual balance vector before adding next component
      :type w_check: numpy array
      :param H: matrix with addresses (arrangement)
      :type H: numpy array
      :return: the arrangement with new component added
      :rtype: numpy array

      .. code-block:: python

         >>> cdp.reccom(9, 3, 10, [0, 1, 2, 4, 5, 6, 7, 8], np.array([1, 2, 1, 2, 3, 3, 3, 3, 3, 0]), np.array([2, 1, 1, 2, 0, 0, 0, 0, 0, 0]), np.array([[0, 2, 3], [0, 1, 3], [0, 1, 9], [0, 2, 9], [2, 3, 9]]))
         array([[0, 1, 2], [1, 2, 5], [1, 4, 5], [0, 4, 5], [0, 2, 4], [0, 2, 3], [0, 1, 3], [0, 1, 9], [0, 2, 9], [2, 3, 9]])
       
.. function:: rcbba(m, r, n) -> list, list

      :param m: number of pools
      :type m: int
      :param r: address weight, i.e. to how many pools one item is added
      :type r: int
      :param n: number of items
      :type n: int
      :return:
         1) list with number of items in each pool, i.e. balance;
         2) list with address arrangement
      :rtype: list, list

      .. code-block:: python

         >>> cdp.reccom(9, 3, 10, [0, 1, 2, 4, 5, 6, 7, 8], np.array([1, 2, 1, 2, 3, 3, 3, 3, 3, 0]), np.array([2, 1, 1, 2, 0, 0, 0, 0, 0, 0]), np.array([[0, 2, 3], [0, 1, 3], [0, 1, 9], [0, 2, 9], [2, 3, 9]]))
         array([[0, 1, 2], [1, 2, 5], [1, 4, 5], [0, 4, 5], [0, 2, 4], [0, 2, 3], [0, 1, 3], [0, 1, 9], [0, 2, 9], [2, 3, 9]])

.. _test-section:

Tests
-----

.. function:: check_unique(lists) -> Boolean, Boolean

      :param lists: an arrangement for the test
      :type lists: list of lists
      :return:
         1) are addresses unique (True)
         2) are unions unique (True)
      :rtype: Boolean, Boolean

      .. code-block:: python

         >>> b, H = cdp.rcbba(10, 5, 100)
         >>> cdp.check_unique(H)
         (True, True)