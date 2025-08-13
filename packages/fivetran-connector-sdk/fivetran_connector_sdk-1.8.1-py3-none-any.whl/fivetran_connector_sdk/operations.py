import json
import sys
import queue
import threading

from datetime import datetime
from google.protobuf import timestamp_pb2

from fivetran_connector_sdk.constants import (
    JAVA_LONG_MAX_VALUE,
    TABLES,
    MAX_RECORDS_IN_BATCH,
    MAX_BATCH_SIZE_IN_BYTES,
    QUEUE_SIZE,
    CHECKPOINT_OP_TIMEOUT_IN_SEC
)
from fivetran_connector_sdk.helpers import (
    get_renamed_table_name,
    get_renamed_column_name,
    print_library_log,
)
from fivetran_connector_sdk.logger import Logging
from fivetran_connector_sdk.protos import connector_sdk_pb2, common_pb2

class _OperationStream:
    """
    A simple iterator-based stream backed by a queue for producing and consuming operations.

    This class allows adding data items into a queue and consuming them using standard iteration.
    It uses a sentinel object to signal the end of the stream.

    Example:
        stream = _OperationStream()
        stream.add("response1")
        stream.mark_done()

        for response in stream:
            print(response)  # prints "response1"
    """

    def __init__(self):
        """
        Initializes the operation stream with a queue and a sentinel object.
        """
        self._queue = queue.Queue(maxsize=QUEUE_SIZE)
        self._sentinel = object()
        self._is_done = False
        self._buffer = []
        self._buffer_record_count = 0
        self._buffer_size_bytes = 0
        self._checkpoint_lock = threading.Lock()
        self._checkpoint_flush_signal = threading.Event()
        self._checkpoint_flush_signal.set()

    def __iter__(self):
        """
        Returns the iterator instance itself.
        """
        return self

    def add(self, operation):
        """
        Adds an operation to the stream. Guarantees that operations within a single thread are processed in the order.

        In multithreaded environment if a thread initiates a checkpoint, it's producer is blocked until the
        checkpoint flush is complete. This block is localized, other threads
        remain unblocked and can continue to perform other operations
        (such as upserts, updates, deletes), but they are prevented from initiating a new checkpoint
        until the existing one is finished.

        Args:
            operation (object): The data item to add to the stream.
        """
        if isinstance(operation, connector_sdk_pb2.Checkpoint):
            # lock to ensure checkpoint operations are processed one at a time
            with self._checkpoint_lock:
                # clear the signal to indicate checkpoint operation is being processed.
                self._checkpoint_flush_signal.clear()
                self._queue.put(operation)
                # wait until the consumer flushes the buffer and sets the flag.
                if not self._checkpoint_flush_signal.wait(CHECKPOINT_OP_TIMEOUT_IN_SEC):
                    raise TimeoutError(
                        "Checkpoint flush timed out. Consumer may have failed to process checkpoint."
                    )
        else:
            self._queue.put(operation)

    def unblock(self):
        """
        Unblocks the queue, called by consumer after the checkpoint flush is completed.
        """
        self._checkpoint_flush_signal.set()

    def mark_done(self):
        """
        Marks the end of the stream by putting a sentinel in the queue.
        """
        self._queue.put(self._sentinel)

    def __next__(self):
        """
        Retrieves the next item from the stream. Raises StopIteration when the sentinel is encountered.

        Returns:
            object: The next item in the stream.

        Raises:
            StopIteration: If the sentinel object is encountered.
        """
        # If stream is completed and buffer is empty, raise StopIteration. Else flush the buffer.
        if self._is_done and not self._buffer:
            raise StopIteration

        if self._is_done:
            return self._flush_buffer()

        return self._build_next_batch()

    def _build_next_batch(self):
        """
        Core logic to build the batch. The loop continues until the buffer is full,
        but can be interrupted by a checkpoint or a sentinel from the producer.

        Returns:
            connector_sdk_pb2.UpdateResponse or list[connector_sdk_pb2.UpdateResponse]: Either a single response
            containing records or checkpoint, or a list of responses when flushing data with a checkpoint.

        """
        while self._buffer_record_count < MAX_RECORDS_IN_BATCH and self._buffer_size_bytes < MAX_BATCH_SIZE_IN_BYTES:
            operation = self._queue.get()

            # Case 1: If operation is sentinel, mark the stream as done, flush the buffer.
            if operation is self._sentinel:
                self._is_done = True
                if self._buffer:
                    return self._flush_buffer()
                else:
                    raise StopIteration

            # Case 2: if operation is a Checkpoint, flush the buffer and send the checkpoint.
            elif isinstance(operation, connector_sdk_pb2.Checkpoint):
                return self._flush_buffer_on_checkpoint(operation)

            # it is record, buffer it to flush in batches
            self._buffer_record_count += 1
            self._buffer_size_bytes += len(operation.SerializeToString())
            self._buffer.append(operation)

        # Case 3: If buffer size limit is reached, flush the buffer and return the response.
        return self._flush_buffer()

    def _flush_buffer_on_checkpoint(self, checkpoint: connector_sdk_pb2.Checkpoint):
        """
        Creates the responses containing the checkpoint and buffered records.

        Args:
            checkpoint (object): Checkpoint operation to be added to the response.
        """
        responses = []

        if self._buffer:
            responses.append(self._flush_buffer())

        responses.append(connector_sdk_pb2.UpdateResponse(checkpoint=checkpoint))
        return responses

    def _flush_buffer(self):
        """
        Flushes the current buffer and returns a response containing the buffered records.

        Returns:
            connector_sdk_pb2.UpdateResponse: A response containing the buffered records.
        """
        batch_to_flush = self._buffer
        self._buffer = []
        self._buffer_record_count = 0
        self._buffer_size_bytes = 0
        return connector_sdk_pb2.UpdateResponse(records=connector_sdk_pb2.Records(records=batch_to_flush))


