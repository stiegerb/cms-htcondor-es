"""
Process the jobs in queue for given set of schedds.
"""

import json
import time
import logging
import resource
import traceback
import Queue
import multiprocessing
import Queue

import htcondor

import htcondor_es.es
import htcondor_es.amq
from htcondor_es.utils import send_email_alert, time_remaining, TIMEOUT_MINS
from htcondor_es.convert_to_json import convert_to_json
from htcondor_es.convert_to_json import convert_dates_to_millisecs
from htcondor_es.convert_to_json import unique_doc_id



class ListenAndBunch(multiprocessing.Process):
    """
    Listens to incoming items on a queue and puts bunches of items
    to an outgoing queue

    n_expected is the expected number of agents writing to the
    queue. Necessary for knowing when to shut down.
    """

    def __init__(self, input_queue, output_queue,
                 n_expected,
                 starttime,
                 bunch_size=5000,
                 report_every=50000):
        super(ListenAndBunch, self).__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue
        logging.warning("Bunching records for AMQP in sizes of %d", bunch_size)
        self.bunch_size = bunch_size
        self.report_every = report_every
        self.n_expected = n_expected
        self.starttime = starttime

        self.buffer = []
        self.tracker = []
        self.n_processed = 0
        self.count_in = 0 # number of added docs

        self.start()


    def run(self):
        since_last_report = 0
        while True:
            try:
                next_batch = self.input_queue.get(timeout=time_remaining(self.starttime, positive=True)-5)
            except Queue.Empty:
                logging.warning("Closing listener before all schedds were processed")
                self.close()
                return

            if isinstance(next_batch, basestring):
                schedd_name = str(next_batch)
                try:
                    # We were already processing this sender,
                    # this is the signal that it's done sending.
                    self.tracker.remove(schedd_name)
                    self.n_processed += 1
                except ValueError:
                    # This is a new sender
                    self.tracker.append(schedd_name)

                if self.n_processed == self.n_expected:
                    # We finished processing all expected senders.
                    assert len(self.tracker) == 0
                    self.close()
                    return
                continue

            self.count_in += len(next_batch)
            since_last_report += len(next_batch)
            self.buffer.extend(next_batch)

            if since_last_report > self.report_every:
                logging.debug("Processed %d docs", self.count_in)
                since_last_report = 0

            # If buffer is full, send the docs and clear the buffer
            if len(self.buffer) >= self.bunch_size:
                self.output_queue.put(self.buffer[:self.bunch_size],
                                      timeout=time_remaining(self.starttime, positive=True))
                self.buffer = self.buffer[self.bunch_size:]

    def close(self):
        """Clear the buffer, send a poison pill and the total number of docs"""
        if self.buffer:
            self.output_queue.put(self.buffer, timeout=time_remaining(self.starttime, positive=True))
            self.buffer = []

        logging.warning("Closing listener, received %d documents total", self.count_in)
        # send back a poison pill
        self.output_queue.put(None, timeout=time_remaining(self.starttime, positive=True))
        # send the number of total docs
        self.output_queue.put(self.count_in, timeout=time_remaining(self.starttime, positive=True))


def process_schedd_queue(starttime, schedd_ad, queue, args):
    my_start = time.time()
    logging.info("Querying %s queue for jobs.", schedd_ad["Name"])
    if time_remaining(starttime) < 10:
        message = ("No time remaining to run queue crawler on %s; "
                   "exiting." % schedd_ad['Name'])
        logging.error(message)
        send_email_alert(args.email_alerts,
                         "spider_cms queue timeout warning",
                         message)
        return

    count_since_last_report = 0
    count = 0
    cpu_usage = resource.getrusage(resource.RUSAGE_SELF).ru_utime
    queue.put(schedd_ad['Name'], timeout=time_remaining(starttime, positive=True))

    schedd = htcondor.Schedd(schedd_ad)
    sent_warnings = False
    batch = []
    try:
        query_iter = schedd.xquery() if not args.dry_run else []
        for job_ad in query_iter:
            dict_ad = None
            try:
                dict_ad = convert_to_json(job_ad, return_dict=True,
                                          reduce_data=args.reduce_running_data)
            except Exception as e:
                message = ("Failure when converting document on %s queue: %s" %
                           (schedd_ad["Name"], str(e)))
                logging.warning(message)
                if not sent_warnings:
                    send_email_alert(args.email_alerts,
                                     "spider_cms queue document conversion error",
                                     message)
                    sent_warnings = True

            if not dict_ad:
                continue

            batch.append((unique_doc_id(dict_ad), dict_ad))
            count += 1
            count_since_last_report += 1

            if not args.dry_run and len(batch) == args.query_queue_batch_size:
                if time_remaining(starttime) < 10:
                    message = ("Queue crawler on %s has been running for "
                               "more than %d minutes; exiting" %
                               (schedd_ad['Name'], TIMEOUT_MINS))
                    logging.error(message)
                    send_email_alert(args.email_alerts,
                                     "spider_cms queue timeout warning",
                                     message)
                    break
                queue.put(batch, timeout=time_remaining(starttime, positive=True))
                batch = []
                if count_since_last_report >= 1000:
                    cpu_usage_now = resource.getrusage(resource.RUSAGE_SELF).ru_utime
                    cpu_usage = cpu_usage_now - cpu_usage
                    processing_rate = count_since_last_report / cpu_usage
                    cpu_usage = cpu_usage_now
                    logging.debug("Processor for %s has processed %d jobs "
                                 "(%.1f jobs per CPU-second)",
                                 schedd_ad['Name'], count, processing_rate)
                    count_since_last_report = 0

        if batch:  # send remaining docs
            queue.put(batch, timeout=time_remaining(starttime, positive=True))
            batch = []

    except RuntimeError, e:
        logging.error("Failed to query schedd %s for jobs: %s",
                      schedd_ad["Name"], str(e))
    except Exception, e:
        message = ("Failure when processing schedd queue query on %s: %s" %
                   (schedd_ad["Name"], str(e)))
        logging.error(message)
        send_email_alert(args.email_alerts, "spider_cms schedd queue query error",
                         message)
        traceback.print_exc()

    queue.put(schedd_ad['Name'], timeout=time_remaining(starttime, positive=True))
    total_time = (time.time() - my_start)/60.
    logging.warning("Schedd %-25s queue: response count: %5d; "
                    "query time %.2f min; ",
                    schedd_ad["Name"], count, total_time)

    return count


