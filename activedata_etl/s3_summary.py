from pyLibrary.aws import s3
from mo_logs import startup, constants
from mo_logs import Log
from mo_math.randoms import Random
from mo_threads import Thread


def summarize(settings):
    conn = s3.Connection(settings.aws).connection
    threads = []
    for b in conn.get_all_buckets():

        def counter(b, please_stop):
            bucket = conn.lookup(b.name)
            if not bucket:
                return

            count = 0
            total_bytes = 0
            for key in bucket:
                count += 1
                total_bytes += key.size
                if not Random.range(0, 10000):
                    Log.note("UPDATE: size = {{size}}, count = {{count}}", bucket=b.name, size=total_bytes, count=count)

                if please_stop:
                    return

            Log.note("SUMMARY: size = {{size}}, count = {{count}}", bucket=b.name, size=total_bytes, count=count)

        if b.name > "ekyle-talos-dev":
            threads.append(Thread.run("count " + b.name, counter, b))

    for t in threads:
        t.join()

try:
    settings = startup.read_settings()
    constants.set(settings.constants)
    Log.start(settings.debug)
    summarize(settings)
except Exception as e:
    Log.error("Problem with summary", e)
finally:
    Log.stop()