_LOG_DATA_TYPE_INFERENCE = {}

class Operations:
    operation_stream = _OperationStream()

    @staticmethod
    def upsert(table: str, data: dict):
        """Updates records with the same primary key if already present in the destination. Inserts new records if not already present in the destination.

        Args:
            table (str): The name of the table.
            data (dict): The data to upsert.

        Returns:
            list[connector_sdk_pb2.UpdateResponse]: A list of update responses.
        """
        table = get_renamed_table_name(table)
        columns = _get_columns(table)
        if not columns:
            for field in data.keys():
                field_name = get_renamed_column_name(field)
                columns[field_name] = common_pb2.Column(
                    name=field_name, type=common_pb2.DataType.UNSPECIFIED, primary_key=False)
            new_table = common_pb2.Table(name=table, columns=columns.values())
            TABLES[table] = new_table

        mapped_data = _map_data_to_columns(data, columns, table)
        record = connector_sdk_pb2.Record(
            schema_name=None,
            table_name=table,
            type=common_pb2.RecordType.UPSERT,
            data=mapped_data
        )

        Operations.operation_stream.add(record)

    @staticmethod
    def update(table: str, modified: dict):
        """Performs an update operation on the specified table with the given modified data.

        Args:
            table (str): The name of the table.
            modified (dict): The modified data.

        Returns:
            connector_sdk_pb2.UpdateResponse: The update response.
        """
        table = get_renamed_table_name(table)
        columns = _get_columns(table)
        mapped_data = _map_data_to_columns(modified, columns, table)
        record = connector_sdk_pb2.Record(
            schema_name=None,
            table_name=table,
            type=common_pb2.RecordType.UPDATE,
            data=mapped_data
        )

        Operations.operation_stream.add(record)

    @staticmethod
    def delete(table: str, keys: dict):
        """Performs a soft delete operation on the specified table with the given keys.

        Args:
            table (str): The name of the table.
            keys (dict): The keys to delete.

        Returns:
            connector_sdk_pb2.UpdateResponse: The delete response.
        """
        table = get_renamed_table_name(table)
        columns = _get_columns(table)
        mapped_data = _map_data_to_columns(keys, columns, table)
        record = connector_sdk_pb2.Record(
            schema_name=None,
            table_name=table,
            type=common_pb2.RecordType.DELETE,
            data=mapped_data
        )

        Operations.operation_stream.add(record)

    @staticmethod
    def checkpoint(state: dict):
        """Checkpoint saves the connector's state. State is a dict which stores information to continue the
        sync from where it left off in the previous sync. For example, you may choose to have a field called
        "cursor" with a timestamp value to indicate up to when the data has been synced. This makes it possible
        for the next sync to fetch data incrementally from that time forward. See below for a few example fields
        which act as parameters for use by the connector code.\n
        {
            "initialSync": true,\n
            "cursor": "1970-01-01T00:00:00.00Z",\n
            "last_resync": "1970-01-01T00:00:00.00Z",\n
            "thread_count": 5,\n
            "api_quota_left": 5000000
        }

        Args:
            state (dict): The state to checkpoint/save.

        Returns:
            connector_sdk_pb2.UpdateResponse: The checkpoint response.
        """
        checkpoint = connector_sdk_pb2.Checkpoint(state_json=json.dumps(state))

        Operations.operation_stream.add(checkpoint)

