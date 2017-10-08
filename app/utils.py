# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from copy import deepcopy
from threading import RLock

truthy = frozenset(('t', 'true', 'y', 'yes', 'on', '1'))


def asbool(s):
    """ Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is any of ``t``, ``true``, ``y``, ``on``, or ``1``, otherwise
    return the boolean value ``False``.  If ``s`` is the value ``None``,
    return ``False``.  If ``s`` is already one of the boolean values ``True``
    or ``False``, return it."""
    if s is None:
        return False
    if isinstance(s, bool):
        return s
    s = str(s).strip()
    return s.lower() in truthy


class BaseDataTables:
    """

    """

    def __init__(self, request, columns, collection):

        self.columns = columns

        self.collection = collection

        # values specified by the datatable for filtering, sorting, paging
        self.request_values = request.values

        # results from the db
        self.result_data = None

        # total in the table after filtering
        self.cardinality_filtered = 0

        # total in the table unfiltered
        self.cadinality = 0

        self.run_queries()

    def output_result(self):

        output = {}

        # output['sEcho'] = str(int(self.request_values['sEcho']))
        output['iTotalRecords'] = str(self.cardinality)
        output['iTotalDisplayRecords'] = str(self.cardinality_filtered)
        aaData_rows = []

        for row in self.result_data:
            aaData_row = []
            for i in range(len(self.columns)):
                # #print row, self.columns, self.columns[i]
                aaData_row.append(str(row[self.columns[i]]))
            aaData_rows.append(aaData_row)

        output['aaData'] = aaData_rows

        return output

    def run_queries(self):

        self.result_data = self.collection
        self.cardinality_filtered = len(self.result_data)
        self.cardinality = len(self.result_data)


# https://www.willmcgugan.com/blog/tech/post/timed-caching-decorator/
def timed_cache(seconds=0, minutes=0, hours=0, days=0):
    time_delta = timedelta(seconds=seconds,
                           minutes=minutes,
                           hours=hours,
                           days=days)

    def decorate(f):

        f._lock = RLock()
        f._updates = {}
        f._results = {}

        def do_cache(*args, **kwargs):

            lock = f._lock
            lock.acquire()

            try:
                key = (args, tuple(sorted(kwargs.items(), key=lambda i: i[0])))

                updates = f._updates
                results = f._results

                t = datetime.now()
                updated = updates.get(key, t)

                if key not in results or t - updated > time_delta:
                    # Calculate
                    updates[key] = t
                    result = f(*args, **kwargs)
                    results[key] = deepcopy(result)
                    return result

                else:
                    # Cache
                    return deepcopy(results[key])

            finally:
                lock.release()

        return do_cache

    return decorate
