#!/usr/bin/env python
# coding: utf-8

import os
# Get the path of the current module
current_module_path = os.path.dirname(__file__)
# Define the path to your data directory
data_directory = os.path.join(current_module_path, 'data')

import numpy as np
import math
from itertools import combinations
import cvxpy as cp
import random
import sys
from fnmatch import fnmatch


# # Functions for ITERS search

def factorial(num):

    """
    Returns factorial of the number.
    Used in function(combination).
    """

    if num == 0:
        return 1
    else:
        return num * factorial(num-1)

def combination(n, k):

    """
    Returns number of possible combinations.
    Is dependent on function(factorial)
    Used in function(find_possible_k_values).
    """

    return factorial(n) // (factorial(k) * factorial(n - k))

def find_possible_k_values(n, l):

    """
    Returns possible iters given number of peptides (l) and number of pools (n).
    Is dependent on function(combination).
    """

    k_values = []
    k = 0
    
    while k <= n:
        c = combination(n, k)
        if c >= l:
            break
        k += 1

    while k <= n:
        if combination(n, k) >= l:
            k_values.append(k)
        else:
            break
        k += 1

    return k_values


# # Gray codes functions


def find_q_r(n):
    
    """
    Solves an equation: what is an equal for partition for 2**n:
    2**n = n*q + r
    What is n?
    Used in function(bgc).
    """

    q = cp.Variable(integer=True)
    r = cp.Variable(integer=True)

    constraints = [
        2**n == n*q + r,
        r >= 0,
        r <= n-1
    ]

    problem = cp.Problem(cp.Minimize(r), constraints)

    problem.solve()
    
    if problem.status == 'optimal':
        return int(q.value), int(r.value)
    
def bgc(n, s = None):
    
    """
    Balanced Gray codes construction.
    Takes a transition sequence for a balanced Gray code with n-2 bits,
    returns a transition sequence of n-bit BGC.
    Is dependent on function(find_q_r).
    Used in function(n_bgc)
    """

    ### Calculation of q, r
    q, r = find_q_r(n=n)

    ### Partition p_i
    p_i = []

    if q%2 == 0:
        q_def = int(r/2)
        if q_def != 0:
            Q = list(range(1, n-1))[-q_def:]
        else:
            Q = []
    
        for i in range(n):
            if i in Q:
                p_i.append(q+2)
            else:
                p_i.append(q)
    elif q%2 != 0:
        q_def = int((n+r)/2)
        if q_def != 0:
            Q = list(range(1, n-1))[-q_def:]
        else:
            Q = []
    
        for i in range(n):
            if i in Q:
                p_i.append(q+1)
            else:
                p_i.append(q-1)
            
    p_i = sorted(p_i)

    ### Calculation b_i
    if s is None:
        if n == 4:
            s = [1, 2, 1, 2]
        elif n == 5:
            s = [1, 2, 3, 2, 1, 2, 3, 2]
    b_i = []

    for i in range(1, len(set(s))+1):
        if i != s[len(s)-1]:
            b = (4*s.count(i) - p_i[i-1])/2
            b_i.append(int(b))
        else:
            b = (4*(s.count(i) - 1) - p_i[i-1])/2
            b_i.append(int(b))
    l = sum(b_i)

    counts = dict()
    for i in range(len(b_i)):
        counts[i+1] = b_i[i]
    
    s = s[:-1]
    u = []
    t = []
    new_counts = dict()
    for i in range(1, n-1):
        new_counts[i] = 0
    for i in s:
        if new_counts[i] >= counts[i]:
            u[-1].append(i)
        else:
            t.append([i])
            u.append([])
        new_counts[i] += 1
    n = n-2

    s_2 = []

    for t_i, u_i in zip(t, u):
        s_2 = s_2 + t_i + u_i
    s_2 = s_2 + [n+1]

    row_count = 0
    for i in range(len(u)-1, -1, -1):
        if row_count == 0:
            s_2 = s_2 + list(reversed(u[i])) + [n+2] + u[i] + [n+1] + list(reversed(u[i])) + t[i]
            row_count = 1
        else:
            s_2 = s_2 + list(reversed(u[i])) + [n+1] + u[i] + [n+2] + list(reversed(u[i])) + t[i]
            row_count = 0
    if row_count == 0:
        s_2 = s_2 + [n+2] + [n+1] + [n+2]
    elif row_count == 1:
        s_2 = s_2 + [n+1] + [n+2] + [n+1]

    return s_2

def n_bgc(n):
    
    """
    Takes n and returns n-bit BGC.
    Is dependent on function(bgc).
    Used in function(m_length_BGC).
    """
    
    if n == 2:
        s_2 = [1, 2, 1, 2]
        counter = 2
    elif n == 3:
        s_2 = [1, 2, 3, 2, 1, 2, 3, 2]
        counter = 3
    elif n >3 and n%2 == 0:
        counter = 4
        s_2 = bgc(n=counter)
    elif n > 3 and n%2 != 0:
        counter = 5
        s_2 = bgc(n=counter)
    while counter != n:
        counter = counter + 2
        s_2 = bgc(n=counter, s = s_2)
        
    balance = []
    for item in set(s_2):
        balance.append(s_2.count(item))
        
    #print(balance)
    return s_2

