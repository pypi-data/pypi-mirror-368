from django.db import models
import requests
import logging
import json
from django_mtg_res.utils import safe_clean_json_text


logger = logging.getLogger(__name__)


class RequestLog(models.Model):
    """
    This model is used to store request and response logs.
    It is used to store the request and response logs for the API.
    """

    # Save the request and response
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    method = models.CharField(max_length=255, null=True, blank=True)
    request = models.TextField(null=True, blank=True)  # request body
    response = models.TextField(null=True, blank=True)  # response body
    status_code = models.IntegerField(null=True, blank=True)
    ref_obj = models.CharField(max_length=255, null=True, blank=True)
    ref_id = models.CharField(max_length=255, null=True, blank=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)

    # Timestamps
    created = models.DateTimeField(auto_now_add=True, editable=False, null=True)

    class Meta:
        db_table = "request_log"
        verbose_name = "Request Log"
        verbose_name_plural = "Request Logs"

    def __str__(self):
        return f"{self.method} {self.url} {self.remarks}"

    @classmethod
    def create_request_log(
        cls,
        response: requests.Response | dict | str | None = None,
        url: str | None = None,
        request: requests.Request | requests.PreparedRequest | dict | str | None = None,
        status_code: int | None = None,
        method: str | None = None,
        ref_obj: str | None = None,
        ref_id: str | None = None,
        remarks: str | None = None,
        safely_create: bool = True,  # if True, will skip if exception is raised
    ):
        """
        Easiest way is to pass in the response object, and the request object will be extracted from the response object
        """
        try:
            response_body = response
            if isinstance(response_body, requests.Response):
                if request == None:
                    request = response_body.request
                if status_code == None:
                    status_code = response_body.status_code
                try:
                    response_body = response_body.json()
                except Exception as e:
                    # try use safe_clean_json_text
                    response_body = safe_clean_json_text(
                        response_body.text, fallback=None
                    )
                    if response_body == None:
                        response_body = response_body.text

            request_body = request
            if isinstance(request_body, (requests.Request, requests.PreparedRequest)):
                if method == None:
                    method = request_body.method
                if url == None:
                    url = request_body.url

                request_body = request_body.body

            if isinstance(request_body, dict):
                request_body = json.dumps(request_body)

            if isinstance(response_body, dict):
                response_body = json.dumps(response_body)

            logger.info(
                f"Creating request log to [{method}] {url}. ref_obj: {ref_obj} ref_id: {ref_id} remarks: {remarks}"
            )

            cls.objects.create(
                url=url,
                method=method,
                request=request_body,
                response=response_body,
                status_code=status_code,
                ref_obj=ref_obj,
                ref_id=ref_id,
                remarks=remarks,
            )
        except Exception as e:
            logger.error(f"Error creating request log: {e}")
            if safely_create:
                return
            else:
                raise e
