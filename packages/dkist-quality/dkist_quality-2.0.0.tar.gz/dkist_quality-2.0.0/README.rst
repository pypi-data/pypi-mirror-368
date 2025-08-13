dkist-quality
-------------

|codecov|

Provides the ability to create a pdf quality report from structured quality data.


Sample Usage
~~~~~~~~~~~~

.. code-block:: python

    from dkist_quality.report import format_report

    def create_quality_report(report_data: dict | list[dict], dataset_id: str) -> bytes:
        """
        Generate a quality report in pdf format.

        :param report_data: Quality data for the dataset.
        :param dataset_id: The dataset id.

        :return: quality report in pdf format
        """
        return format_report(report_data=report_data, dataset_id=dataset_id)

Developer Setup
~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install -e .[test]
    pip install pre-commit
    pre-commit install


License
-------

This project is Copyright (c) NSO / AURA and licensed under
the terms of the BSD 3-Clause license. This package is based upon
the `Openastronomy packaging guide <https://github.com/OpenAstronomy/packaging-guide>`_
which is licensed under the BSD 3-clause licence. See the licenses folder for
more information.

.. |codecov| image:: https://codecov.io/bb/dkistdc/dkist-quality/branch/master/graph/badge.svg
   :target: https://codecov.io/bb/dkistdc/dkist-quality