def computing_ab_i_odd(s_2, l, v):
    
    """
    Used in special case of n-bit BGC construction with flexible length.
    Used in function(m_length_BGC).
    """
    
    ## How many values we need to add before s_r
    E_v = int(np.floor((v-1)/3))
    E_v = s_2[:E_v]
        
    ## Computing b_i
    b_i = dict()
    for i in range(n):
        b_i[i] = 0
        if i in E_v:
            b_i[i] = E_v.count(i)
            
    inequalities = []
    TC = dict()

    ## How many a_i we need to compute:
    a_i = []
    for i in range(n):
        a_i.append(cp.Variable(integer=True))

    for i in range(n+2):
        if l%2 == 0:
            if i == n:
                TC_i = l - cp.floor(v/3) + cp.ceil(((v+4)%6)/6)
            elif i == n+1:
                TC_i = l - cp.floor(v/3) + cp.ceil(((v+1)%6)/6)
            elif i == s_2[-1]:
                TC_i = 3*(s_2.count(i)-1) - 2*a_i[i] + b_i[i]
            else:
                TC_i = 3*s_2.count(i) - 2*a_i[i] + b_i[i]
            TC[i] = TC_i
        else:
            if i == n:
                TC_i = l - cp.floor(v/3) + cp.ceil(((v+1)%6)/6)
            elif i == n+1:
                TC_i = l - cp.floor(v/3) + cp.ceil(((v+4)%6)/6)
            elif i == s_2[-1]:
                TC_i = 3*(s_2.count(i)-1) - 2*a_i[i] + b_i[i]
            else:
                TC_i = 3*s_2.count(i) - 2*a_i[i] + b_i[i]
            TC[i] = TC_i
                
    ## Solving the resulting inequalities for a_i
    inequalities = []
    for key1 in TC.keys():
        for key2 in TC.keys():
            if key1 != key2:
                inequalities.append(-2 <= TC[key1] - TC[key2])
                inequalities.append(TC[key1] - TC[key2] <= 2)
    inequalities.append(sum(a_i) == l)
    for i in range(len(a_i)):
        inequalities.append(a_i[i] >= 0)
        inequalities.append(a_i[i] <= l)

    a_values = dict()
    problem = cp.Problem(cp.Minimize(0), inequalities)
    problem.solve()

    if problem.status == 'optimal':
        for i in range(len(a_i)):
            a_values[i] = int(a_i[i].value)
    
    return [v, a_values, E_v]

