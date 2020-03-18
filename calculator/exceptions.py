class DocumentError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, "Document is not in required format")


class FinvizError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)
