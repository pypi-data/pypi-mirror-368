import os
import typing
import json
import io
import time
from pogodoc.client.client import PogodocApi
from pogodoc.utils import RenderConfig, upload_to_s3_with_url
from pogodoc.client.templates.types import SaveCreatedTemplateRequestPreviewIds, SaveCreatedTemplateRequestTemplateInfo, UpdateTemplateRequestPreviewIds, UpdateTemplateRequestTemplateInfo

class PogodocClient(PogodocApi):
    def __init__(self, token: str = None, base_url: str = None):
        """Initializes a new instance of the PogodocClient."""
        token = token or os.getenv("POGODOC_API_TOKEN")
        base_url = base_url or os.getenv("POGODOC_BASE_URL")

        if not token:
            raise ValueError("API token is required. Please provide it either as a parameter or set the API_TOKEN environment variable.")

        super().__init__(token=token, base_url=base_url)
   
    def save_template(self, path: str, template_info:SaveCreatedTemplateRequestTemplateInfo):
        """
        Saves a new template from a local file path.
        This method reads a template from a .zip file, uploads it, and saves it in Pogodoc.
        It is a convenient wrapper around `save_template_from_file_stream`.
        """
        zip = open(path, "rb")
        zip_length = os.path.getsize(path)
        return self.save_template_from_file_stream(payload=zip, payload_length=zip_length, template_info=template_info)
    
    def save_template_from_file_stream(self, payload:io.BufferedReader, payload_length:int, template_info:SaveCreatedTemplateRequestTemplateInfo):
        """
        Saves a new template from a file stream.
        This is the core method for creating templates. It uploads a template from a stream,
        generates previews, and saves it with the provided metadata.
        """
        init_response = self.templates.initialize_template_creation()

        template_id = init_response.template_id

        upload_to_s3_with_url(presigned_url=init_response.presigned_template_upload_url, payload=payload, payload_length=payload_length, content_type="application/zip")

        self.templates.extract_template_files(template_id)

        preview_response = self.templates.generate_template_previews(template_id,
            type=template_info.type,
            data=template_info.sample_data
        )

        self.templates.save_created_template(template_id, 
            template_info=template_info,
            preview_ids=SaveCreatedTemplateRequestPreviewIds(
                png_job_id=preview_response.png_preview.job_id,
                pdf_job_id=preview_response.pdf_preview.job_id
            )
        )

        return template_id
    
    def update_template(self, template_id: str, path: str, template_info:UpdateTemplateRequestTemplateInfo):
        """
        Updates an existing template from a local file path.
        This method reads a new version of a template from a .zip file, uploads it,
        and updates the existing template in Pogodoc.
        It is a convenient wrapper around `update_template_from_file_stream`.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Template file not found at path: {path}")

        zip = open(path, "rb")
        zip_length = os.path.getsize(path)

        return self.update_template_from_file_stream(
            template_id=template_id,
            payload=zip,
            payload_length=zip_length,
            template_info=template_info
        )

    def update_template_from_file_stream(self, template_id: str, payload:io.BufferedReader, payload_length:int, template_info:UpdateTemplateRequestTemplateInfo):
        """
        Updates an existing template from a file stream.
        This is the core method for updating templates. It uploads a new template version from a stream,
        generates new previews, and updates the template with the provided metadata.
        """
        init_response = self.templates.initialize_template_creation()
        content_id = init_response.template_id

        upload_to_s3_with_url(
            presigned_url=init_response.presigned_template_upload_url,
            payload=payload,
            payload_length=payload_length,
            content_type="application/zip"
        )

        self.templates.extract_template_files(content_id)

        preview_response = self.templates.generate_template_previews(
            template_id=content_id,
            type=template_info.type,
            data=template_info.sample_data
        )

        updated_template_response = self.templates.update_template(
            template_id=template_id,
            content_id=content_id,
            template_info=template_info,
            preview_ids= UpdateTemplateRequestPreviewIds(
                png_job_id=preview_response.png_preview.job_id,
                pdf_job_id=preview_response.pdf_preview.job_id
            )
        )
        return updated_template_response

    def generate_document(self, data: dict, render_config: RenderConfig, personal_upload_presigned_s3_url:typing.Optional[str] = None,  template: typing.Optional[str] = None, template_id: typing.Optional[str] = None):
        """
        Generates a document by starting a job and polling for its completion.
        This is the recommended method for most use cases, especially for larger documents or when you want a simple fire-and-forget operation.
        It first calls `start_generate_document` to begin the process, then `poll_for_job_completion` to wait for the result.
        You must provide either a `template_id` of a saved template or a `template` string.
        """
        job_id = self.start_generate_document(data, render_config, personal_upload_presigned_s3_url, template, template_id)
        return self.poll_for_job_completion(job_id)

    def start_generate_document(self, data: dict, render_config: RenderConfig, personal_upload_presigned_s3_url:typing.Optional[str] = None,  template: typing.Optional[str] = None, template_id: typing.Optional[str] = None):
        """
        Starts an asynchronous document generation job.
        This is a lower-level method that only initializes the job.
        You can use this if you want to implement your own polling logic.
        It returns the initial job status, which includes the `job_id`.
        Use `poll_for_job_completion` with the `job_id` to get the final result.
        You must provide either a `template_id` of a saved template or a `template` string.
        """

        render_options = {
            "type": render_config.type,
            "target": render_config.target,
        }
        if render_config.format_opts:
            render_options["format_opts"] = render_config.format_opts

        init_response = self.documents.initialize_render_job(
            data=data,
            template_id=template_id,
            **render_options
        )
        
        if data and init_response.presigned_data_upload_url:
            data_string = json.dumps(data)
            data_stream = io.BytesIO(data_string.encode('utf-8'))
            data_length = len(data_string)

            upload_to_s3_with_url(
                presigned_url=init_response.presigned_data_upload_url,
                payload=data_stream,
                payload_length=data_length,
                content_type="application/json"
            )

        if template and init_response.presigned_template_upload_url:
            upload_to_s3_with_url(
                presigned_url=init_response.presigned_template_upload_url,
                payload=io.BytesIO(template.encode('utf-8')),
                payload_length=len(template),
                content_type="text/html"
            )

        response = self.documents.start_render_job(
            job_id=init_response.job_id,
            upload_presigned_s_3_url=personal_upload_presigned_s3_url
        )

        return response.job_id
    
    
    def generate_document_immediate(self, data: dict, render_config: RenderConfig, template: typing.Optional[str] = None, template_id: typing.Optional[str] = None):
        """
        Generates a document and returns the result immediately.
        Use this method for quick, synchronous rendering of small documents.
        The result is returned directly in the response.
        For larger documents or when you need to handle rendering asynchronously, use `generate_document`.
        You must provide either a `template_id` of a saved template or a `template` string.
        """
        return self.documents.start_immediate_render(
            template_id=template_id,
            template=template,
            type=render_config.type,
            target=render_config.target,
            format_opts=render_config.format_opts,
            data=data,
        )
    
    def poll_for_job_completion(self, job_id: str, max_attempts: int = 60, interval_ms: int = 500):
        """
        Polls for the completion of a rendering job.
        This method repeatedly checks the status of a job until it is 'done'.
        """
        time.sleep(1)
        for attempt in range(max_attempts):
            job = self.documents.get_job_status(job_id)
            if job.status == "done":
                return job
            time.sleep(interval_ms / 1000)

        return self.documents.get_job_status(job_id)