### Ready for both cases
def m_length_BGC(m, n):
    
    """
    Construction of n-bit BGC with flexible length from n-2 bit BGC.
    Is dependent on function(computing_ab_i_odd) and function(n_bgc).
    """
    
    n = n-2
    s_2 = n_bgc(n = n)
    s_2 = [x - 1 for x in s_2]
    
    ### if 3*2**n < m < 2**(n+2) (Case I)
    if 3*2**n < m < 2**(n+2):
        intervals = [np.floor(m/(n+2)) -3, np.floor(m/(n+2))]
    
        ## l is chosen from intervals
        l_options = dict()
        for l in list(range(int(intervals[0]), int(intervals[1]) + 1)):
            ## How many values we need to add before s_r
            u = m - 3*2**n
            if l%2 == 0:
                E_u = s_2[-l:][:-1]
            elif l%2 != 0:
                E_u = s_2[-l-1:][:-1]
        
            ## Computing b_i
            b_i = dict()
            for i in range(n):
                b_i[i] = 0
                if i in E_u:
                    b_i[i] = E_u.count(i)

            inequalities = []
            TC = dict()

            ## How many a_i we need to compute:
            a_i = []
            for i in range(n):
                a_i.append(cp.Variable(integer=True))

            for i in range(n+2):
                if l%2 == 0:
                    if i == n:
                        TC_i = l + 2
                    elif i == n+1:
                        TC_i = l + 2
                    elif i == s_2[-1]:
                        TC_i = 3*(s_2.count(i)-1) - 2*a_i[i] + b_i[i]
                    else:
                        TC_i = 3*s_2.count(i) - 2*a_i[i] + b_i[i]
                    TC[i] = TC_i
                else:
                    if i == n:
                        TC_i = l + 2
                    elif i == n+1:
                        TC_i = l + 1
                    elif i == s_2[-1]:
                        TC_i = 3*(s_2.count(i)-1) - 2*a_i[i] + b_i[i]
                    else:
                        TC_i = 3*s_2.count(i) - 2*a_i[i] + b_i[i]
                    TC[i] = TC_i
                
            ## Solving the resulting inequalities for a_i
            inequalities = []
            for key1 in TC.keys():
                for key2 in TC.keys():
                    if key1 != key2:
                        inequalities.append(-2 <= TC[key1] - TC[key2])
                        inequalities.append(TC[key1] - TC[key2] <= 2)
            for i in range(len(a_i)):
                inequalities.append(a_i[i] >= 0)
                inequalities.append(a_i[i] <= l)
            inequalities.append(sum(a_i) == l)

            a_values = dict()
            problem = cp.Problem(cp.Minimize(0), inequalities)
            problem.solve()

            if problem.status == 'optimal':
                for i in range(len(a_i)):
                    a_values[i] = int(a_i[i].value)
                break
            l_options[l] = [u, a_values]
                    
        s_2 = s_2[:-1]
        u = []
        t = []
        new_counts = dict()
        for i in range(0, n):
            new_counts[i] = 0
        for i in s_2:
            if new_counts[i] >= a_values[i]:
                u[-1].append(i)
            else:
                t.append([i])
                u.append([])
            new_counts[i] += 1
    
        flex_s = []
        if l%2 == 0:
            flex_s = flex_s + E_u + [n]
            row_count = 0
            for i in range(l-1, -1, -1):
                if row_count == 0:
                    flex_s = flex_s + list(reversed(u[i])) + [n+1] + u[i] + [n] + list(reversed(u[i])) + t[i]
                    row_count = 1
                elif row_count == 1:
                    flex_s = flex_s + list(reversed(u[i])) + [n] + u[i] + [n+1] + list(reversed(u[i])) + t[i]
                    row_count = 0
            flex_s = flex_s + [n+1] + [n] + [n+1]
    
        elif l%2 != 0:
            flex_s = flex_s + E_u + [n]
            row_count = 0
            for i in range(l-1, -1, -1):
                if row_count == 0:
                    flex_s = flex_s + list(reversed(u[i])) + [n+1] + u[i] + [n] + list(reversed(u[i])) + t[i]
                    row_count = 1
                elif row_count == 1:
                    flex_s = flex_s + list(reversed(u[i])) + [n] + u[i] + [n+1] + list(reversed(u[i])) + t[i]
                    row_count = 0
            flex_s = flex_s + [n] + [n+1] + [n]
    
            
        balance = []
        for item in set(flex_s):
            balance.append(flex_s.count(item))
        #print(balance)
    
        return flex_s
    
    ### if 2**(n+1) < m <= 3*(2**n) (Case II)
    if 2**(n+1) < m <= 3*(2**n):
        v = 3*(2**n)-m
        intervals = [np.floor(m/(n+2)) + np.floor(v/3) -2, np.floor(m/(n+2)) + np.floor(v/3) +2]
    
        ## Possible l's and v's:
        l_options = dict()
    
        ## l is chosen from intervals
        for l in list(range(int(intervals[0]), int(intervals[1]) + 1)):
            l_options[l] = computing_ab_i_odd(s_2 = s_2, l = l, v = v)
            
            if l_options[l][1] != {}:
                v = l_options[l][0]
                if v > 1:
                    el = int(np.floor((v+1)/3))
                    t = s_2[:el]
                    a_i = l_options[l][1]
                    verdict = []
                    for item in a_i.keys():
                        if a_i[item] != t.count(item):
                            verdict.append('No')
                        else:
                            verdict.append('True')
                    if a_i == {}:
                        verdict.append('No')
                        
                    if 'No' not in verdict:
                        u = []
                        t = []
                        new_counts = dict()
                        for i in range(0, n):
                            new_counts[i] = 0
                        for i in s_2:
                            if new_counts[i] >= a_values[i]:
                                u[-1].append(i)
                            else:
                                t.append([i])
                                u.append([])
                            new_counts[i] += 1
                        
                        flex_s = []
                        if l%2 == 0:
                            row_count = 0
                            for i in range(l-1, -1, -1):
                                if row_count == 0:
                                    flex_s = flex_s + list(reversed(u[i])) + [n+1] + u[i] + [n] + list(reversed(u[i])) + t[i]
                                    row_count = 1
                                elif row_count == 1:
                                    flex_s = flex_s + list(reversed(u[i])) + [n] + u[i] + [n+1] + list(reversed(u[i])) + t[i]
                                    row_count = 0
                                    flex_s = flex_s + [n+1] + [n] + [n+1]
    
                        elif l%2 != 0:
                            row_count = 0
                            for i in range(l-1, -1, -1):
                                if row_count == 0:
                                    flex_s = flex_s + list(reversed(u[i])) + [n+1] + u[i] + [n] + list(reversed(u[i])) + t[i]
                                    row_count = 1
                                elif row_count == 1:
                                    flex_s = flex_s + list(reversed(u[i])) + [n] + u[i] + [n+1] + list(reversed(u[i])) + t[i]
                                    row_count = 0
                                    flex_s = flex_s + [n] + [n+1] + [n]
                        flex_s = flex_s[:-v] 
                        balance = []
                        for item in set(flex_s):
                            balance.append(flex_s.count(item))
                        #print(balance)
                        return flex_s
                    
                    elif 'No' in verdict:
                        new_options = dict()
                        new_s = s_2[1:] + [s_2[0]]
                        new_options[l] = computing_ab_i_odd(s_2 = new_s, l = l, v = v)
                        v = new_options[l][0]
                        if v > 1:
                            el = int(np.floor((v+1)/3))
                            t = new_s[:el]
                            a_i = new_options[l][1]
                            verdict = []
                            for item in a_i.keys():
                                if a_i[item] != t.count(item):
                                    verdict.append('No')
                                else:
                                    verdict.append('True')
                            if a_i == {}:
                                verdict.append('No')
                        
                            if 'No' not in verdict:
                                
                                u = []
                                t = []
                                new_counts = dict()
                                for i in range(0, n):
                                    new_counts[i] = 0
                                for i in s_2:
                                    if new_counts[i] >= a_values[i]:
                                        u[-1].append(i)
                                    else:
                                        t.append([i])
                                        u.append([])
                                    new_counts[i] += 1
                                
                                flex_s = []
                                if l%2 == 0:
                                    row_count = 0
                                    for i in range(l-1, -1, -1):
                                        if row_count == 0:
                                            flex_s = flex_s + list(reversed(u[i])) + [n+1] + u[i] + [n] + list(reversed(u[i])) + t[i]
                                            row_count = 1
                                        elif row_count == 1:
                                            flex_s = flex_s + list(reversed(u[i])) + [n] + u[i] + [n+1] + list(reversed(u[i])) + t[i]
                                            row_count = 0
                                            flex_s = flex_s + [n+1] + [n] + [n+1]
    
                                elif l%2 != 0:
                                    row_count = 0
                                    for i in range(l-1, -1, -1):
                                        if row_count == 0:
                                            flex_s = flex_s + list(reversed(u[i])) + [n+1] + u[i] + [n] + list(reversed(u[i])) + t[i]
                                            row_count = 1
                                        elif row_count == 1:
                                            flex_s = flex_s + list(reversed(u[i])) + [n] + u[i] + [n+1] + list(reversed(u[i])) + t[i]
                                            row_count = 0
                                            flex_s = flex_s + [n] + [n+1] + [n]
                                flex_s = flex_s[:-v]
                                balance = []
                                for item in set(flex_s):
                                    balance.append(flex_s.count(item))
                                #print(balance)
                                return flex_s
                            
                            
def gc_to_address(s_2, iters, n):
    
    """
    Takes BGC transition sequence and returns BGC with particular number of 1 (iters).
    Returns list of addresses.
    """
    
    codes = [['0']*n]
    for item in s_2:
        n_item = codes[-1].copy()
        if n_item[item-1] == '0':
            n_item[item-1] = '1'
        else:
            n_item[item-1] = '0'
        codes.append(n_item)
    addresses = []
    for item in codes:
        if item.count('1') == iters:
            ad = []
            for i in range(len(item)):
                if item[i] == '1':
                    ad.append(i)
            if ad not in addresses:
                addresses.append(ad)
    return addresses


