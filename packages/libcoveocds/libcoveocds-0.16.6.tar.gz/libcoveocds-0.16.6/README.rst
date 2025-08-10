Lib CoVE OCDS
=============

|PyPI Version| |Build Status| |Coverage Status| |Python Version|

.. |PyPI Version| image:: https://img.shields.io/pypi/v/libcoveocds.svg
   :target: https://pypi.org/project/libcoveocds/
.. |Build Status| image:: https://github.com/open-contracting/lib-cove-ocds/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/open-contracting/lib-cove-ocds/actions/workflows/ci.yml
.. |Coverage Status| image:: https://coveralls.io/repos/github/open-contracting/lib-cove-ocds/badge.svg?branch=main
   :target: https://coveralls.io/github/open-contracting/lib-cove-ocds?branch=main
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/libcoveocds.svg
   :target: https://pypi.org/project/libcoveocds/

Command line
------------

Call ``libcoveocds`` and pass the filename of some JSON data.

::

   libcoveocds tests/fixtures/common_checks/basic_1.json

It will produce JSON data of the results to standard output. You can pipe this straight into a file to work with.

You can also pass ``--schema-version 1.X`` to force it to check against a certain version of the schema.

In some modes, it will also leave directory of data behind. The following options apply to this mode:

* Pass ``--convert`` to get it to produce spreadsheets of the data.
* Pass ``--output-dir output`` to specify a directory name (default is a name based on the filename).
* Pass ``--delete`` to delete the output directory if it already exists (default is to error)
* Pass ``--exclude-file`` to avoid copying the original file into the output directory (default is to copy)

(If none of these are specified, it will not leave any files behind)

Library
-------

To use this as a Python library as part of a Python script for validating multiple files or testing, you need to:

1. Install the library with pip:

   .. code-block:: bash

      pip install libcoveocds

   If using the library in a web context, install as:

   .. code-block:: bash

      pip install libcoveocds[web]

2. Use it in your Python code, for example:

   .. code-block:: python

      import os
      import shutil
      import tempfile

      from libcoveocds.api import ocds_json_output


      data_directory = "path/to/your/directory/with/json/files"
      temporary_directory = tempfile.mkdtemp(dir=tempfile.gettempdir())

      for filename in os.listdir(data_directory):
          path = os.path.join(data_directory, filename)
          try:
              result = ocds_json_output(temporary_directory, path, file_type="json")
         finally:
             shutil.rmtree(temporary_directory)

          # Do something with the result. For example:
          if result["validation_errors"]:
              for error in result["validation_errors"]:
                  print(f"Validation error {error} found in {path}")
          else:
              print(f"No validation errors found for {path}")

Code for use by external users
------------------------------

The only code that should be used directly by users is the ``libcoveocds.config`` and ``libcoveocds.api`` modules.

Other code (in ``libcore``, ``lib``, etc.) should not be used by external users of this library directly, as the structure and use of these may change more frequently.

Output JSON format
------------------

The output is an object with the following properties:

===================================== ===================== ==============
Property (key) name		      Type                  Value
===================================== ===================== ==============
``file_type``                         string                The type of the file supplied, one of ``json``, ``csv``, ``xlsx`` or ``ods``
``version_used``                      string                The version of the OCDS schemas used, e.g. ``1.1`` (This is ``1.0`` when no version fields exists)
``schema_url``                        string                The URL to the package schema used, e.g. ``https://standard.open-contracting.org/1.1/en/release-package-schema.json``
``extensions``                        object                An extensions_ object
``validation_errors``                 array[object]         An array of validation_errors_ objects
``common_error_types``                array[]               Always an empty array
``deprecated_fields``                 array[object]         An array of deprecated_fields_ objects
``releases_aggregates``               object                A releases_aggregates_ object
``records_aggregates``                object                A records_aggregates_ object
``additional_closed_codelist_values`` object                A mapping from a codelist field's JSON Pointer (with array indices removed, e.g. ``releases/tender/documents/documentType``) to an `additional codelist object`_
``additional_open_codelist_values``   object                A mapping from a codelist field's JSON Pointer (with array indices removed, e.g. ``releases/tender/documents/documentType``) to an `additional codelist object`_
``additional_checks``                 object                A mapping from an additional check type (currently only ``empty_field``) to an array of `additional check objects <additional check object_>`_
``conformance_errors``                object                A conformance_errors_ object
``additional_fields``                 array[object]         The top-level additional fields, as an array of additional_fields_ objects
``all_additional_fields``             array[object]         All additional fields, including children of other additional fields, as an array of all_additional_fields_ objects
``json_deref_error``                  string                An exception message for an unresolvable reference (if raised)
===================================== ===================== ==============

