
from bagpy import bagreader
from rosbag.bag import BagMessage
import rosbag
import pandas as pd
from io import StringIO
import pathlib
import os, io


"""
Utility functions for working with ROS bags in memory.
This module provides a subclass of `bagreader` that allows for
message extraction without writing to disk, suitable for cloud environments.
This is particularly useful for environments like AWS Lambda where
disk I/O can be slow or limited.
This module is designed to work with ROS bags and provides methods
to extract messages by topic, convert them to pandas DataFrames,
and return them as CSV strings or bytes for easy upload to cloud storage.
"""


class NamedBytesIO(io.BytesIO):
    def __init__(self, data: bytes, name: str = "memory.bag", mode: str = "rb"):
        super().__init__(data)
        self.name = name
        self.mode = mode  # rosbag expects this when given a file-like


def slotvalues(m: BagMessage, slot: str):
    """
    Helper function to extract values and column names from message slots.
    Parameters
    ----------
    m : BagMessage
        The ROS bag message object.
    slot : str
        The slot name to extract values from.
    Returns
    -------
    tuple
        A tuple containing the values and the corresponding slot names.
    Raises
    ------
    AttributeError
        If the slot does not exist in the message.
    """
    vals = getattr(m, slot)
    try:
        slots = vals.__slots__
        varray = []
        sarray = []
        for s in slots:
            vnew, snew = slotvalues(vals, s)       
            if isinstance(snew, list):
                for i, snn in enumerate(snew):
                    sarray.append(slot + '.' + snn)
                    varray.append(vnew[i])
            elif isinstance(snew, str):
                sarray.append(slot + '.' + snew)
                varray.append(vnew)    
                
        return varray, sarray
    except AttributeError:
        return vals, slot

class MemoryBagReader(bagreader):
    """
    Subclass of bagreader that supports reading from a path or in-memory bytes.
    """
    def __init__(self, bagfile, delimiter: str = ",", verbose: bool = False):
        self.delimiter = delimiter
        self.verbose = verbose

        self._buf = None   # keep strong ref if using in-memory file
        self.bagfile = bagfile

        # -------- Path-like input --------
        if isinstance(bagfile, (str, os.PathLike)):
            path = pathlib.Path(bagfile)
            self.filename = path.name
            self.dir = str(path.parent) or "./"
            open_arg = str(path)
            self.reader = rosbag.Bag(open_arg, mode='r')

        # -------- File-like / bytes input --------
        else:
            # Normalize to a BytesIO
            if isinstance(bagfile, (bytes, bytearray, memoryview)):
                buf = NamedBytesIO(bytes(bagfile))
            else:
                buf = bagfile  # assume file-like object

            # Give it a name if missing (best-effort)
            if not hasattr(buf, "name"):
                try:
                    buf.name = "memory.bag"  # type: ignore[attr-defined]
                except Exception:
                    pass

            self._buf = buf
            self._buf.seek(0)  # IMPORTANT: rewind after any prior use

            self.filename = getattr(self._buf, "name", "memory.bag")
            self.dir = "./"

            # Let rosbag scan without relying on on-disk index
            self.reader = rosbag.Bag(self._buf, mode='r',
                                     allow_unindexed=True, skip_index=True)

        # ---- rest unchanged ----
        info = self.reader.get_type_and_topic_info()
        self.topic_tuple = info.topics.values()
        self.topics = list(info.topics.keys())

        self.message_types = [t.msg_type for t in self.topic_tuple]
        self.n_messages    = [t.message_count for t in self.topic_tuple]
        self.frequency     = [t.frequency for t in self.topic_tuple]

        self.topic_table = pd.DataFrame(
            list(zip(self.topics, self.message_types, self.n_messages, self.frequency)),
            columns=['Topics', 'Types', 'Message Count', 'Frequency']
        )

        self.start_time = self.reader.get_start_time()
        self.end_time   = self.reader.get_end_time()

        # For path inputs, derive a datafolder; for streams, use a safe default
        if isinstance(bagfile, (str, os.PathLike)):
            stem = pathlib.Path(bagfile).with_suffix('')  # drop .bag
            self.datafolder = str(stem)
        else:
            self.datafolder = "./memory_bag"

        if self.verbose:
            print(f"[INFO] MemoryBagReader initialized for {self.filename!r} (dir={self.dir})")

    
    def message_by_topic_memory(self, topic: str) -> pd.DataFrame:
        """
        Extract messages from ROS bag by topic name without writing to disk.
        Returns a pandas DataFrame directly.
        
        This method closely follows the logic from the original bagreader.message_by_topic
        but creates a DataFrame directly instead of writing to CSV.
        
        Parameters
        ----------
        topic : str
            Topic from which to extract messages.
            
        Returns
        -------
        pandas.DataFrame
            DataFrame containing the extracted message data.
        """
        msg_list = []
        tstart = None
        tend = None
        time = []
        
        for topic_name, msg, t in self.reader.read_messages(topics=topic, start_time=tstart, end_time=tend):
            time.append(t)
            msg_list.append(msg)

        msgs = msg_list

        if len(msgs) == 0:
            if self.verbose:
                print(f"No data on the topic: {topic}")
            return pd.DataFrame()

        # Set column names from the slots - using the same logic as original bagreader
        cols = ["Time"]
        m0 = msgs[0]
        slots = m0.__slots__
        for s in slots:
            v, s_names = slotvalues(m0, s)
            if isinstance(v, tuple):
                snew_array = [] 
                p = list(range(0, len(v)))
                snew_array = [s_names + "_" + str(pelem) for pelem in p]
                s_names = snew_array
            
            if isinstance(s_names, list):
                for i, s1 in enumerate(s_names):
                    cols.append(s1)
            else:
                cols.append(s_names)
        
        # Create data rows - using the same logic as original bagreader
        data_rows = []
        for i, m in enumerate(msgs):
            slots = m.__slots__
            vals = []
            vals.append(time[i].secs + time[i].nsecs*1e-9)
            for s in slots:
                v, s_names = slotvalues(m, s)
                if isinstance(v, tuple):
                    snew_array = [] 
                    p = list(range(0, len(v)))
                    snew_array = [s_names + "_" + str(pelem) for pelem in p]
                    s_names = snew_array

                if isinstance(s_names, list):
                    for j, s1 in enumerate(s_names):
                        vals.append(v[j])
                else:
                    vals.append(v)
            data_rows.append(vals)
        
        # Create DataFrame directly
        df = pd.DataFrame(data_rows, columns=cols)
        return df
    
    def message_by_topic_csv_memory(self, topic: str) -> str:
        """
        Extract messages and return as CSV string in memory.
        
        Parameters
        ----------
        topic : str
            Topic from which to extract messages.
            
        Returns
        -------
        str
            CSV string representation of the data.
        """
        df = self.message_by_topic_memory(topic)
        if df.empty:
            return ""
        
        # Convert to CSV string
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False, sep=self.delimiter)
        return csv_buffer.getvalue()
    
    def message_by_topic_bytes(self, topic: str) -> bytes:
        """
        Extract messages and return as bytes (for S3 upload).
        
        Parameters
        ----------
        topic : str
            Topic from which to extract messages.
            
        Returns
        -------
        bytes
            CSV data as bytes.
        """
        csv_string = self.message_by_topic_csv_memory(topic)
        return csv_string.encode('utf-8')
    
    def close(self):
        """Close the bag reader."""
        if hasattr(self, 'reader'):
            self.reader.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()