# # Hamiltonian path functions


def union_address(address, union, nums = None):
    
    """
    For AU-hamiltonian path search.
    Takes an address, a union, and a list of index options, returns possible unions.
    Used in function(hamiltonian_path_AU), function(bAU_search).
    """
    
    one_bits = []
    zero_bits = []
    for i in range(len(address)):
        if address[i] == '1' and union[i] == '1':
            one_bits.append(i)
        elif address[i] == '0' and union[i] == '0':
            zero_bits.append(i)
    unions = []
    string = ['0']*len(union)
    if nums is None:
        nums = list(range(len(union)))
            
    for one_bit in one_bits:
        string[one_bit] = '1'
    for zero_bit in zero_bits:
        if zero_bit in nums:
            new_bit = string.copy()
            new_bit[zero_bit] = '1'
            unions.append(''.join(new_bit))
    return unions

def address_union(address, union, nums = None):
    
    """
    For AU-hamiltonian path search.
    Takes an address, a union, and a list of index options, returns possible addresses.
    Used in function(hamiltonian_path_AU), function(bAU_search).
    """
    
    one_bits = []
    for i in range(len(address)):
        if address[i] == '0' and union[i] == '1':
            zero_bit = i
        elif address[i] == '1' and union[i] == '1':
            one_bits.append(i)

    if nums is not None:
        if zero_bit not in nums:
            return []
    else:
        nums = list(range(len(address)))
        
    addresses = []
    string = ['0']*len(address)
    string[zero_bit] = '1'
    comb_len = len(one_bits)-1
    one_bits = [item for item in one_bits if item in nums]
    one_combs = list(combinations(one_bits, comb_len))
    for one_comb in one_combs:
        new_bit = string.copy()
        for one_bit in one_comb:
            new_bit[one_bit] = '1'
        addresses.append(''.join(new_bit))
    return addresses

def hamiltonian_path_AU(size, point, t, unions=None, path=None, balance=None):
    
    """
    AU-hamiltonian path search.
    Is dependent on function(union_address), function(address_union), function(variance_score), function(sum_bits).
    Used in function(bba_au).
    """
    
    if path is None:
        path = []
    if unions is None:
        unions = []
    
    if t == 'a':
        if point not in set(path):
            path.append(point)
            if len(path) == size:
                return path
            next_points = union_address(address=path[-1], union=unions[-1] if unions else None)
            next_points.sort(key=lambda s: (variance_score(sum_bits(path), s, balance), random.random()))
            for nxt in next_points:
                res_path = hamiltonian_path_AU(size, nxt, 'u', unions, path, balance)
                if res_path:
                    return res_path
            path.remove(point)
        else:
            return None
        
    elif t == 'u':
        if point not in set(unions):
            unions.append(point)
            next_points = address_union(address=path[-1], union=unions[-1] if unions else None)
            next_points.sort(key=lambda s: (variance_score(sum_bits(path), s, balance), random.random()))
            for nxt in next_points:
                res_path = hamiltonian_path_AU(size, nxt, 'a', unions, path, balance)
                if res_path:
                    return res_path   
            unions.remove(point)
        else:
            return None
    return None

def variance_score(bit_sums, s, balance = None):
    
    """
    For both versions of Hamiltonian path search.
    Takes an address (or union), measures how it influences the balance in path is being added.
    Returns penalty: difference between variance of balance before and after or between required balance and after.
    Is dependent on function(bit_sums).
    Used in function(bba_au), function(bba_a)
    """
    
    if balance is None:
        variance = np.var(bit_sums)

    new_bit_sums = bit_sums[:]
    for i, bit in enumerate(s):
        new_bit_sums[i] += int(bit)

    if balance is None:
        new_variance = np.var(new_bit_sums)
        penalty = new_variance - variance
    else:
        diff = np.array(balance) - np.array(new_bit_sums)
        penalty = np.var(diff)

    return penalty

def return_address_message(code, mode):
    
    """
    For A-hamiltonian path search.
    Takes an address and returns message (0/1 string).
    Or takes a message and returns an address.
    Used in function(binary_union), function(bAU_search).
    """
    
    if mode == 'a':
        address = []
        for i in range(len(code)):
            if code[i] == '1':
                address.append(i)
        return address
    if mode[0] == 'm':
        n = int(mode[1:])
        message = ''
        for i in range(n):
            if i in code:
                message = message + '1'
            else:
                message = message + '0'
        return message
    
def binary_union(bin_list):
    
    """
    For A-hamiltonian path search.
    Takes list of addresses, returns list of their unions.
    Is dependent on function(return_address_message).
    Used in function(hamiltonian_path_A).
    """
    
    union_list = []
    for i in range(len(bin_list)-1):
        
        set1 = set(return_address_message(bin_list[i], mode = 'a'))
        set2 = set(return_address_message(bin_list[i+1], mode = 'a'))
        set_union = set1.union(set2)
        union = return_address_message(set_union, mode = 'm'+str(len(bin_list[i])))
        union_list.append(union)
    
    return union_list

def hamming_distance(s1, s2):
    
    """
    For A-hamiltonian path search.
    Takes two messages (0/1 string) and returns their Hamming distance.
    Used in function(bba_a).
    """
    
    return sum(el1 != el2 for el1, el2 in zip(s1, s2))

def sum_bits(arr):
    
    """
    For both versions of hamiltonian path search.
    Takes list of addresses and returns their balance.
    Used in function(bba_a), function(bba_au),
    function(hamiltonian_path_A), function(hamiltonian_path_AU).
    """
    
    bit_sums = [0]*len(arr[0])

    for s in arr:
        for i, bit in enumerate(s):
            bit_sums[i] += int(bit)
    return bit_sums

