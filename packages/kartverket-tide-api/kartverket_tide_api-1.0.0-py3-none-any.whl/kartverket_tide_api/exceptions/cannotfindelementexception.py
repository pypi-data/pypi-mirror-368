class CannotFindElementException(Exception):
    """Exception for when an xml element has been searcher for but cannot be found"""
    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "CannotFindElementException: status={}".format(self.status)