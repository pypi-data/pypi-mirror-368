
codePUB
=======


codePUB package constructs balanced constant-weight Gray codes for detecting consecutive positives (DCP-CWGCs) for the efficient construction of combinatorial pooling schemes.

Task
----

To minimize complexity and reduce costs of the high-throughput experiments, combinatorial pooling strategies have been developed. Such experiments use an encoding scheme where items are mixed across multiple pools, with each pool containing multiple items. Measurements are performed at the pool level, producing a unique pattern of signals for each item, which is then decoded to determine individual item measurements. With fewer pools than items, this approach improves efficiency compared to individual testing. Carefully designed encoding/decoding schemes can also detect errors, leveraging the presence of items in multiple pools.

.. image:: comb_p_p.png
   :alt: Visual representation of combinatorial pooling
   :align: center
   :width: 80%


Balanced Constant-Weight Gray Codes
-----------------------------------

We introduce **balanced constant-weight Gray codes for detecting consecutive positives (DCP-CWGCs)** as a novel combinatorial pooling strategy. Items are assigned to pools using a sequence of binary vectors (binary addresses). Addresses have constant Hamming weight, adjacent addresses differ by a Hamming distance of 2, and their OR-sums are unique. These properties enable error detection, ensure constant testing for individual items and consecutive item pairs, and maintain stable detection by balancing the number of items per pool.

To construct balanced DCP-CWGCs with adjustable parameters, we developed a **branch-and-bound algorithm (BBA)**. This algorithm efficiently constructs DCP-CWGCs with a near-optimal balance for short to moderate code lengths (e.g., up to 3,000 items in under 250 seconds). It uses a depth-first heuristic to search for a Hamiltonian path in a bipartite graph formed by item addresses and their unions. To extend applicability and speed, an enhanced recursive branch-and-bound algorithm (**rcBBA**) constructs long codes by combining shorter, BBA-generated ones. Both methods are implemented in **codePub**.

Definition of DCP-CWGCs
-----------------------

A DCP-CWGC, denoted as :math:`(m, r, n)`, is a sequence of :math:`n` distinct binary addresses, :math:`C = \{a_1, a_2, \dots, a_n\}`, where each address :math:`a_j = (a_{j,1}, a_{j,2}, \dots, a_{j,m})` satisfies the following constraints:

1. **Distinct OR-sums**:
   For all :math:`j, k \in \{1, 2, \dots, n-1\}` and :math:`j \neq k`, the bitwise OR (denoted :math:`\vee`) of consecutive addresses must be distinct:

   .. math::
      a_j \vee a_{j+1} \neq a_k \vee a_{k+1}

2. **Constant weight**:
   For all :math:`j \in \{1, 2, \dots, n\}`:

   .. math::
      \sum_{i=1}^m a_{j,i} = r.

3. **Adjacent distance**:
   For all :math:`j \in \{1, 2, \dots, n-1\}`:

   .. math::
      D_H(a_j, a_{j+1}) = 2,

   where :math:`D_H` represents the Hamming distance.

Mapping and Constraints
-----------------------

This design maps directly to a pooling arrangement with :math:`m` pools, weight :math:`r`, and :math:`n` items. 

- Constraint (1) ensures unique identification of consecutive item pairs. 
- Constraint (2) ensures consistent testing for each item. 
- Together, constraints (2) and (3) maintain a constant OR-sum weight (:math:`r+1`) for consecutive addresses, resulting in consistent testing for consecutive item pairs.

Consequently, the scheme can detect single or consecutive positives and identify at least one error using the count of positive pools.

BBA and rcBBA
-------------

The details on both algorithms are described in our `preprint <https://arxiv.org/abs/2502.08214>`_ : **"Unbiased and Error-Detecting Combinatorial Pooling Experiments with Balanced Constant-Weight Gray Codes for Consecutive Positives Detection"**.