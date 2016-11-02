=======================
Document Transformation
=======================

Document transformation is used to transform a `Document` to a form which is
suitable for the API.

Prepare::

    >>> from iris.service.db import get_es

    >>> from lovely.esdb.properties import Property, LocalRelation
    >>> from lovely.esdb.document import Document
    >>> class TestDoc(Document):
    ...     INDEX = 'testdocs'
    ...     id = Property(primary_key=True)
    ...     more = Property()
    ...     other = LocalRelation('_relations.other', 'OtherDoc.id')
    ...     _relations = Property(name="relations", default=lambda: {})

    >>> class OtherDoc(Document):
    ...     INDEX = 'otherdocs'
    ...     id = Property(primary_key=True)
    ...     self_ref = LocalRelation('_relations.self_ref', 'OtherDoc.id')
    ...     _relations = Property(name="relations", default=lambda: {})

    >>> get_es().indices.create(
    ...     index=OtherDoc.INDEX,
    ...     body={
    ...         'settings': {'number_of_shards': 1},
    ...         "mappings" : {
    ...             OtherDoc.DOC_TYPE : {
    ...                 "properties" : {
    ...                     "id" : { "type" : "string", "index" : "not_analyzed" },
    ...                 }
    ...             }
    ...         }
    ...     })
    {u'acknowledged': True}


Transform To API Data
=====================

Transforms `Document` instances to simple python dicts with the possibility to
resolve relations. The result of the transformation is always JSON
serializable::

    >>> from iris.service.rest.transform import APITransformer


Document Transformation into JSON
---------------------------------

Simple transformation of the TestDoc::

    >>> doc = TestDoc(id=1, more={'info': 'text'})
    >>> transformer = APITransformer(doc)
    >>> print_json(transformer.to_api())
    {
      "id": 1,
      "more": {
        "info": "text"
      },
      "other": {
        "class": "OtherDoc",
        "id": null
      }
    }


Transformation With Resolved Relations
--------------------------------------

Relations can be resolved::

    >>> transformer = APITransformer(doc, resolve=['other'])
    >>> print_json(transformer.to_api())
    {
      "id": 1,
      "more": {
        "info": "text"
      },
      "other": {
        "class": "OtherDoc",
        "data": null,
        "id": null
      }
    }

Resolve with a referenced document. The relation now contains a `data`
property containing the related document::

    >>> other = OtherDoc(id=1)
    >>> _ = other.store()
    >>> doc.other = other
    >>> print_json(transformer.to_api())
    {
      "id": 1,
      "more": {
        "info": "text"
      },
      "other": {
        "class": "OtherDoc",
        "data": {
          "id": 1,
          "self_ref": {
            "class": "OtherDoc",
            "id": null
          }
        },
        "id": 1
      }
    }

It is possible to transform a list of documents::

    >>> doc2 = TestDoc(id=2)
    >>> other2 = OtherDoc(id=2)
    >>> _ = other2.store()
    >>> doc2.other = other2
    >>> transformer = APITransformer([doc, doc2])
    >>> print_json(transformer.to_api())
    [
      {
        "id": 1,
        "more": {
          "info": "text"
        },
        "other": {
          "class": "OtherDoc",
          "id": 1
        }
      },
      {
        "id": 2,
        "other": {
          "class": "OtherDoc",
          "id": 2
        }
      }
    ]

    >>> transformer = APITransformer([doc, doc2], resolve=['other'])
    >>> print_json(transformer.to_api())
    [
      {
        "id": 1,
        "more": {
          "info": "text"
        },
        "other": {
          "class": "OtherDoc",
          "data": {
            "id": 1,
            "self_ref": {
                "class": "OtherDoc",
                "id": null
            }
          },
          "id": 1
        }
      },
      {
        "id": 2,
        "other": {
          "class": "OtherDoc",
          "data": {
            "id": 2,
            "self_ref": {
                "class": "OtherDoc",
                "id": null
            }
          },
          "id": 2
        }
      }
    ]

With a reference to a document which is not stored::

    >>> other3 = OtherDoc(id=3)
    >>> doc2.other = other3
    >>> transformer = APITransformer(doc2, resolve=['other'])
    >>> print_json(transformer.to_api())
    {
      "id": 2,
      "other": {
        "class": "OtherDoc",
        "data": null,
        "id": 3
      }
    }


Resolve "deep" relations
------------------------

Create a doc referencing another doc::

    >>> other4 = OtherDoc(id=4)
    >>> _ = other4.store(refresh=True)
    >>> other2.self_ref = other4
    >>> _ = other2.store(refresh=True)
    >>> doc2.other = other2
    >>> transformer = APITransformer(doc2, resolve=['other.self_ref'])
    >>> print_json(transformer.to_api())
    {
      "id": 2,
      "other": {
        "class": "OtherDoc",
        "data": {
          "id": 2,
          "self_ref": {
            "class": "OtherDoc",
            "data": {
              "id": 4,
              "self_ref": {
                "class": "OtherDoc",
                "id": null
              }
            },
            "id": 4
          }
        },
        "id": 2
      }
    }

Build a relation loop::

    >>> other4.self_ref = other2
    >>> _ = other4.store(refresh=True)
    >>> transformer = APITransformer(doc2, resolve=['other.self_ref.self_ref'])
    >>> print_json(transformer.to_api())
    {
      "id": 2,
      "other": {
        "class": "OtherDoc",
        "data": {
          "id": 2,
          "self_ref": {
            "class": "OtherDoc",
            "data": {
              "id": 4,
              "self_ref": {
                "class": "OtherDoc",
                "data": {
                  "id": 2,
                  "self_ref": {
                    "class": "OtherDoc",
                    "id": 4
                  }
                },
                "id": 2
              }
            },
            "id": 4
          }
        },
        "id": 2
      }
    }
    >>> transformer = APITransformer(doc2, resolve=['other.self_ref.self_ref.self_ref'])
    >>> print_json(transformer.to_api())
    {
      "id": 2,
      "other": {
        "class": "OtherDoc",
        "data": {
          "id": 2,
          "self_ref": {
            "class": "OtherDoc",
            "data": {
              "id": 4,
              "self_ref": {
                "class": "OtherDoc",
                "data": {
                  "id": 2,
                  "self_ref": {
                    "class": "OtherDoc",
                    "data": {
                      "id": 4,
                      "self_ref": {
                        "class": "OtherDoc",
                        "id": 2
                      }
                    },
                    "id": 4
                  }
                },
                "id": 2
              }
            },
            "id": 4
          }
        },
        "id": 2
      }
    }