def process_queues(schedd_ads, starttime, pool, args):
    """
    Process all the jobs in all the schedds given.
    """
    my_start = time.time()
    if time_remaining(starttime) < 10:
        logging.warning("No time remaining to process queues")
        return

    mp_manager = multiprocessing.Manager()
    input_queue = mp_manager.Queue()
    output_queue = mp_manager.Queue()
    listener = ListenAndBunch(input_queue=input_queue,
                              output_queue=output_queue,
                              n_expected=len(schedd_ads),
                              starttime=starttime,
                              bunch_size=5000)
    futures = []

    upload_pool = multiprocessing.Pool(processes=args.upload_pool_size)

    for schedd_ad in schedd_ads:
        future = pool.apply_async(process_schedd_queue,
                                  args=(starttime, schedd_ad, input_queue, args))
        futures.append((schedd_ad['Name'], future))

    def _callback_amq(result):
        sent, received, elapsed = result
        logging.info("Uploaded %d/%d docs to StompAMQ in %d seconds", sent, received, elapsed)

    total_processed = 0
    while True:
        if args.dry_run or len(schedd_ads) == 0:
            break

        if time_remaining(starttime) < 5:
            logging.warning("Listener did not shut down properly; terminating.")
            listener.terminate()
            break

        bunch = output_queue.get(timeout=time_remaining(starttime, positive=True))
        if bunch is None: # swallow the poison pill
            total_processed = int(output_queue.get(timeout=time_remaining(starttime, positive=True)))
            break

        if args.feed_amq and not args.read_only:
            amq_bunch = [(id_, convert_dates_to_millisecs(dict_ad)) for id_, dict_ad in bunch]
            future = upload_pool.apply_async(htcondor_es.amq.post_ads,
                                             args=(amq_bunch,),
                                             callback=_callback_amq)
            futures.append(("UPLOADER_AMQ", future))
            logging.info("Starting AMQ uploader, %d items in queue" % output_queue.qsize())

        if args.feed_es_for_queues and not args.read_only:
            es_bunch = [(id_, json.dumps(dict_ad)) for id_, dict_ad in bunch]
            ## FIXME: Why are we determining the index from one ad?
            idx = htcondor_es.es.get_index(bunch[0][1].get("QDate", int(time.time())),
                                           template=args.es_index_template,
                                           update_es=(args.feed_es and not args.read_only))

            future = upload_pool.apply_async(htcondor_es.es.post_ads_nohandle,
                                             args=(idx, es_bunch, args))
            futures.append(("UPLOADER_ES", future))

        # # Limit the number of concurrent upload processes
        # while len([f for f in futures if f[0].startswith('UPLOADER') and not f[1].ready()]) >= args.upload_pool_size:
        #     if time_remaining(starttime) < 0:
        #         break

        #     # Wait a short time before counting again
        #     time.sleep(1)

    listener.join()

    timed_out = False
    total_sent = 0
    total_upload_time = 0
    total_queried = 0
    for name, future in futures:
        if time_remaining(starttime) > -20:
            try:
                count = future.get(time_remaining(starttime, positive=True)+10)
                if name == "UPLOADER_AMQ":
                    total_sent += count[0]
                    total_upload_time += count[2]
                elif name == "UPLOADER_ES":
                    total_sent += count
                else:
                    try:
                        total_queried += count
                    except TypeError:
                        pass
            except multiprocessing.TimeoutError:
                message = "Schedd %s queue timed out; ignoring progress." % name
                logging.error(message)
                send_email_alert(args.email_alerts,
                                 "spider_cms queue timeout warning",
                                 message)
        else:
            timed_out = True
            break

    if timed_out:
        logging.error("Timed out when retrieving uploaders. Upload count incomplete.")
        pool.terminate()
        upload_pool.terminate()

    if not total_queried == total_processed:
        logging.warning("Number of queried docs not equal to number of processed docs.")

    logging.warning("Processing time for queues: %.2f mins, %d/%d docs sent in %.2f min "
                    "of total upload time",
                    (time.time()-my_start)/60., total_sent, total_queried,
                    total_upload_time/60.)

    upload_pool.close()
    upload_pool.join()