def hamiltonian_path_A(G, size, pt, path=None):
    
    """
    A-hamiltonian path search.
    Is dependent on function(binary_union), function(variance_score), function(sum_bits).
    Used in function(bba_a).
    """

    if path is None:
        path = []
    if (pt not in set(path)) and (len(binary_union(path+[pt]))==len(set(binary_union(path+[pt])))):
        path.append(pt)
        if len(path)==size:
            return path
        next_points = G.get(pt, [])
        next_points.sort(key=lambda s: (variance_score(sum_bits(path), s), random.random()))
        for pt_next in next_points:
            res_path = hamiltonian_path_A(G, size, pt_next, path)
            if res_path:
                return res_path
        path.remove(pt)
    return None

def starts(n_pools, iters, start = None):

    """
    For AU-hamiltonian path search.
    Takes number of pools, number of pools per peptide, and (optionally) first address,
    returns a dictionary with possible first addresses and unions.
    Used in function(bba_au).
    """

    starts = dict()
    positions = range(n_pools)
    for ones_positions in combinations(positions, iters):
        ad = ['0'] * n_pools
        for pos in ones_positions:
            ad[pos] = '1'
        start_a = ''.join(ad)
        zeros = [x for x in range(n_pools) if x not in ones_positions]
        start_u = []
        for zero in zeros:
            u = ''.join(['1' if i == zero else char for i, char in enumerate(start_a)])
            start_u.append(u)
        starts[start_a] = start_u
    if start is None:
        return starts
    else:
        return {start: starts[start]}

def bba_au(n_pools, iters, len_lst, start_a = None, balance = None):
    
    """
    For AU-hamiltonian path search.
    Takes number of pools, number of pools per peptide, length of the path, (optionally) starting address and required balance.
    Returns balance of the path and list of addresses.
    Is dependent on function(hamiltonian_path_AU), function(sum_bits), and function(starts).
    Used in function(reccom), function(gen_elementary_sequence).
    """

    if math.comb(n_pools, iters) <= len_lst or math.comb(n_pools, iters+1) <= len_lst:
        return [None, None]

    depth = len_lst*2+500
    sys.setrecursionlimit(depth)

    ## First address and first union
    if start_a is None:
        starting = starts(n_pools, iters)
    else:
        starting = starts(n_pools, iters, start_a)
    arrangement = False

    for start_a in starting.keys():
        path = [start_a]
        if len(path) != len_lst:
            for start_u in starting[start_a]:
                arrangement = hamiltonian_path_AU(size=len_lst, point = start_u, t = 'u', unions = None, path = [start_a], balance=balance)
                if arrangement:
                    break
            if arrangement:
                break
        else:
            arrangement = path
            break

    if arrangement:
        addresses = []
        for item in arrangement:
            address = []
            for i in range(len(item)):
                if item[i] == '1':
                    address.append(i)
            addresses.append(address)
        #print(sum_bits(arrangement))
        return sum_bits(arrangement), addresses
    return [None, None]

def bba_a(n_pools, iters, len_lst):
    
    """
    For A-hamiltonian path search.
    Takes number of pools, iters, and length of the path.
    Returns balance of the path and list of addresses.
    Is dependent on function(hamiltonian_path_A) and function(sum_bits).
    """
    
    if math.comb(n_pools, iters) <= len_lst or math.comb(n_pools, iters+1) <= len_lst:
        return [None, None]

    depth = len_lst*2+500
    sys.setrecursionlimit(depth)

    vertices = []
    for combo in combinations(range(n_pools), iters):
        v = ['0']*n_pools
        for i in combo:
            v[i] = '1'
        vertices.append(''.join(v))
        
    G = {v: [] for v in vertices}
    for v1 in vertices:
        for v2 in vertices:
            if hamming_distance(v1, v2) == 2:
                G[v1].append(v2)
            
    arrangement = hamiltonian_path_A(G, len_lst, vertices[0])
    
    addresses = []
    if arrangement:
        for item in arrangement:
            address = []
            for i in range(len(item)):
                if item[i] == '1':
                    address.append(i)
            addresses.append(address)
        return sum_bits(arrangement), addresses
    else:
        return [None, None]

# # RCA

def item_per_pool(addresses, n):
    
    """
    For RCA and RCA_AU path search.
    Takes matrix of addresses and number of pools.
    Returns the balance.
    Used in function(rca), function(reccom), function(rcau).
    """

    balance = [0]*n
    for line in addresses:
        for i in line:
            balance[i]+=1
    return np.array(balance)


def find_path(n, X, directory):

    """
    For RCA path search.
    Takes number of pools, pool per item and the directory of the elementary sequences.
    Returns the path to the elementary short sequence.
    Used in function(rca).
    """

    fileList = [f for f in os.listdir(directory) if fnmatch(f,f'{n}n_{X}X*.txt')]
    l = len(fileList)
    filepath = os.path.join(directory, fileList[l - 1])
    return filepath


def list_union(address_matrix):
    
    """
    For RCA and RCA_AU path search.
    Takes matrix of addresses, returns the union matrix.
    Used in function(bAU_search), function(isGrayUnionDisjoint).
    """
    
    address_matrix = address_matrix.tolist()
    union_matrix = []
    for i in range(len(address_matrix)-1):
        union = list(set(address_matrix[i]+address_matrix[i+1]))
        union_matrix.append(union)
    return np.array(union_matrix)


def set_distance(set1, set2):
    
    """
    For RCA path search.
    Takes two address vectors and returns their Hamming distance.
    Used in function(isGrayUnionDisjoint).
    """
    
    a = np.setdiff1d(set1, set2)
    return a.size


