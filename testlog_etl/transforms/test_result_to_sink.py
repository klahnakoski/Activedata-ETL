# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from __future__ import unicode_literals
from __future__ import division

from pyLibrary import convert
from pyLibrary.debugs.logs import Log
from pyLibrary.thread.threads import Lock


is_done_lock=Lock()
is_done = set()

def process_test_result(source_key, source, destination, please_stop=None):
    if source.bucket.name == "ekyle-test-result" and len(source_key.split(".")) == 3:
        source_key = ".".join(source_key.split(".")[:-1])
        with is_done_lock:
            if source_key in is_done:
                return set()
            is_done.add(source_key)
            source.key = source_key

    lines = source.read_lines()

    keys=[]
    data = []
    for l in lines:
        record = convert.json2value(l)
        if record._id==None:
            continue
        keys.append(record._id)
        data.append({
            "id": record._id,
            "value": record
        })
        record._id = None
    if data:
        destination.extend(data)
    return set(keys)
