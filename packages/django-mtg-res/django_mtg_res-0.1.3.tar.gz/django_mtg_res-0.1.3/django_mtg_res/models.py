from django.db import models
import requests
import logging
import json
import re
from django_mtg_res.utils import safe_clean_json_text
from django.http import HttpRequest, HttpResponse
from typing import Union, Optional


logger = logging.getLogger(__name__)


class RequestLog(models.Model):
    """
    This model is used to store request and response logs.
    It is used to store the request and response logs for the API.
    """

    # Save the request and response
    # fmt: off
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    method = models.CharField(max_length=255, null=True, blank=True)
    request = models.TextField(null=True, blank=True)  # request body
    response = models.TextField(null=True, blank=True)  # response body
    status_code = models.IntegerField(null=True, blank=True)
    remote_addr = models.CharField(max_length=255, null=True, blank=True)
    ref_obj = models.CharField(max_length=255, null=True, blank=True)
    ref_id = models.CharField(max_length=255, null=True, blank=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)

    # Timestamps
    created = models.DateTimeField(auto_now_add=True, editable=False, null=True)
    # fmt: on

    class Meta:
        db_table = "request_log"
        verbose_name = "Request Log"
        verbose_name_plural = "Request Logs"

    def __str__(self):
        return f"{self.method} {self.url} {self.remarks}"

    @classmethod
    def create_request_log(
        cls,
        response: Union[requests.Response, HttpResponse, dict, str, None] = None,
        url: Optional[str] = None,
        request: Union[
            requests.Request, requests.PreparedRequest, HttpRequest, dict, str, None
        ] = None,
        status_code: Optional[int] = None,
        method: Optional[str] = None,
        remote_addr: Optional[str] = None,
        ref_obj: Optional[str] = None,
        ref_id: Optional[str] = None,
        remarks: Optional[str] = None,
        safely_create: bool = True,  # if True, will skip if exception is raised
        max_body_size: int = 50000,  # Maximum size for request/response bodies
    ):
        """
        Create a request log entry with improved safety and validation.

        Args:
            response: Response object or data to log
            url: URL for the request
            request: Request object or data to log
            status_code: HTTP status code
            method: HTTP method
            remote_addr: Remote IP address
            ref_obj: Reference object name
            ref_id: Reference object ID
            remarks: Additional remarks
            safely_create: If True, will suppress exceptions
            max_body_size: Maximum size for request/response bodies (chars)
        """
        try:
            response_body = response

            # Process response object
            if isinstance(response_body, requests.Response):
                if request is None:
                    request = response_body.request
                if status_code is None:
                    status_code = response_body.status_code

                # Try to extract JSON, fallback to text
                try:
                    response_body = response_body.json()
                except (json.JSONDecodeError, ValueError):
                    # Try using safe_clean_json_text utility
                    response_body_safe = safe_clean_json_text(
                        response_body.text, fallback=None
                    )
                    response_body = (
                        response_body_safe
                        if response_body_safe is not None
                        else response_body.text
                    )

            elif isinstance(response_body, HttpResponse):
                # Fix: HttpResponse doesn't have a request attribute
                if status_code is None:
                    status_code = response_body.status_code
                # Handle both string and bytes content
                content = response_body.content
                if isinstance(content, bytes):
                    try:
                        response_body = content.decode("utf-8")
                    except UnicodeDecodeError:
                        response_body = content.decode("utf-8", errors="replace")
                else:
                    response_body = content

            # Process request object
            request_body = request
            if isinstance(request_body, (requests.Request, requests.PreparedRequest)):
                if method is None:
                    method = request_body.method
                if url is None:
                    url = request_body.url

            elif isinstance(request_body, HttpRequest):
                if method is None:
                    method = request_body.method
                if url is None:
                    url = request_body.get_full_path()
                if remote_addr is None:
                    remote_addr = cls._get_client_ip(request_body)

                # Handle request body
                try:
                    if hasattr(request_body, "body"):
                        body = request_body.body
                        if isinstance(body, bytes):
                            try:
                                request_body = body.decode("utf-8")
                            except UnicodeDecodeError:
                                request_body = body.decode("utf-8", errors="replace")
                        else:
                            request_body = body
                    else:
                        request_body = None
                except Exception as e:
                    logger.warning(f"Failed to get request body: {e}")
                    request_body = str(e)

            # Serialize dictionaries to JSON
            if isinstance(request_body, dict):
                try:
                    request_body = json.dumps(
                        request_body, default=str, ensure_ascii=False
                    )
                except (TypeError, ValueError) as e:
                    logger.warning(f"Failed to serialize request body to JSON: {e}")
                    request_body = str(request_body)

            if isinstance(response_body, dict):
                try:
                    response_body = json.dumps(
                        response_body, default=str, ensure_ascii=False
                    )
                except (TypeError, ValueError) as e:
                    logger.warning(f"Failed to serialize response body to JSON: {e}")
                    response_body = str(response_body)

            # Truncate large bodies and sanitize data
            request_body = cls._sanitize_and_truncate(request_body, max_body_size)
            response_body = cls._sanitize_and_truncate(response_body, max_body_size)

            # Validate field lengths
            url = cls._truncate_field(url, 255)
            method = cls._truncate_field(method, 255)
            remote_addr = cls._truncate_field(remote_addr, 255)
            ref_obj = cls._truncate_field(ref_obj, 255)
            ref_id = cls._truncate_field(ref_id, 255)
            remarks = cls._truncate_field(remarks, 255)

            logger.debug(
                f"Creating request log for [{method}] {url}. "
                f"ref_obj: {ref_obj} ref_id: {ref_id} remarks: {remarks}"
            )

            return cls.objects.create(
                url=url,
                method=method,
                request=request_body,
                response=response_body,
                status_code=status_code,
                remote_addr=remote_addr,
                ref_obj=ref_obj,
                ref_id=ref_id,
                remarks=remarks,
            )

        except Exception as e:
            logger.error(f"Error creating request log: {e}", exc_info=True)
            if safely_create:
                return None
            else:
                raise e

    @staticmethod
    def _get_client_ip(request: HttpRequest) -> Optional[str]:
        """
        Extract client IP address from request, handling proxy headers.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # Take the first IP in case of multiple proxies
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    @staticmethod
    def _sanitize_and_truncate(data: Optional[str], max_size: int) -> Optional[str]:
        """
        Sanitize and truncate data to prevent storage of sensitive information
        and limit size.
        """
        if not data:
            return data

        data_str = str(data)

        # Remove potential sensitive data patterns
        # This is a basic implementation - adjust patterns based on your needs
        sensitive_patterns = [
            (r'"password"\s*:\s*"[^"]*"', '"password": "[REDACTED]"'),
            (r'"token"\s*:\s*"[^"]*"', '"token": "[REDACTED]"'),
            (r'"api_key"\s*:\s*"[^"]*"', '"api_key": "[REDACTED]"'),
            (r'"secret"\s*:\s*"[^"]*"', '"secret": "[REDACTED]"'),
            (r"Authorization:\s*[^\s\n]+", "Authorization: [REDACTED]"),
        ]

        for pattern, replacement in sensitive_patterns:
            data_str = re.sub(pattern, replacement, data_str, flags=re.IGNORECASE)

        # Truncate if too long
        if len(data_str) > max_size:
            data_str = data_str[:max_size] + "\n... [TRUNCATED]"

        return data_str

    @staticmethod
    def _truncate_field(value: Optional[str], max_length: int) -> Optional[str]:
        """
        Truncate field value to fit database constraints.
        """
        if value and len(value) > max_length:
            return value[:max_length]
        return value
