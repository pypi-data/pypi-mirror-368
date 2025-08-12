(venv) root@shadow189:/vyomos$ tail -f -n 200000 /var/log/vyomcloudbridge/vyomcloudbridge.log | grep Error
2025-08-05 15:41:46,077 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388703997.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:41:46,163 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388704143.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:41:48,090 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388703997.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:41:48,176 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388704143.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:41:50,104 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388703997.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:41:50,203 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388704143.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:41:56,570 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Stream connection lost: IndexError('pop from an empty deque')
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 15:41:56,826 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Stream connection lost: IndexError('pop from an empty deque')
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 15:41:57,042 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Stream connection lost: AssertionError(('_AsyncTransportBase._produce() tx buffer size underflow', -69, 1))
pika.exceptions.StreamLostError: Stream connection lost: AssertionError(('_AsyncTransportBase._produce() tx buffer size underflow', -69, 1))
2025-08-05 15:41:57,065 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Channel is closed.
    raise exceptions.ChannelWrongStateError('Channel is closed.')
pika.exceptions.ChannelWrongStateError: Channel is closed.
2025-08-05 15:41:57,162 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: ('_AsyncTransportBase._initate_abort() expected non-_STATE_COMPLETED', 4)
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
IndexError: pop from an empty deque
AssertionError: ('_AsyncTransportBase._initate_abort() expected non-_STATE_COMPLETED', 4)
2025-08-05 15:41:58,622 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388716590.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:41:59,097 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Stream connection lost: IndexError('pop from an empty deque')
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 15:41:59,099 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: ('_AsyncTransportBase._initate_abort() expected non-_STATE_COMPLETED', 4)
IndexError: pop from an empty deque
AssertionError: ('_AsyncTransportBase._initate_abort() expected non-_STATE_COMPLETED', 4)
2025-08-05 15:41:59,101 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: ('_AsyncTransportBase._initate_abort() expected _STATE_ABORTED_BY_USER', 4)
AssertionError: ('_AsyncTransportBase._produce() tx buffer size underflow', -123, 1)
AssertionError: ('_AsyncTransportBase._initate_abort() expected _STATE_ABORTED_BY_USER', 4)
2025-08-05 15:41:59,228 - vyomcloudbridge.services.rabbit_queue.queue_main - WARNING - RabbitMQ connection attempt 1 failed AMQPConnectionError, retrying...
2025-08-05 15:41:59,230 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: ('_AsyncTransportBase._initate_abort() expected non-_STATE_COMPLETED', 4)
IndexError: pop from an empty deque
AssertionError: ('_AsyncTransportBase._initate_abort() expected non-_STATE_COMPLETED', 4)
2025-08-05 15:41:59,347 - vyomcloudbridge.services.rabbit_queue.queue_main - WARNING - RabbitMQ connection attempt 1 failed AMQPConnectionError, retrying...
2025-08-05 15:41:59,347 - vyomcloudbridge.services.chunk_merger.ChunkMerger - ERROR - Error publishing chunk merger notification: Could not establish connection
2025-08-05 15:41:59,386 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388717012.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:00,521 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Stream connection lost: IndexError('pop from an empty deque')
AssertionError: ('_AsyncTransportBase._produce() tx buffer size underflow', -123, 1)
AssertionError: ('_AsyncTransportBase._initate_abort() expected _STATE_ABORTED_BY_USER', 4)
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 15:42:00,693 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388716590.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:00,970 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Stream connection lost: IndexError('pop from an empty deque')
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 15:42:01,139 - vyomcloudbridge.services.rabbit_queue.queue_main - WARNING - RabbitMQ connection attempt 1 failed AMQPConnectionError, retrying...
2025-08-05 15:42:01,507 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388717012.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:02,349 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Stream connection lost: IndexError('pop from an empty deque')
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 15:42:02,473 - vyomcloudbridge.services.rabbit_queue.queue_main - WARNING - RabbitMQ connection attempt 1 failed AMQPConnectionError, retrying...
2025-08-05 15:42:02,483 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: 'NoneType' object has no attribute 'write'
AttributeError: 'NoneType' object has no attribute 'write'
2025-08-05 15:42:02,758 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388716590.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:02,831 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Stream connection lost: IndexError('pop from an empty deque')
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 15:42:03,622 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388717012.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:04,069 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388721894.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:04,089 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Stream connection lost: IndexError('pop from an empty deque')
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 15:42:04,277 - vyomcloudbridge.services.rabbit_queue.queue_main - WARNING - RabbitMQ connection attempt 1 failed AMQPConnectionError, retrying...
2025-08-05 15:42:04,278 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Channel is closed.
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
    raise exceptions.ChannelWrongStateError('Channel is closed.')
