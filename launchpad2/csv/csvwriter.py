import csv


class WriterException(Exception):
    pass


class CSVFormatterWriter(object):
    def __init__(self, filename, headers, attribute_names):
        self.filename = filename
        self.headers = headers
        self.attributes = attribute_names
        self._fd = None
        self._writer = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *ex_args):
        self.close()

        # If there was an exception for any reason, just let Python re-raise
        # it for us
        if any(ex_args):
            return False

    def open(self):
        if self._fd is None and self._writer is None:
            self._fd = open(self.filename, 'w')
            self._writer = csv.writer(self._fd)
            self._writer.writerow(self.headers)

    def close(self):
        self._writer = None
        if self._fd is not None:
            self._fd.close()
            self._fd = None

    def record_bug(self, bug):
        if not self._writer:
            raise WriterException(
                'CSVFormatterWritter was not opened before trying to save a'
                ' bug as CSV'
            )
        row = [bug.get(attribute, '') for attribute in self.attributes]
        self._writer.writerow(row)
