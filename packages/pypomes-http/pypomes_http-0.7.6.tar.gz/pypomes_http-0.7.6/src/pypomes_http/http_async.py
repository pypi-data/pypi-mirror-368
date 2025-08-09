import base64
import json
import threading
from collections.abc import Callable
from datetime import datetime
from logging import Logger
from pypomes_core import TZ_LOCAL
from requests import Response
from typing import Any

from .http_methods import HttpMethod, http_rest


class HttpAsync(threading.Thread):
    """
    Asynchronous invocation of a *REST* service.

    This invocation is done with Python's *request* and the method specified in *job_method*.
    """

    def __init__(self,
                 job_name: str,
                 job_url: str,
                 job_method: HttpMethod,
                 jwt_provider: callable = None,
                 callback: Callable[[dict[str, Any]], None] = None,
                 report_content: bool = False,
                 headers: dict[str, Any] = None,
                 params: dict[str, Any] = None,
                 data: dict[str, Any] = None,
                 json: dict[str, Any] = None,
                 timeout: float = None,
                 logger: Logger = None) -> None:
        """
        Initiate the asychronous invocation of the *REST* service.

        If a *jwt_provider* is specified, a JWT authorization token is requested prior to invoking the service.
        If a *callback* is specified, it will be sent the results of the job invocaton, in *JSON* format.
        This is the structure of the results sent:
        {
            "job-name": "<str>"            -- the name given for the job
            "start": "<iso-date>",         -- timestamp of invocation start (ISO format)
            "finish": "<iso-date>",        -- timestamp of invocation finish (ISO format)
            "errors": "<errors-reported>"  -- errors returned by the service, if applicable
            "content": "<bytes-in-BASE64>" -- Base64-wrapped contents of the response
        }

        :param job_name: the name of the job being invoked
        :param job_url: the job's URL
        :param job_method: the HTTP method to use (DELETE, GET, HEAD, PATCH, POST, PUT)
        :param callback: the function to call on job termination
        :param jwt_provider: option JWT token provider
        :param report_content: whether to report the response's content to callback
        :param headers: optional headers
        :param params: optional parameters
        :param timeout: timeout, in seconds (defaults to None)
        :param logger: optional logger
        """
        threading.Thread.__init__(self)

        # instance attributes
        self.job_name: str = job_name
        self.job_url: str = job_url
        self.job_method: HttpMethod = job_method
        self.callback: Callable[[dict[str, Any]], None] = callback
        self.jwt_provider: callable = jwt_provider
        self.report_content: bool = report_content
        self.headers: dict[str, Any] = headers
        self.params: dict[str, Any] = params
        self.data: dict[str, Any] = data
        self.json: dict[str, Any] = json
        self.timeout: float = timeout
        self.logger: Logger = logger

        self.start_timestamp: str | None = None
        self.finish_timestamp: str | None = None

        if self.logger:
            self.logger.debug(msg=f"Job '{job_name}' instantiated, with URL '{job_url}'")

    def run(self) -> None:
        """
        Invoke the *REST* service.
        """
        # initialize the errors list
        errors: list[str] = []

        # log the operation start
        if self.logger:
            self.logger.info(msg=f"Job '{self.job_name}' started")

        # obtain the start timestamp
        self.start_timestamp = datetime.now(tz=TZ_LOCAL).isoformat()

        # obtain the JWT token
        if self.jwt_provider:
            jwt_token: str = self.jwt_provider(self.job_name)
            if jwt_token:
                if not self.headers:
                    self.headers = {}
                self.headers["Authorization"] = f"Bearer {jwt_token}"

        # invoke the service
        response: Response = http_rest(errors=errors,
                                       method=self.job_method,
                                       url=self.job_url,
                                       headers=self.headers,
                                       params=self.params,
                                       data=self.data,
                                       json=self.json,
                                       timeout=self.timeout,
                                       logger=self.logger)
        # obtain the finish timestamp
        self.finish_timestamp = datetime.now(tz=TZ_LOCAL).isoformat()

        # log the opertion finish
        if self.logger:
            self.logger.info(msg=f"Job '{self.job_name}' finished")

        # foward the results of the service invocation
        if self.callback:
            reply: dict[str, Any] = {
                "job-name": self.job_name,
                "job-url": self.job_url,
                "start": self.start_timestamp,
                "finish": self.finish_timestamp,
            }
            # report the errors messages
            if errors:
                reply["errors"] = json.dumps(obj=errors,
                                             ensure_ascii=False)
            # report the response's content
            if (self.report_content and
                    response is not None and
                    hasattr(response, "content") and
                    isinstance(response.content, bytes)):
                reply["content"] = base64.b64encode(s=response.content).decode()
            self.callback(reply)
