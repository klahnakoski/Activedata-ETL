# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from __future__ import unicode_literals

from pyLibrary import convert, strings
from pyLibrary.debugs.logs import Log
from pyLibrary.dot import Dict
from pyLibrary.env import http
from pyLibrary.times.timer import Timer
from testlog_etl.transforms.pulse_block_to_es import scrub_pulse_record
from testlog_etl.transforms.pulse_block_to_unittest_logs import EtlHeadGenerator

DEBUG = False

TALOS_PREFIX = b"     INFO -  INFO : TALOSDATA: "


def process(source_key, source, dest_bucket, please_stop=None):
    """
    SIMPLE CONVERT pulse_block INTO TALOS, IF ANY
    """
    all_talos = []
    stats = Dict()
    etl_head_gen = EtlHeadGenerator(source_key)

    for i, pulse_line in enumerate(source.read_lines()):
        pulse_record = scrub_pulse_record(source_key, i, pulse_line, stats)
        if not pulse_record:
            continue

        if not pulse_record.data.talos:
            continue

        try:
            with Timer("Read {{url}}", {"url": pulse_record.data.logurl}, debug=DEBUG):
                response = http.get(pulse_record.data.logurl)
                if response.status_code == 404:
                    Log.alarm("Talos log missing {{url}}",  url= pulse_record.data.logurl)
                    continue
                all_log_lines = response.all_lines

            for log_line in all_log_lines:
                s = log_line.find(TALOS_PREFIX)
                if s < 0:
                    continue

                log_line = strings.strip(log_line[s + len(TALOS_PREFIX):])
                talos = convert.json2value(convert.utf82unicode(log_line))

                for t in talos:
                    _, dest_etl = etl_head_gen.next(pulse_record.data.etl, "talos")
                    t.etl = dest_etl
                all_talos.extend(talos)

        except Exception, e:
            Log.error("Problem processing {{url}}", {
                "url": pulse_record.data.logurl
            }, e)

    output = set()
    if all_talos:
        Log.note("found {{num}} talos records",  num= len(all_talos))
        output = dest_bucket.extend([{"id": source_key + "." + unicode(t.etl.id), "value": t} for t in all_talos])
    return output