Note that wherever a schema is used, it is the extended schema (if extensions exist).

extensions
^^^^^^^^^^

============================= ===================== ==============
Property (key) name	      Type                  Value
============================= ===================== ==============
``extensions``                array[object]         An `extensions/extensions`_ object
``invalid_extensions``        array[array[string]]  An array of pairs of an extension URL and a human-readable error message, e.g. ``[["http://etc", "404: not found"]]``
``extended_schema_url``       string                The file the extended schema will be written to, if an output directory has been set, e.g. ``extended_schema.json``           
``is_extended_schema``        boolean               Has the schema been extended?
============================= ===================== ==============

extensions/extensions
^^^^^^^^^^^^^^^^^^^^^

======================= =============== ============
Property (key) name     Type            Value
======================= =============== ============
``url``                 string          The URL of the extension's metadata file, e.g. ``https://raw.githubusercontent.com/open-contracting-extensions/ocds_metrics_extension/master/extension.json``
``schema_url``          string          The URL of the extension's release schema file, e.g. ``https://raw.githubusercontent.com/open-contracting-extensions/ocds_metrics_extension/master/release-schema.json``
``description``         string          Extracted from the metadata file
``name``                string          Extracted from the metadata file
``documentationUrl``    string          Extracted from the metadata file
``failed_codelists``    object          A mapping from an extended codelist name (prefixed with ``+`` or ``-`` if appropriate) to a human-readable error message
``codelists``           array[string]   Extracted from the metadata file
======================= =============== ============

validation_errors
^^^^^^^^^^^^^^^^^

Note that this list will exclude codelist errors, which instead appear in ``additional_closed_codelist_values``.

lib-cove-ocds uses the ``jsonschema`` module's ``uniqueItems`` validator to check for unique OCIDs and IDs.

======================= =========== ========
Property (key) name     Type        Value
======================= =========== ========
``type``                string      The JSON Schema keyword that caused the validation error, e.g. ``minLength`` (`full list in the jsonschema lib <https://github.com/Julian/jsonschema/blob/9b6a9f5/jsonschema/validators.py#L321-L345>`_), unless the keyword is ``type`` or ``format``, in which case this is the relevant `type <https://datatracker.ietf.org/doc/html/draft-zyp-json-schema-04#section-3.5>`_ or `format <https://datatracker.ietf.org/doc/html/draft-fge-json-schema-validation-00#section-7.3>`_, e.g. ``array`` or ``date-time``
``field``               string      The JSON Pointer to the erroneous data, with array indices removed, e.g. ``releases/tender/items``
``description``         string      A human-readable error message, e.g. ``'id' is missing but required within 'items'``
``path``                string      The JSON Pointer to the erroneous data, e.g. ``releases/0/tender/items/0``
``value``               any         The value in the data that was erroneous, or ``""`` if not applicable
======================= =========== ========

deprecated_fields
^^^^^^^^^^^^^^^^^

