import magic
import uuid

from pyramid import security

from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

from iris.service.endpoint import EndpointErrorMixin
from iris.service.errors import Errors

from .document import File, StorageType
from .s3 import upload, fetch


@RestService("blob_api")
class BlobRESTService(EndpointErrorMixin):
    """The blob service API.

    Allows upload and download of arbitrary files. Files are stored to and
    fetched from S3.
    """

    def __init__(self, request):
        self.request = request

    @rpcmethod_route(request_method='POST')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    def create_blob(self, data=None, **kwargs):
        if data is not None:
            content_type = magic.from_buffer(data.file.read(1024), mime=True)
            data.file.seek(0)
            iid = uuid.uuid4().hex
            success = upload(iid, data.file)
            if success:
                owner = self.request.user or self.request.session_user
                f = File(
                    id=iid,
                    state='visible',
                    original_name=data.filename,
                    owner_id=owner and owner.id,
                    storage_type=StorageType.S3,
                    content_type=content_type
                )
                f.store()
                return {
                    "status": "ok",
                    "data": {
                        "id": iid
                    }
                }
        return {"status": "failed"}

    @rpcmethod_route(route_suffix='/{contentId}')
    @rpcmethod_view(http_cache=86400,
                    permission=security.NO_PERMISSION_REQUIRED)
    def get(self, contentId):
        f = File.get(contentId)
        if f and f.storage_type == StorageType.S3:
            body = fetch(contentId)
            if body:
                response = self.request.response
                response.body_file.write(body.read())
                response.content_type = f.content_type.encode('ascii')
                return response
        raise self.not_found(
            Errors.document_not_found,
            {'contentId': contentId, 'mapperName': 'blob'}
        )

    @rpcmethod_route(request_method='OPTIONS')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    def options_event_generic(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/{contentId}')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    def options_event_generic_content_id(self, **kwargs):
        return {}
