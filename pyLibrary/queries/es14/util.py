# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http:# mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from pyLibrary.dot import wrap, split_field, join_field


def es_query_template(path):
    """
    RETURN TEMPLATE AND PATH-TO-FILTER AS A 2-TUPLE
    :param path:
    :return:
    """
    sub_path = split_field(path)[1:]

    if sub_path:
        f0 = {}
        f1 = {}
        output = wrap({
            "filter": {"and": [
                f0,
                {"nested": {
                    "path": join_field(sub_path),
                    "filter": f1,
                    "inner_hits": {"size": 100000}
                }}
            ]},
            "from": 0,
            "size": 0,
            "sort": []
        })
        return output, wrap([f0, f1])
    else:
        f0 = {}
        output = wrap({
            "query": {"filtered": {
                "filter": f0
            }},
            "from": 0,
            "size": 0,
            "sort": []
        })
        return output, wrap([f0])


def qb_sort_to_es_sort(sort):
    if not sort:
        return []

    output = []
    for s in sort:
        if s.sort == 1:
            output.append(s.value)
        elif s.sort == -1:
            output.append({s.value: "desc"})
        else:
            pass
    return output


# FOR ELASTICSEARCH aggs
aggregates1_4 = {
    "none": "none",
    "one": "count",
    "cardinality": "cardinality",
    "sum": "sum",
    "add": "sum",
    "count": "value_count",
    "maximum": "max",
    "minimum": "min",
    "max": "max",
    "min": "min",
    "mean": "avg",
    "average": "avg",
    "avg": "avg",
    "median": "median",
    "percentile": "percentile",
    "N": "count",
    "s0": "count",
    "s1": "sum",
    "s2": "sum_of_squares",
    "std": "std_deviation",
    "stddev": "std_deviation",
    "var": "variance",
    "variance": "variance",
    "stats": "stats"
}

NON_STATISTICAL_AGGS = {"none", "one"}

