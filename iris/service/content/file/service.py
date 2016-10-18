import magic
import uuid

from lovely.pyrest.rest import RestService, rpcmethod_route

from iris.service import rest
from iris.service.rest import queries
from iris.service.rest.swagger import swagger_reduce_response
from iris.service.security import acl

from .document import File
from .s3 import upload


@RestService("file_public_api")
class FilePublicRESTService(rest.RESTService):
    """The public file service API.

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


@RestService("file_admin_api",
             permission=acl.Permissions.AdminFull)
class FileAdminRESTService(FilePublicRESTService):
    """The admin file service API.
    """


class FileRESTMapper(rest.DocumentRESTMapperMixin,
                     rest.SearchableDocumentRESTMapperMixin,
                     rest.RESTMapper):
    """A mapper for the file REST API
    """

    NAME = 'files'

    DOC_CLASS = File

    QUERY_PARAMS = {
        'ft': queries.fulltextQuery(['original_name_ft'])
    }

    FILTER_PARAMS = {
        'state': queries.termsFilter('state'),
        'storage_type': queries.termsFilter('storage_type'),
        'content_type': queries.termsFilter('content_type'),
        'owner_id': queries.termsFilter('owner_id'),
    }

    SORT_PARAMS = {
        'created': queries.fieldSorter('dc.created'),
        'modified': queries.fieldSorter('dc.modified'),
        'id': queries.fieldSorter('id'),
        'state': queries.fieldSorter('state'),
        'original_name': queries.fieldSorter('original_name'),
        'owner_id': queries.fieldSorter('owner_id'),
        'storage_type': queries.fieldSorter('storage_type'),
        'content_type': queries.fieldSorter('content_type'),
    }
