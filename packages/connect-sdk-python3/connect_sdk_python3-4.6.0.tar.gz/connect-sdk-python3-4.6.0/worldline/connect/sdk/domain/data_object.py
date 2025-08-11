class DataObject(object):
    def to_dictionary(self) -> dict:
        return {}

    def from_dictionary(self, dictionary: dict) -> 'DataObject':
        if not isinstance(dictionary, dict):
            raise TypeError('value \'{}\' is not a dictionary'.format(dictionary))
        return self
