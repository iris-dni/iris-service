===========
Swagger API
===========

The IRIS API is defined using `swagger <http://swagger.io>`_

This makes it easy to use the API.

`swagger-ui <http://swagger.io/swagger-ui/>`_ is available here `</swaggerui>`_


CORS
====

The API is fully CORS enabled.

.. note::

    Currently the API can be accessed from any external domain. This will be
    changed later to allow only specific domains to access the API.


Javascript API usage
====================

The package `swagger-js <https://github.com/swagger-api/swagger-js>`_ allows
to use a swagger enabled API to automatically create javascript object which
allow the use og the API.


Swagger Client API Module
-------------------------

A swagger api initialisation:

.. sourcecode:: javascript

    /**
    * Creates a swagger client from the provided swagger specification.
    * Once the client is ready, it is stored on the window object.
    * The provided callback is called in case of success and failure.
    *
    * @param {string} swaggerJsonUrl  URL to the swagger json specification.
    * @param {Function} callback  The callback that should be called when ready.
    */
    function initSwagger(swaggerJsonUrl, callback) {
      new Swagger({ url: swaggerJsonUrl, usePromise: true }).then(client => {
        window.__swaggerClient = client;
        callback();
      }).catch(reason => {
        callback();
      });
    }


Example use
-----------

Use the method to defer rendering of the react dom:

.. sourcecode:: javascript

    initSwagger('http://api-iris-dev.lovelysystems.com/swagger.json',
                function() {
                    React.DOM.render(
                        ...
                    );
                }
            )


.. note::

    Your code should check if the swagger client was created by checking if
    `window.__swaggerClient` exists.
