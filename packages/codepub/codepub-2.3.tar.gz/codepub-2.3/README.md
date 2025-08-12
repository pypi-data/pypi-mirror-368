<span style="color:white"> </span>
## <span style="color:#015396">CodePUB</span>

CodePUB (Code: precise, unique, balanced) is a Python tool developed for construction of balanced constant-weight Gray
codes for detecting consecutive positives (DCP-CWGCs) for the
efficient construction of combinatorial pooling schemes.

# Cite as

# Requirements

- numpy >= 1.23.5
	```python
	    pip install "numpy>=1.23.5"
	```

# How to use

Please read documentation for the package at [codepub.readthedocs](https://codepub.readthedocs.io/en/latest/).

# Description

To minimize complexity and reduce costs of high-throughput experiments, combinatorial pooling strategies have been developed. These experiments use an encoding scheme where items are mixed across multiple pools, with each pool containing multiple items. Measurements are performed at the pool level, producing a unique pattern of signals for each item, which is then decoded to determine individual item measurements. With fewer pools than items, this approach improves efficiency compared to individual testing. Carefully designed encoding/decoding schemes can also detect errors, leveraging the presence of items in multiple pools.

![Combinatorial Pooling Illustration](comb_p_p.png)

---

## Balanced Constant-Weight Gray Codes

We introduce **balanced constant-weight Gray codes for detecting consecutive positives (DCP-CWGCs)** as a novel combinatorial pooling strategy. Items are assigned to pools using a sequence of binary vectors (binary addresses). Addresses have constant Hamming weight, adjacent addresses differ by a Hamming distance of 2, and their OR-sums are unique. These properties enable error detection, ensure constant testing for individual items and consecutive item pairs, and maintain stable detection by balancing the number of items per pool.

To construct balanced DCP-CWGCs with adjustable parameters, we developed a **branch-and-bound algorithm (BBA)**. This algorithm efficiently constructs DCP-CWGCs with a near-optimal balance for short to moderate code lengths (e.g., up to 3,000 items in under 250 seconds). It uses a depth-first heuristic to search for a Hamiltonian path in a bipartite graph formed by item addresses and their unions. To extend applicability and speed, an enhanced recursive branch-and-bound algorithm (**rcBBA**) constructs long codes by combining shorter, BBA-generated ones. Both methods are implemented in **codePub**.

---

## Definition of DCP-CWGCs

A DCP-CWGC, denoted as `(m, r, n)`, is a sequence of `n` distinct binary addresses, `C = {a_1, a_2, ..., a_n}`, where each address `a_j = (a_{j,1}, a_{j,2}, ..., a_{j,m})` satisfies the following constraints:

1. **Distinct OR-sums**:  
   For all `j, k ∈ {1, 2, ..., n-1}` and `j ≠ k`:

   `a_j ∨ a_{j+1} ≠ a_k ∨ a_{k+1}`

   where `∨` is the bitwise OR operation.

2. **Constant weight**:  
   For all `j ∈ {1, 2, ..., n}`:

   `∑{i=1}^m a{j,i} = r`

3. **Adjacent distance**:  
   For all `j ∈ {1, 2, ..., n-1}`:

   `D_H(a_j, a_{j+1}) = 2`

   where `D_H` represents the Hamming distance.

---

## Mapping and Constraints

This design maps directly to a pooling arrangement with \( m \) pools, weight \( r \), and \( n \) items.

- **Constraint (1)** ensures unique identification of consecutive item pairs.
- **Constraint (2)** ensures consistent testing for each item.
- Together, **Constraints (2) and (3)** maintain a constant OR-sum weight (\( r+1 \)) for consecutive addresses, resulting in consistent testing for consecutive item pairs.

Consequently, the scheme can detect single or consecutive positives and identify at least one error using the count of positive pools.

---

## BBA and rcBBA

The details on both algorithms are described in our preprint: **"Unbiased and Error-Detecting Combinatorial Pooling Experiments with Balanced Constant-Weight Gray Codes for Consecutive Positives Detection"**.


# Authors


| Authors     | Guanchen He, Qin Huang                                 |
| ----------- | ------------------------------------------------------ |
| Affiliation | Beihang University                                     |
| ----------- | ------------------------------------------------------ |
| Authors     | Vasilisa Kovaleva, Hannah Meyer                        |
| ----------- | ------------------------------------------------------ |
| Affiliation | Cold Spring Harbor Laboratory                          |
| ----------- | ------------------------------------------------------ |
| Authors     | Mikhail Pogorelyy, Paul Thomas                         |
| ----------- | ------------------------------------------------------ |
| Affiliation | St. Jude Research Hospital                             |
| ----------- | ------------------------------------------------------ |
| Authors     | Carl Barton                                            |
| ----------- | ------------------------------------------------------ |
| Affiliation | Birkbeck, University of London                         |
| Date        | 09/02/2024                                             |