def bAU_search(address_matrix, n_pools, nums):

    """
    For RCA and RCA_AU path search.
    Takes an address matrix, number of pools, and possible indices.
    Returns possible first addresses for an elementary sequence.
    Is dependent on function(return_address_message), function(list_union), function(union_address), function(address_union).
    Used in function(rca), function(reccom).
    """

    ad1 = return_address_message(list(address_matrix[0]), 'm'+str(n_pools))
    un1 = return_address_message(list(np.union1d(address_matrix[0], address_matrix[1])), 'm'+str(n_pools))
    union_matrix = list_union(address_matrix)
    b_unions = union_address(ad1, un1, nums)
    bs = np.empty((0, len(address_matrix[0])), dtype='int')
    
    for b_union in b_unions:
        union = return_address_message(b_union, 'a')
        if not any(np.array_equal(np.array(union), row) for row in union_matrix):
            addresses = address_union(ad1, b_union, nums)
            for address in addresses:
                address = return_address_message(address, 'a')
                if not any(np.array_equal(np.array(address), row) for row in address_matrix):
                    b = np.reshape(np.array(address), (1,len(address_matrix[0])))
                    bs=np.concatenate((bs,b), axis=0)
    return bs


def permutation_map(address_matrix, k, b, n, nums, p=-1):
    
    """
    For RCA_AU path search.
    Finds a permutation map such that the k-th address of
    address_matrix is mapped one-by-one to b, and n is mapped to p.
    Takes address_matrix, row index k, target address b,
    and set of indices from which b values are chosen.
    Returns the permuted matrix.
    Is dependent on fuction(rca), function(reccom).
    """
    
    r, iters = address_matrix.shape
    permuted_address_matrix=np.zeros((r,iters),dtype='int')

    a = address_matrix[k]
    perm_vec = dict()
    
    perm_vec[a[-1]] = b[p]

    a1 = np.setdiff1d(a, a[-1])
    b1 = np.setdiff1d(b, b[p])

    for l in range(len(a1)):
        perm_vec[a1[l]] = b1[l]

    map_row1 = np.setdiff1d(np.unique(address_matrix.flatten()), a)
    map_row2 = np.setdiff1d(nums, b)

    for l in range(len(map_row1)):
        perm_vec[map_row1[l]] = map_row2[l]

    for l in range(r):
        for j in range(iters):
            permuted_address_matrix[l, j] = perm_vec[address_matrix[l, j]]
        permuted_address_matrix[l] = np.sort(permuted_address_matrix[l])
    return permuted_address_matrix


def isGrayUnionDisjoint(S):

    """
    For RCA path search.
    Takes an address matrix, returns TRUE if it satisfies Hamming distance and union uniqueness constraints.
    Is used in function(rca).
    """
    r, _ = S.shape
    U=list_union(S)
    flag = True
    for i in range(r-1):
        if set_distance(S[i], S[i+1]) != 1:
            flag = False

    for i in range(r-2):
        for j in range(i+1,r-1):
            if sum(abs(U[i]-U[j])) == 0:
                flag = False

    return flag


