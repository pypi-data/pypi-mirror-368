cdef class Node:
    cdef public int node_id
    cdef public str event
    cdef public children
    cdef public parents
    cdef public dict attributes