
Installation
============

This assumes you already have a :doc:`WuttJamaican app
<wuttjamaican:narr/install/index>` setup and working.

Install the WuttaTell package to your virtual environment:

.. code-block:: sh

   pip install WuttaTell

Edit your :term:`config file` to add telemetry submission info, and
related settings.  Please note, the following example is just that -
and will not work as-is:

.. code-block:: ini

   [wutta.telemetry]
   default.collect_keys = os, python
   default.submit_url = /nodes/telemetry
   default.submit_uuid = 06897767-eb70-7790-8000-13f368a40ea3

.. note::

   The built-in logic can collect some "minimal" telemetry info, but
   there is no built-in logic for the submission.
