import magic
import uuid

from lovely.pyrest.rest import RestService, rpcmethod_route

from iris.service import rest
from iris.service.rest.swagger import swagger_reduce_response

from .document import File
from .s3 import upload


@RestService("file_api")
class FileRESTService(rest.RESTService):
    """The file service API.

    Allows upload and download of arbitrary files. Files are stored to and
    fetched from S3.
    """

    MAPPER_NAME = 'files'

    @rpcmethod_route(request_method='POST')
    @swagger_reduce_response
    def create(self, data=None, **kwargs):
        data = self.upload_file(data)
        if data:
            res = self.create_content(self.MAPPER_NAME, {"data": data})
            if res:
                res['status'] = "ok"
                return res
        return {"status": "failed"}

    def upload_file(self, data):
        """Upload the file to S3.
        """
        if data is not None:
            content_type = magic.from_buffer(data.file.read(1024), mime=True)
            data.file.seek(0)
            iid = uuid.uuid4().hex
            storage_type = upload(iid, data.file)
            if storage_type:
                owner = self.request.user or self.request.session_user
                return {
                    "id": iid,
                    "state": "visible",
                    "original_name": data.filename,
                    "owner_id": owner and owner.id,
                    "storage_type": storage_type,
                    "content_type": content_type
                }


class FileRESTMapper(rest.DocumentRESTMapperMixin,
                     rest.RESTMapper):
    """A mapper for the file REST API
    """

    NAME = 'files'

    DOC_CLASS = File