======================================= =========================== ==============
Property (key) name	                Type                        Value
======================================= =========================== ==============
``paths``                               array[string]               An array of JSON Pointers to parent objects containing deprecated fields, e.g. ``["releases/0/tender"]``
``explanation``                         array[string]               A pair of the version in which the field was deprecated, and the human-readable deprecation message, e.g. ``["1.1", "Some explanation text"]``
``field``                               string                      The name of the field within the parent object that is deprecated, e.g. ``amendment``
======================================= =========================== ==============

releases_aggregates
^^^^^^^^^^^^^^^^^^^

======================================= =========================== ==============
Property (key) name	                Type                        Value
======================================= =========================== ==============
``release_count``                       integer                     The number of items in the releases array 
``unique_ocids``                        array*                      An array of all ocids, deduplicated
``unique_initation_type``               array*
``duplicate_release_ids``               array*                      **This is an OCDS implementation error.**
``tags``                                object
``unique_lang``                         array*
``unique_award_id``                     array*
``planning_count``                      integer
``tender_count``                        integer
``award_count``                         integer
``processes_award_count``               integer
``contract_count``                      integer
``processes_contract_count``            integer
``implementation_count``                integer
``processes_implementation_count``      integer
``min_release_date``                    string (date-time or "")
``max_release_date``                    string (date-time or "")
``min_tender_date``                     string (date-time or "")
``max_tender_date``                     string (date-time or "")
``min_award_date``                      string (date-time or "")
``max_award_date``                      string (date-time or "")
``min_contract_date``                   string (date-time or "")
``max_contract_date``                   string (date-time or "")
``unique_buyers_identifier``            object                      A mapping from identifier to name
``unique_buyers_name_no_id``            array*
``unique_suppliers_identifier``         object                      A mapping from identifier to name
``unique_suppliers_name_no_id``         array*
``unique_procuring_identifier``         object                      A mapping from identifier to name
``unique_procuring_name_no_id``         array*
``unique_tenderers_identifier``         object                      A mapping from identifier to name
``unique_tenderers_name_no_id``         array*
``unique_buyers``                       array[string]               An array of organisation names, with the identifier in brackets if it exists
``unique_suppliers``                    array[string]               An array of organisation names, with the identifier in brackets if it exists
``unique_procuring``                    array[string]               An array of organisation names, with the identifier in brackets if it exists
``unique_tenderers``                    array[string]               An array of organisation names, with the identifier in brackets if it exists
``unique_buyers_count``                 integer
``unique_suppliers_count``              integer
``unique_procuring_count``              integer
``unique_tenderers_count``              integer
``unique_org_identifier_count``         integer
``unique_org_name_count``               integer
``unique_org_count``                    integer
``unique_organisation_schemes``         array*
``organisations_with_address``          integer
``organisations_with_contact_point``    integer
``total_item_count``                    integer                     The sum of the following 3 item counts:
``tender_item_count``                   integer
``award_item_count``                    integer
``contract_item_count``                 integer
``unique_item_ids_count``               integer
``item_identifier_schemes``             array*
``unique_currency``                     array*
``planning_doc_count``                  integer
``tender_doc_count``                    integer
``tender_milestones_doc_count``         integer
``award_doc_count``                     integer
``contract_doc_count``                  integer
``implementation_doc_count``            integer
``implementation_milestones_doc_count`` integer
``planning_doctype``                    object                      A mapping from ``documentType``, to the number of occurrences
``tender_doctype``                      object                      A mapping from ``documentType``, to the number of occurrences
``tender_milestones_doctype``           object                      A mapping from ``documentType``, to the number of occurrences
``award_doctype``                       object                      A mapping from ``documentType``, to the number of occurrences
``contract_doctype``                    object                      A mapping from ``documentType``, to the number of occurrences
``implementation_doctype``              object                      A mapping from ``documentType``, to the number of occurrences
``implementation_milestones_doctype``   object                      A mapping from ``documentType``, to the number of occurrences
``contracts_without_awards``            array                       An array of contract objects that don't have awards. **This is an OCDS implementation error.**
======================================= =========================== ==============

