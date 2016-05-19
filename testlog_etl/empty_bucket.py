# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from __future__ import division
from __future__ import unicode_literals

from pyLibrary.aws import s3
from pyLibrary.debugs import startup
from pyLibrary.debugs.logs import Log
from pyLibrary.dot import unwrap
from pyLibrary.queries import jx
from testlog_etl import key2etl, etl2path


def main():
    """
    This script will delete everything in the active-data-codecoverage-dev bucket
    """
    try:
        settings = startup.read_settings()
        Log.alert(
            "READY TO DELETE FILES FROM {{bucket}} IN RANGE OF {{range.min}} TO {{range.max}}",
            bucket=settings.source.bucket,
            range=settings.range
        )
        try:
            input("Break out now to save yourself! Otherwise press <ENTER>.")
        except Exception:
            pass

        min_ = etl2path(key2etl(settings.range.min))
        max_ = etl2path(key2etl(settings.range.max))

        bucket = s3.Bucket(settings.source)
        delete_me = []
        for k in bucket.bucket.list():
            k = k.key
            if k == "0.json":
                continue
            etl = etl2path(key2etl(k))
            if gte(min_, etl) and gte(etl, max_):
                Log.note("will remove {{key}}", key=k)
                delete_me.append(k)
            else:
                pass

        for g, kk in jx.groupby(delete_me, 100):
            pass
            # bucket.delete_key(kk)

    except Exception, e:
        Log.error("Problem with compaction", e)
    finally:
        Log.stop()


def gte(a, b):
    for aa, bb in zip(unwrap(a), unwrap(b)):
        if aa < bb:
            return True
        elif aa > bb:
            return False
    return True


if __name__ == "__main__":
    main()