def _get_columns(table: str) -> dict:
    """Retrieves the columns for the specified table.

    Args:
        table (str): The name of the table.

    Returns:
        dict: The columns for the table.
    """
    columns = {}
    if table in TABLES:
        for column in TABLES[table].columns:
            columns[column.name] = column

    return columns

def _get_table_pk(table: str) -> bool:
    """Retrieves the columns for the specified table.

    Args:
        table (str): The name of the table.

    Returns:
        dict: The columns for the table.
    """
    columns = {}
    if table in TABLES:
        for column in TABLES[table].columns:
            if column.primary_key:
                return True
    return False


def _map_data_to_columns(data: dict, columns: dict, table: str = "") -> dict:
    """Maps data to the specified columns.

    Args:
        data (dict): The data to map.
        columns (dict): The columns to map the data to.

    Returns:
        dict: The mapped data.
    """
    mapped_data = {}
    for k, v in data.items():
        key = get_renamed_column_name(k)
        if v is None:
            mapped_data[key] = common_pb2.ValueType(null=True)
        elif (key in columns) and columns[key].type != common_pb2.DataType.UNSPECIFIED:
            map_defined_data_type(columns[key].type, key, mapped_data, v)
        else:
            map_inferred_data_type(key, mapped_data, v, table)
    return mapped_data

def map_inferred_data_type(k, mapped_data, v, table=""):
    # We can infer type from the value
    if isinstance(v, int):
        if abs(v) > JAVA_LONG_MAX_VALUE:
            mapped_data[k] = common_pb2.ValueType(float=v)
        else:
            mapped_data[k] = common_pb2.ValueType(long=v)
        if _LOG_DATA_TYPE_INFERENCE.get("boolean_" + table, True) and isinstance(v, bool):
            print_library_log("Fivetran: Boolean Datatype has been inferred for " + table, Logging.Level.INFO, True)
            if not _get_table_pk(table):
                print_library_log("Fivetran: Boolean Datatype inference issue for " + table, Logging.Level.INFO, True)
            _LOG_DATA_TYPE_INFERENCE["boolean_" + table] = False
    elif isinstance(v, float):
        mapped_data[k] = common_pb2.ValueType(float=v)
    elif isinstance(v, bool):
        mapped_data[k] = common_pb2.ValueType(bool=v)
    elif isinstance(v, bytes):
        mapped_data[k] = common_pb2.ValueType(binary=v)
    elif isinstance(v, list):
        raise ValueError(
            "Values for the columns cannot be of type 'list'. Please ensure that all values are of a supported type. Reference: https://fivetran.com/docs/connectors/connector-sdk/technical-reference#supporteddatatypes")
    elif isinstance(v, dict):
        mapped_data[k] = common_pb2.ValueType(json=json.dumps(v))
    elif isinstance(v, str):
        mapped_data[k] = common_pb2.ValueType(string=v)
    else:
        # Convert arbitrary objects to string
        mapped_data[k] = common_pb2.ValueType(string=str(v))