records_aggregates
^^^^^^^^^^^^^^^^^^

============================= ==================== ==============
Property (key) name	      Type                 Value
============================= ==================== ==============
``count``                     integer              The number of items in the records array
``unique_ocids``              array*               An array of all ocids, deduplicated
============================= ==================== ==============

additional codelist object
^^^^^^^^^^^^^^^^^^^^^^^^^^

=========================== ======================= ============
Property (key) name	    Type                    Value
=========================== ======================= ============
``path``                    string                  The JSON Pointer to the parent object, with array indices removed, e.g. ``releases/tender/documents``
``field``                   string                  The name of the codelist field, e.g. ``documentType`` 
``codelist``                string                  The filename of the codelist, e.g. ``documentType.csv``
``codelist_url``            string                  The URL of the codelist, e.g. ``https://raw.githubusercontent.com/open-contracting/standard/1.1/schema/codelists/documentType.csv``
``codelist_amend_urls``     array[array[string]     The URLs of the codelist patches in extensions that modify the codelist, as an array of pairs of ``+`` or ``-`` and the URL, e.g. ``[["+", "https://raw.githubusercontent.com/open-contracting-extensions/ocds_tariffs_extension/d9df2969030b0a555c24c7db685262c714b4da24/codelists/+documentType.csv"]]``
``isopen``                  boolean                 Is this an open codelist?
``values``                  array*                  Values of the field that are not in the codelist
``extension_codelist``      boolean                 Is the codelist added by an extension? (Not only modified by it)
=========================== ======================= ============

additional check object
^^^^^^^^^^^^^^^^^^^^^^^

=========================== ===================== ==============
Property (key) name	    Type                  Value
=========================== ===================== ==============
``json_location``           string                A JSON Pointer to the problematic data, e.g. ``releases/0/buyer``
=========================== ===================== ==============


conformance_errors
^^^^^^^^^^^^^^^^^^

=============================== ======================= =====
Property (key) name	        Type                    Value
=============================== ======================= =====
``ocds_prefixes_bad_format``    array[array[string]]    An array of pairs of a bad ``ocid`` value and the JSON Pointer to it, e.g. ``["MY-ID", "releases/0/ocid"]``
``ocid_description``            string                  The description of the ``ocid`` field from the OCDS schema
``ocid_info_url``               string                  The URL to the identifiers content in the OCDS documentation
=============================== ======================= =====

additional_fields
^^^^^^^^^^^^^^^^^

============================= ========= ==============
Property (key) name	      Type      Value
============================= ========= ==============
``path``                      string    The JSON Pointer to the parent object, with array indices removed, e.g. ``/releases/tender``
``field``                     string    The name of the additional field, e.g. ``myField``
``usage_count``               integer   The number of times the additional field is set
============================= ========= ==============

all_additional_fields
^^^^^^^^^^^^^^^^^^^^^

=================================== =========== ==============
Property (key) name	            Type        Value
=================================== =========== ==============
``count``                           integer     The number of times the additional field is set
``examples``                        array*      A sample of up to 3 values of the field
``root_additional_field``           boolean     Is the parent object described by the schema?
``additional_field_descendance``    object      The additional fields that are descendants of this field. Is only set if ``root_additional_field`` is true. A mapping from an additional field's JSON Pointer (with array indices removed) to an all_additional_fields_ object in which ``root_additional_field`` is false
``path``                            string      The JSON Pointer to the parent object, with array indices removed, e.g. ``/releases/tender``
``field_name``                      string      The name of the additional field, e.g. ``myField``
=================================== =========== ==============

array\*
^^^^^^^

An array marked with an asterisk is populated from fields in the data, so could be any type (if the data doesn't conform to the schema).

Contributing
------------

lib-cove-ocds was extracted from [cove](https://github.com/OpenDataServices/cove/tree/fa4441b9413324a740b8dc063ffbf0256a353c55).
