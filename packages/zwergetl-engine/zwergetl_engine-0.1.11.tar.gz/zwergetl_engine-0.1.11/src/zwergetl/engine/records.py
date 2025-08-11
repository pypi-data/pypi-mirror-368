
class Record(object):
    """A helper class that allows reading and writing values to the
    internal list of values by name.
    """
    
    def __init__(self, metadata):
        """Inialize the record. param: metadata is a list of dicts
        where each dict contains field metadata.
        """
        self._values = None
        self._metadata = metadata
        # We need mapping field_name->field_index for fast access
        # to record values in the list (or array) of record values.
        self._names = dict()
        # metadata is a list of field definitions. Each field definition
        # is a dictionary of field's properties
        cnt = 0
        for field_def in metadata:
            field_name = field_def['name']
            self._names[field_name] = cnt
            cnt += 1

    def set_values(self, values):
        """
        Assign a new array of values to the instance's internal buffer.
        Values are not copied, only a reference to the array in 'values' param is stored.
        """
        self._values = values

    def get_values(self):
        """
        Get the underlying array of values
        :return: a reference to the array of values
        """
        return self._values

    def copy_from(self, source_record):
        """
        Copies values from all columns with corresponding names from source_record.
        If a column with corresponding name is not found in source_record,
        it is skipped, it's value is not changed and no error is returned.
        Data types are not checked nor converted, values are copied as is.
        """
        for name, index in self._names.items():
            source_index = source_record._names.get(name)
            if source_index is not None:
                self._values[index] = source_record._values[source_index]

    def __getitem__(self, key):
        if isinstance(key, str):
            col_num = self._names.get(key)
            if col_num is None:
                raise AttributeError("no record field {!r}".format(key))
            key = col_num
        return self._values[key]

    def __setitem__(self, key, value):
        if isinstance(key, str):
            col_num = self._names.get(key)
            if col_num is None:
                raise AttributeError("no record field {!r}".format(key))
            key = col_num
        self._values[key] = value

    def __getattr__(self, name):
        col_num = self._names.get(name)
        if col_num is None:
            raise AttributeError("no record field {!r}".format(name))
        return self._values[col_num]

    def __setattr__(self, name, value):
        if name in ['_names', '_values', '_metadata']:
            super().__setattr__(name, value)
        else:
            col_num = self._names.get(name)
            if col_num is None:
                raise AttributeError("no record field {!r}".format(name))
            self._values[col_num] = value
        
    def __len__(self):
        return len(self._values)