def rca(n_pools, iters, len_lst):

    """
    RCA path search.
    Takes number of pools, number of pools per peptide, and the length of the sequence.
    Returns matrix of addresses.
    Utilizes pre-determined sequences in folder short_sequences_txt.
    Is dependent on function(bAU_search) and function(permutation_map), function(isGrayUnionDisjoint), function(find_path), function(item_per_pool).
    """

    ## if there are not enough addresses and unions
    if math.comb(n_pools, iters) <= len_lst or math.comb(n_pools, iters+1) <= len_lst:
        return [None, None]

    n_0 = [8,8,8,9,10,12,14,16]
    n0=n_0[iters-1]
    deviation_now=999

    w=math.floor(iters*len_lst/n_pools)
    weights0 = w * np.ones((n_pools,), dtype='int')
    delta = len_lst * iters - w * n_pools
    weights0[:delta] += 1  # Initialize items per pool vector

    weights = weights0
    n = n_pools

    filepath=find_path(n - 1, iters-1, data_directory)
    S1_0 = np.loadtxt(filepath, dtype='int')
    M1, _ = S1_0.shape  
    B = (n-1) * np.ones((M1, 1), dtype='int')
    S1_0 = np.concatenate([S1_0, B], axis=1)
    filepath=find_path(n - 2, iters-1, data_directory)
    S2_0 = np.loadtxt(filepath, dtype='int')
    M2, _ = S2_0.shape
    B = (n-2) * np.ones((M2, 1), dtype='int')
    S2_0 = np.concatenate([S2_0, B], axis=1)

    for ite1 in range(M1-w+1):
        # S_out = np.zeros((0,iters),dtype='int')
        S1 = S1_0[ite1:ite1+w]
        S_out = S1
        weights_n = item_per_pool(S1, len(weights0))
        weights = weights0 - weights_n
        nums = np.setdiff1d(np.arange(0, n_pools), n-1)
        nums0=nums
        S_out0 = S_out


        # ite = n-2 level traverse 
        bs = bAU_search(S_out, len(weights0), nums) 
        bs_diff = np.setdiff1d(bs, S_out[0, :]) 
        weights_selected=weights[bs_diff]
        row2 = np.argmax(weights_selected)
        b2 = bs[row2, :]
        w_is, p2 = np.sort(weights[b2]), np.argsort(weights[b2])
        pos2 = np.searchsorted(w_is, M2, side='right') - 1

        if pos2 == -1:
            pos2 = 0
            w2 = M2
        else:
            w2 = weights[b2[p2[pos2]]]

        weights1 = weights

        for ite2 in range(M2-w2+1):
            nums = nums0
            mat_level2 = permutation_map(S2_0, ite2+w2-1, b2, n - 1, nums, p2[pos2])
            S2 = mat_level2[ite2:ite2+w2]
            S_out = np.concatenate([S2, S_out0], axis=0)
            w_i_diff = item_per_pool(S2, n_pools)
            weights = weights1 - w_i_diff
            nums = np.setdiff1d(nums0, b2[p2[pos2]])


            # (n-i)-th level concatenation
            for i in range(n - 3, n0 - 1, -1):
                filepath=find_path(i, iters-1, data_directory)
                Si_0 = np.loadtxt(filepath, dtype='int')
                Mi, _ = Si_0.shape
                B = i * np.ones((Mi, 1), dtype='int')
                Si_0 = np.concatenate([Si_0, B], axis=1)
                bs = bAU_search(S_out, len(weights0), nums)
                r, _ = bs.shape
                if r == 0:
                    break

                # Find the maximum number in w_i(b) that is smaller than Mi
                bs_diff = np.setdiff1d(bs, S_out[0, :])
                p = np.argmax(weights[bs_diff])
                bi = bs[p, :]
                w_is, p = np.sort(weights[bi]), np.argsort(weights[bi])
                pos = np.searchsorted(w_is, Mi, side='right') - 1
                # if pos == -1:
                #     pos = 0
                #     wi = Mi
                # else:
                #     wi = weights[bi[p[pos]]]

                # Concatenate the (n-i)-th level subsequence
                if pos == -1:
                    Si = permutation_map(Si_0, Mi-1, bi, i+1, nums, p[-1])
                    S_out = np.concatenate([Si, S_out], axis=0)
                    # print(f"i={i}, M2<w_i(b(X)), does not clear w_i(b(X))")
                    w_i_diff = item_per_pool(Si, n)
                    weights = weights - w_i_diff
                    nums = np.setdiff1d(nums, bi[p[-1]])
                elif weights[bi[p[pos]]] > 0:
                    Si = permutation_map(Si_0, Mi-1, bi, i+1, nums, p[pos])
                    S_out = np.concatenate(
                        [Si[Mi - weights[bi[p[pos]]]:Mi, :], S_out], axis=0)
                    w_i_diff = item_per_pool(Si[Mi - weights[bi[p[pos]]]:Mi, :], n_pools)
                    weights = weights- w_i_diff
                    nums = np.setdiff1d(nums, bi[p[pos]])
                else:
                    nums = np.setdiff1d(nums,bi[p[0]])


            M_last = int(np.sum(weights) / iters)
            filepath=find_path(n0, iters, data_directory)
            S0_0 = np.loadtxt(filepath, dtype='int')
            M0, _ = S0_0.shape
            bs = bAU_search(S_out, len(weights0), nums)
            r, _ = bs.shape


            if r > 0:
                if M_last <= 0:
                    S_out = S_out[-len_lst:]
                elif M0 < M_last:
                    b = bs[0, :]
                    S0 = permutation_map(S0_0, M0-1, b, n0, nums)
                    S_out = np.concatenate([S0, S_out], axis=0)
                    w_i_diff = item_per_pool(S0, n_pools)
                    weights = weights - w_i_diff
                    print("M0<M_last, does not achieve length.")
                else:
                    deviation = 999
                    flag = False
                    for j in range(r):
                        b = bs[j, :]
                        for k in range(M0, M_last - 1, -1):
                            mat_last_0 = permutation_map(S0_0, k-1, b, n0, nums)
                            S0 = mat_last_0[k - M_last:k]
                            w_i_diff = item_per_pool(S0, n)
                            w_i_verify = weights - w_i_diff
                            deviation_k = np.max(w_i_verify) - np.min(w_i_verify)
                            if deviation_k < deviation:
                                flag = True
                                deviation = deviation_k
                                S_out1 = np.concatenate([S0, S_out], axis=0)   
                    if flag:
                        S_out = S_out1



            if isGrayUnionDisjoint(S_out) and len(S_out) == len_lst:
            # if len(S_out) == len_lst:
                item_nums = item_per_pool(S_out, n)
                deviation = np.max(item_nums) - np.min(item_nums)
                # print(f"ite1={ite1}, ite2={ite2}, isGrayUnionDisjoint, deviation={deviation}")
                if deviation_now > deviation:
                    deviation_now = deviation
                    S_out_out = S_out
            elif len(S_out) < len_lst:
                print(f"ite1={ite1}, ite2={ite2}, len(S_out)={len(S_out)}<M")
            else:
                print("not GrayUnionDisjoint.")

    if S_out_out is not None:
        balance = item_per_pool(S_out_out, n_pools)
        S_out_out = [arr.tolist() for arr in S_out_out]
    return balance, S_out_out


def gen_elementary_sequence(n, iters, nums, m, b = None):
    
    """
    For RCA_AU path search.
    Finds a balanced sequence via BBA_AU, and applies augmentation to generate the AES.
    Takes number of pools, number of pools per peptide, set of possible indices, the required path length, and the last address b.
    Returns the augemented (permuted) elementary sequence.
    Is dependent on function(bba_au), function(permutation_map).
    Used in function(reccom).
    """
    _, A = bba_au(n - 1, iters - 1, m)
    
    if A:
        B = np.array([[n-1]]*m)
        S = np.concatenate([A, B], axis=1)
        if b is None:
            cleared_nums = np.array([n - 1])
            nums = np.setdiff1d(nums, cleared_nums)
            return  S, nums
        else:
            S = permutation_map(S, -1, b, n, nums)
            cleared_nums = np.array([b[-1]])
            nums = np.setdiff1d(nums, cleared_nums)
            return  S, nums
    else:
        return [None, None]


def permute(start, b, n, nums):

    """
    For RCA_AU path search.
    Takes last address for a sequence, permuted version of this address, and returns permutation map.
    Used in function(reccom).
    """

    perm_vec = dict()
    perm_vec[start[-1]] = b[-1]

    a1 = np.setdiff1d(start, start[-1])
    b1 = np.setdiff1d(b, b[-1])

    for l in range(len(a1)):
        perm_vec[a1[l]] = b1[l]

    map_row1 = np.setdiff1d(np.array(range(n)), start)
    map_row2 = np.setdiff1d(nums, b)

    for l in range(len(map_row1)):
        perm_vec[map_row1[l]] = map_row2[l]

    return perm_vec