pika.exceptions.ChannelWrongStateError: Channel is closed.
2025-08-05 15:42:04,399 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388722115.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:04,407 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Stream connection lost: IndexError('pop from an empty deque')
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 15:42:04,483 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388722291.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:04,748 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_summary/1754388722309.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:06,168 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388721894.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:06,496 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388722115.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:06,765 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388722291.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:07,018 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_summary/1754388722309.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:08,207 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388721894.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:08,615 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388722115.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:08,821 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_stats/1754388722291.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:42:09,080 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/88054183/mission_summary/1754388722309.json, remaining_dest_ids: [gcs_mav]
2025-08-05 15:51:07,036 - vyomcloudbridge.services.machine_stats.MachineStats - ERROR - Error processing buffer array: 
2025-08-05 15:58:09,628 - vyomcloudbridge.services.machine_stats.MachineStats - ERROR - Error processing buffer array: 
2025-08-05 16:21:59,193 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391117143.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:21:59,229 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391117214.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:01,208 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391117143.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:01,243 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391117214.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:03,221 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391117143.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:03,257 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391117214.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:12,906 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391130587.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:12,950 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391130818.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:13,525 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Stream connection lost: IndexError('pop from an empty deque')
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 16:22:13,705 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Failed to ensure connection: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 16:22:13,706 - vyomcloudbridge.services.chunk_merger.ChunkMerger - ERROR - Error publishing chunk merger notification: Could not establish connection
2025-08-05 16:22:14,965 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391130587.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:14,976 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391130818.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:15,247 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Stream connection lost: IndexError('pop from an empty deque')
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 16:22:16,987 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391130587.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:17,016 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391130818.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:18,099 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391135492.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:18,722 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391135635.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:18,825 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391135761.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:19,006 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_summary/1754391135769.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:19,895 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: (505, 'UNEXPECTED_FRAME - expected content header for class 60, got non content header frame instead')
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 16:22:20,093 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Stream connection lost: IndexError('pop from an empty deque')
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 16:22:20,165 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391135492.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:20,683 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Stream connection lost: IndexError('pop from an empty deque')
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 16:22:20,776 - vyomcloudbridge.services.rabbit_queue.queue_main - WARNING - RabbitMQ connection attempt 1 failed AMQPConnectionError, retrying...
2025-08-05 16:22:20,776 - vyomcloudbridge.services.rabbit_queue.queue_main - ERROR - Error publishing message: Stream connection lost: IndexError('pop from an empty deque')
pika.exceptions.StreamLostError: Stream connection lost: IndexError('pop from an empty deque')
2025-08-05 16:22:20,839 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391135635.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:20,897 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391135761.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:20,964 - vyomcloudbridge.services.rabbit_queue.queue_main - WARNING - RabbitMQ connection attempt 1 failed AMQPConnectionError, retrying...
2025-08-05 16:22:21,178 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_summary/1754391135769.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:22,663 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391135492.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:22,884 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391135635.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:23,178 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_stats/1754391135761.json, remaining_dest_ids: [gcs_mav]
2025-08-05 16:22:23,282 - vyomcloudbridge.services.queue_worker.QueueWorker - ERROR - Error: Message proccesing failed topic: 1/_all_/2025-08-05/183/98879183/mission_summary/1754391135769.json, remaining_dest_ids: [gcs_mav]
grep: (standard input): binary file matches