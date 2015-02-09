import csv
from StringIO import StringIO
from math import ceil
from collections import Mapping, Sequence


def __expand_container(cont, i, j, empty_sym=''):
    """ Expand, if possible, the list of list cont of size (h, k) to a list
        of lists of size (i, j). If the expansion is successful, newly
        created elements are filled with data empty_sym.
    """
    for ln in cont:
        # expand horizontally
        if len(ln) < j:
            ln.extend([empty_sym for k in range((j - len(ln)))])
    if len(cont) < i:
        # expand vertically
        cont.extend([[empty_sym for k in range(j)]
                     for h in range((i - len(cont)))])


def __recursive_insert_data(di, data_cont, col_index):
    """ Recursively insert data into data_cont (list of list)
        while visiting the data container di (either a dictionary-like
        container or a list-like container) using DFS.
        The position of data_cont in which the data is insert is
        col_index; if data_cont is not big enough to accommodate the
        data, it will be automatically expanded.
    """
    print type(di), isinstance(di, Mapping)

    if not(isinstance(di, Mapping)) and not(isinstance(di, Sequence)):
        # reached the data, back up a position to insert it in!
        return col_index

    new_col_index = col_index

    # assign progressive index names starting from 0 if di
    # is a list-like object
    di_iter = (di.iteritems() if isinstance(di, Mapping) else enumerate(di))

    for k, v in di_iter:
        # recursively insert data for the sublist of di
        new_col_index = __recursive_insert_data(v, data_cont, new_col_index)

    if new_col_index == col_index:
        # previous iteration has reached the data, better dump!
        __expand_container(data_cont, len(di), col_index + 1)
        for i, elem in enumerate(di):
            data_cont[i][col_index] = elem
        return (col_index + 1)
    else:
        # di contains multiple subheaders, so no dumping
        return new_col_index


def __recursive_build_header((name, di), heads_cont, left, depth):
    """ Recursively detect headers in di. Headers are collected in
        the container heads_cont.
        The container is automatically expanded if needed.
    """
    if not(isinstance(di, Mapping)) or not(isinstance(di, Sequence)):
        return left

    right = left
    di_iter = (di.iteritems() if isinstance(di, Mapping) else enumerate(di))
    for k, v in di_iter:
        right = __recursive_build_header((k, v), heads_cont, right, depth + 1)

    if left == right:
        __expand_container(heads_cont, depth + 1, right + 1,)
        heads_cont[depth][right] = name
        right += 1
    elif name is not None:
        pos = left + (int(ceil(float(right - left) / 2)) - 1)
        heads_cont[depth][pos] = name
    return right


def dict2csv(di, csv_kwargs=None):
    """ Input: a dictionary [of dictionaries]* containing data
               (optional) arguments to control layout of csv file
        Output: a string ready to be written as csv file
    """

    # collect data
    data_cont = []
    __recursive_insert_data(di, data_cont, 0)

    # format headers
    heads_cont = []
    __recursive_build_header((None, di), heads_cont, 0, 0)
    heads_cont = heads_cont[1:]

    # prepare output file
    outstr = StringIO()
    if csv_kwargs is None:
        csv_kwargs = {}
    wr = csv.writer(outstr, **csv_kwargs)

    # write data
    wr.writerows(heads_cont)
    wr.writerows(data_cont)

    # rewind and return data
    outstr.seek(0)
    outstr = outstr.read()
    return outstr