_TYPE_HANDLERS = {
    common_pb2.DataType.BOOLEAN: lambda val: common_pb2.ValueType(bool=val),
    common_pb2.DataType.SHORT: lambda val: common_pb2.ValueType(short=val),
    common_pb2.DataType.INT: lambda val: common_pb2.ValueType(int=val),
    common_pb2.DataType.LONG: lambda val: common_pb2.ValueType(long=val),
    common_pb2.DataType.DECIMAL: lambda val: common_pb2.ValueType(decimal=val),
    common_pb2.DataType.FLOAT: lambda val: common_pb2.ValueType(float=val),
    common_pb2.DataType.DOUBLE: lambda val: common_pb2.ValueType(double=val),
    common_pb2.DataType.NAIVE_DATE: lambda val: common_pb2.ValueType(naive_date= _parse_naive_date_str(val)),
    common_pb2.DataType.NAIVE_DATETIME: lambda val: common_pb2.ValueType(naive_datetime= _parse_naive_datetime_str(val)),
    common_pb2.DataType.UTC_DATETIME: lambda val: common_pb2.ValueType(utc_datetime= _parse_utc_datetime_str(val)),
    common_pb2.DataType.BINARY: lambda val: common_pb2.ValueType(binary=val),
    common_pb2.DataType.XML: lambda val: common_pb2.ValueType(xml=val),
    common_pb2.DataType.STRING: lambda val: common_pb2.ValueType(string=val if isinstance(val, str) else str(val)),
    common_pb2.DataType.JSON: lambda val: common_pb2.ValueType(json=json.dumps(val))
}

def map_defined_data_type(data_type, k, mapped_data, v):
    handler = _TYPE_HANDLERS.get(data_type)
    if handler:
        mapped_data[k] = handler(v)
    else:
        raise ValueError(f"Unsupported data type encountered: {data_type}. Please use valid data types.")

def _parse_utc_datetime_str(v):
    timestamp = timestamp_pb2.Timestamp()
    dt = v
    if not isinstance(v, datetime):
        dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%f%z" if '.' in dt else "%Y-%m-%dT%H:%M:%S%z")
    timestamp.FromDatetime(dt)
    return timestamp

def _parse_naive_datetime_str(v):
    if '.' not in v: v = v + ".0"
    timestamp = timestamp_pb2.Timestamp()
    dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%f")
    timestamp.FromDatetime(dt)
    return timestamp

def _parse_naive_date_str(v):
    timestamp = timestamp_pb2.Timestamp()
    dt = datetime.strptime(v, "%Y-%m-%d")
    timestamp.FromDatetime(dt)
    return timestamp

def _yield_check(stack):
    """Checks for the presence of 'yield' in the calling code.
    Args:
        stack: The stack frame to check.
    """

    # Known issue with inspect.getmodule() and yield behavior in a frozen application.
    # When using inspect.getmodule() on stack frames obtained by inspect.stack(), it fails
    # to resolve the modules in a frozen application due to incompatible assumptions about
    # the file paths. This can lead to unexpected behavior, such as yield returning None or
    # the failure to retrieve the module inside a frozen app
    # (Reference: https://github.com/pyinstaller/pyinstaller/issues/5963)

    called_method = stack[0].function
    calling_code = stack[1].code_context[0]
    if f"{called_method}(" in calling_code:
        if 'yield' not in calling_code:
            print_library_log(
                f"Please add 'yield' to '{called_method}' operation on line {stack[1].lineno} in file '{stack[1].filename}'", Logging.Level.SEVERE)
            sys.exit(1)
    else:
        # This should never happen
        raise RuntimeError(
            f"The '{called_method}' function is missing in the connector calling code '{calling_code}'. Please ensure that the '{called_method}' function is properly defined in your code to proceed. Reference: https://fivetran.com/docs/connectors/connector-sdk/technical-reference#technicaldetailsmethods")
