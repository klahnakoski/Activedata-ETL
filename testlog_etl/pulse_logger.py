# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from __future__ import unicode_literals
from pyLibrary import convert
from pyLibrary.collections import MAX, MIN
from pyLibrary.collections.persistent_queue import PersistentQueue
from pyLibrary import aws
from pyLibrary.debugs import startup
from pyLibrary.debugs.logs import Log
from pyLibrary.env.pulse import Pulse
from pyLibrary.queries import Q
from pyLibrary.structs import set_default, wrap
from pyLibrary.thread.threads import Thread
from pyLibrary.times.dates import Date
from testlog_etl import etl2key
from testlog_etl.synchro import SynchState, SYNCHRONIZATION_KEY


def log_loop(settings, synch, queue, bucket, please_stop):
    with aws.Queue(settings.work_queue) as work_queue:
        for i, g in Q.groupby(queue, size=settings.param.size):
            etl_header = wrap({
                "name": "Pulse block",
                "bucket": settings.destination.bucket,
                "timestamp": Date.now().milli,
                "id": synch.next_key,
                "source": {
                    "id": unicode(MIN(g.select("_meta.count"))),
                    "name": "pulse.mozilla.org"
                },
                "type": "aggregation"
            })
            full_key = etl2key(etl_header)
            try:
                output = [etl_header]
                output.extend(
                    set_default(
                        {"etl": {
                            "name": "Pulse block",
                            "bucket": settings.destination.bucket,
                            "timestamp": Date.now().milli,
                            "id": synch.next_key,
                            "source": {
                                "name": "pulse.mozilla.org",
                                "timestamp": Date(d._meta.sent).milli,
                                "id": d._meta.count
                            }
                        }},
                        d.payload
                    )
                    for i, d in enumerate(g)
                )
                bucket.write(full_key + ".json", "\n".join(convert.value2json(d) for d in output))
                synch.advance()
                synch.source_key = MAX(g.select("_meta.count")) + 1

                work_queue.add({
                    "bucket": bucket.name,
                    "key": full_key
                })

                synch.ping()
                queue.commit()
                Log.note("Wrote {{num}} pulse messages to bucket={{bucket}}, key={{key}} ", {
                    "num": len(g),
                    "bucket": bucket.name,
                    "key": full_key
                })
            except Exception, e:
                queue.rollback()
                if not queue.closed:
                    Log.warning("Problem writing {{key}} to S3", {"key": full_key}, e)

            if please_stop:
                break
    Log.note("log_loop() completed on it's own")



def main():
    try:
        settings = startup.read_settings()
        Log.start(settings.debug)

        with startup.SingleInstance(flavor_id=settings.args.filename):
            with aws.s3.Bucket(settings.destination) as bucket:

                if settings.param.debug:
                    if settings.source.durable:
                        Log.error("Can not run in debug mode with a durable queue")
                    synch = SynchState(bucket.get_key(SYNCHRONIZATION_KEY))
                else:
                    synch = SynchState(bucket.get_key(SYNCHRONIZATION_KEY))
                    if settings.source.durable:
                        synch.startup()

                queue = PersistentQueue("pulse-logger-queue.json")
                if queue:
                    last_item = queue[len(queue) - 1]
                    synch.source_key = last_item._meta.count + 1

                with Pulse(settings.source, queue=queue, start=synch.source_key):
                    thread = Thread.run("pulse log loop", log_loop, settings, synch, queue, bucket)
                    Thread.wait_for_shutdown_signal()

                Log.note("starting shutdown")
                thread.stop()
                thread.join()
                queue.close()
                Log.note("write shutdown state to S3")
                synch.shutdown()

    except Exception, e:
        Log.error("Problem with etl", e)
    finally:
        Log.stop()


if __name__ == "__main__":
    main()
