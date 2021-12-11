class Status:
    """The Status type defines a logical error model that is suitable for different programming environments,
    including REST APIs and RPC APIs. It is used by gRPC. Each Status message contains three pieces of data: error
    code, error message, and error details.

    See https://developers.google.com/photos/library/reference/rest/v1/Status for more information.
    """

    # The status code, which should be an enum value of google.rpc.Code.
    code: int

    # A developer-facing error message, which should be in English. Any user-facing error message should be localized
    # and sent in the google.rpc.Status.details field, or localized by the client.
    message: str

    # A list of messages that carry the error details. There is a common set of message types for APIs to use.
    #
    # An object containing fields of an arbitrary type. An additional field "@type" contains a URI identifying the
    # type. Example: { "id": 1234, "@type": "types.example.com/standard/id" }.
    details: dict

    def __init__(self, status: dict):
        self.code = int(status['code'])
        self.message = str(status['message'])
        self.details = dict(status['details'])