def balancing_weights(arr):

    """
    For RCA_AU path search.
    Takes weights of the arrangement, returns necessary balance by taking care of 0's and negative numbers.
    Used in function(AU_balance).
    """

    for i in range(len(arr)):
        if arr[i] < 0:
            mask = arr > 0
            min_el = np.where(mask)[0][np.argmin(arr[mask])]
            arr[min_el] = arr[min_el] - arr[i]
            arr[i] = 0
    return arr


def AU_balance(new_weights, perm_vec):

    """
    For RCA_AU path search.
    Takes weights of the arrangement and a permutation map.
    Returns permuted weights (balance for BBA_AU search step).
    Is dependent on function(balancing_weights).
    Used in function(reccom).
    """

    new_weights = balancing_weights(new_weights)
    bal = np.zeros(len(perm_vec), dtype=int)

    for new_index, old_index in perm_vec.items():
        bal[new_index] = new_weights[old_index]
    
    for i in range(len(bal)):
        if bal[i] == 0:
            bal[i] = 1
            max_el = np.argmax(bal)
            bal[max_el] -= 1
    return bal


def reccom(n, iters, len_lst, nums, weights, w_check = None, S=None):

    """
    RCA_AU path search.
    Takes number of pools, number of pools per peptide, the length of the required arrangement, set of possible indices, balance, overall balance, and previous address matrix.
    Returns matrix of addresses.
    Is dependent on function(gen_elementary_sequence), function(item_per_pool), function(permute), function(AU_balance),
    function(bba_au), function(bAU_search), function(permutation_map).
    """

    if S is None:
        m = weights[-1]
        S, nums = gen_elementary_sequence(n, iters, nums, m, b = None)
        if S is None:
            return None
        w_check = item_per_pool(S, len(weights))
        
    n_pools = len(weights)
    # balance in the arrangement
    new_weights = weights - w_check
    #bs = b_search(S, iters, nums)
    bs = bAU_search(S, n_pools, nums)
    # if b was found
    #if len(bs) > 0:
    b_weights = dict()
    for b in bs:
        b_weights[tuple(b)] = new_weights[b[-1]]
    b_weights = {k: v for k, v in sorted(b_weights.items(), key=lambda item: item[1], reverse=False)}
            
    # n_pools reduction
    n = n - 1

    # last elementary sequence
    if math.comb(n-1, iters) < math.comb(n-1, iters-1)+1:
        left = len_lst - len(S)
        for b in b_weights.keys():
                
            # calculating balance for BBA_AU
            start_a = ''.join(['1']*iters + ['0']*(n-iters))
            perm_vec = permute(list(range(iters)), b, n, nums)
            bal_for_AU = AU_balance(new_weights, perm_vec)
            # search for the arrangement with needed balance
            _, A = bba_au(n, iters, left, start_a, bal_for_AU)
            
            if A is not None:
                A = np.array(A, dtype = 'int')
                S_j = permutation_map(A[::-1], -1, b, n, nums)
                if S_j is not None:
                    S_new = np.concatenate([S_j, S], axis=0)
                        
                    return S_new

    # for each b
    for b in b_weights.keys():
        m = b_weights[b]
        av_ad = math.comb(n-1, iters-1)
        av_un = math.comb(n-1, iters)
        # if AU arrangement can be found
        if m > 0 and m < av_un and av_ad - m > 1:
            #if m is bigger than needed
            if m > len_lst-len(S):
                m = len_lst-len(S)
            S_j, nums_new = gen_elementary_sequence(n, iters, nums, m, b)
            if S_j is not None:
                w_check = item_per_pool(S_j, len(weights))
                S_new = np.concatenate([S_j, S], axis=0)

                if len(S_new) == len_lst:
                    return S_new

                # if arrangement needs only one next element
                elif len_lst-len(S_new) == 1:
                    end = bAU_search(S_new, n_pools, nums_new)
                    #end = b_search(S_new, iters, nums_new)
                    if len(end)>0:
                        b_S = np.concatenate([[end[0]], S_new], axis=0)
                        return b_S
            
                else:
                    res_path = reccom(n, iters, len_lst, nums_new, new_weights, w_check, S_new)
                    if res_path is not None:
                        return res_path


def rcau(n_pools, iters, len_lst):

    """
    For RCA_AU path search.
    Takes number of pools, number of pools per peptide, and the length of the required arrangement.
    Returns the arrangement.
    Is dependent on function(item_per_pool), function(reccom).
    
    """

    ## if there are enough addresses and unions
    if math.comb(n_pools, iters) <= len_lst or math.comb(n_pools, iters+1) <= len_lst:
        return [None, None]
    
    w=math.floor(iters*len_lst/n_pools)
    weights = w * np.ones((n_pools,), dtype='int')
    delta = len_lst * iters - w * n_pools
    weights[:delta] += 1

    nums = np.arange(0, n_pools)
    bs0 =  np.array(list(combinations(nums, iters)))
        
    S = reccom(n_pools, iters, len_lst, nums, weights, w_check = None, S=None)
    if S is not None:
        balance = item_per_pool(S, n_pools)
        S = [arr.tolist() for arr in S]
        return balance, S
    else:
        return [None, None]


# # Check

def check_unique(lists):

    """
    To check constraints.
    Takes address matrix, returns a list. list[0] == TRUE if addresses are unique, list[1] == TRUE if unions are unique.
    
    """

    unique_lists = [list(l) for l in set(tuple(l) for l in lists)]
    all_lists_unique = len(unique_lists) == len(lists)

    unions = [set(lists[i]).union(set(lists[i+1])) for i in range(len(lists) - 1)]
    unique_unions = [list(u) for u in set(tuple(u) for u in unions)]
    all_unions_unique = len(unique_unions) == len(unions)

    return all_lists_unique, all_unions_unique