
Installation
============

This assumes you already have a :doc:`WuttJamaican app
<wuttjamaican:narr/install/index>` setup and working.

Install the WuttaTell package to your virtual environment:

.. code-block:: sh

   pip install WuttaTell

Edit your :term:`config file` to add telemetry submission info, and
related settings:

.. code-block:: ini

   [wutta.telemetry]
   default.collect_keys = os, python
   default.submit_url = https://example.com/api/my-node/telemetry

.. note::

   The built-in logic can collect some "minimal" telemetry info, but
   there is no built-in logic for the submission.
