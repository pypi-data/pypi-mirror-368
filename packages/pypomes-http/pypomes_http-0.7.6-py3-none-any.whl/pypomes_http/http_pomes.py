
from base64 import b64encode
from flask import Request, Response, jsonify
from pypomes_core import validate_format_errors
from typing import Any
from werkzeug.datastructures import FileStorage


def http_retrieve_parameters(url: str) -> dict[str, str]:
    """
    Retrieve the parameters in the query string of *url*.

    :param url: the url to retrieve parameters from
    :return: the extracted parameters, or an empty *dict* if no parameters were found
    """
    # initialize the return variable
    result: dict[str, str] = {}

    # retrieve the parameters
    pos: int = url.find("?")
    if pos > 0:
        params: list[str] = url[pos + 1:].split(sep="&")
        for param in params:
            key: str = param.split("=")[0]
            value: str = param.split("=")[1]
            result[key] = value

    return result


def http_get_parameter(request: Request,
                       param: str,
                       sources: tuple = None) -> Any:
    """
    Obtain the *request*'s input parameter named *param*.

    The following origins are inspected, in the sequence defined by *sources*, defaulting to:
      - *body*: key/value pairs in a *JSON* structure in the request's body
      - *form*: data elements in a HTML form
      - *query*: parameters in the URL's query string

    The first occurrence of *param* found is returned. If *sources* is provided, only the
    origins specified therein (*body*, *form*, and *query*) are inspected.

    :param request: the *Request* object
    :param sources: the sequence of origins to inspect (defaults to *['body', 'form', 'query']*)
    :param param: name of parameter to retrieve
    :return: the parameter's value, or *None* if not found
    """
    params: dict[str, Any] = http_get_parameters(request=request,
                                                 sources=sources)
    return (params or {}).get(param)


def http_get_parameters(request: Request,
                        sources: tuple = None) -> Any:
    """
    Obtain the *request*'s input parameters.

    The following origins are inspected, in the sequence defined by *sources*, defaulting to:
      - *body*: key/value pairs in a *JSON* structure in the request's body
      - *form*: data elements in a HTML form
      - *query*: parameters in the URL's query string

    The first occurrence of each parameter found is returned. If *sources* is provided, only the
    origins specified therein (*body*, *form*, and *query*) are inspected.

    :param request: the *Request* object
    :param sources: the sequence of origins to inspect (defaults to *['body', 'form', 'query']*)
    :return: *dict* containing the input parameters (empty *dict*, if no input data exists)
    """
    # initialize the return variable
    result: dict[str, Any] = {}

    for source in reversed(sources or ("body", "form", "query")):
        match source:
            case "query":
                # retrieve parameters from URL query
                result.update(request.values)
            case "body":
                # retrieve parameters from JSON data in body
                if request.is_json:
                    result.update(request.get_json())
            case "form":
                # obtain parameters from form
                result.update(request.form)

    return result


def http_basic_auth_header(uname: str,
                           pwd: str,
                           header: dict[str, Any] = None) -> dict[str, Any]:
    """
    Add to *header* the HTTP Basic Authorization snippet.

    If *header* is not provided, a new *dict* is created.
    For convenience, the modified, or newly created, *dict* is returned.

    :param uname: the username to use
    :param pwd: the password to use
    :param header: the optional header to add the Basic Authorization to
    :return: header with Basic Authorization data
    """
    # initialize the return variable
    result: dict[str, Any] = header or {}

    enc_bytes: bytes = b64encode(f"{uname}:{pwd}".encode())
    result["Authorization"] = f"Basic {enc_bytes.decode()}"

    return result


def http_bearer_auth_header(token: str | bytes,
                            header: dict[str, Any] = None) -> dict[str, Any]:
    """
    Add to *header* the HTTP Bearer Authorization snippet.

    If *header* is not provided, a new *dict* is created.
    For convenience, the modified, or newly created, *dict* is returned.

    :param token: the token to use
    :param header: the optional header to add the Bearer Authorization to
    :return: header with Basic Authorization data
    """
    # initialize the return variable
    result: dict[str, Any] = header or {}

    if isinstance(token, bytes):
        token = token.decode()
    result["Authorization"] = f"Bearer {token}"

    return result


def http_get_file(request: Request,
                  file_name: str = None,
                  file_seq: int = 0) -> bytes:
    """
    Retrieve the contents of the file returned in the response to a request.

    The file may be referred to by its name (*file_name*), or if no name is specified,
    by its sequence number (*file_seq*).

    :param request: the request
    :param file_name: optional name for the file
    :param file_seq: sequence number for the file, defaults to the first file
    :return: the contents retrieved from the file
    """
    # inicialize the return variable
    result: bytes | None = None

    count: int = len(request.files) \
        if hasattr(request, "files") and request.files else 0
    # has a file been found ?
    if count > 0:
        # yes, retrieve it
        file: FileStorage | None = None
        if isinstance(file_name, str):
            file = request.files.get(file_name)
        elif (isinstance(file_seq, int) and
              len(request.files) > file_seq >= 0):
            file_in: str = list(request.files)[file_seq]
            file = request.files[file_in]

        if file:
            result: bytes = file.stream.read()

    return result


def http_build_response(errors: list[str],
                        reply: dict[str, Any]) -> Response:
    """
    Build a *Response* object based on the given *errors* list and the set of key/value pairs in *reply*.

    :param errors: the reference errors
    :param reply: the key/value pairs to add to the response as JSON string
    :return: the appropriate *Response* object
    """
    # declare the return variable
    result: Response

    if len(errors) == 0:
        # 'reply' might be 'None'
        result = jsonify(reply)
    else:
        reply_err: dict = {"errors": validate_format_errors(errors=errors)}
        if isinstance(reply, dict):
            reply_err.update(reply)
        result = jsonify(reply_err)
        result.status_code = 400

    return result
