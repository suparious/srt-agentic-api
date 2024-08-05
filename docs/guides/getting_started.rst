Getting Started
===============

This guide will help you set up and run the SolidRusT Agentic API on your local machine.

Prerequisites
-------------

- Python 3.8+
- Docker (optional, for containerized deployment)

Installation
------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/your-repo/srt-agentic-api.git
      cd srt-agentic-api

2. Create a virtual environment and activate it:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. Install the required dependencies:

   .. code-block:: bash

      pip install -r requirements.txt

4. Set up the configuration:

   Copy the `.env.example` file to `.env` and update the values according to your setup.

Running the API
---------------

To run the API locally:

.. code-block:: bash

   uvicorn app.main:app --reload

The API will be available at `http://localhost:8000`. You can access the API documentation at `http://localhost:8000/docs`.

Next Steps
----------

- Read the :doc:`configuration` guide to learn how to customize the API settings.
- Explore the :doc:`../api/endpoints/agent` documentation to start creating and managing agents.
- Check out the :doc:`deployment` guide for information on deploying the API to production environments.