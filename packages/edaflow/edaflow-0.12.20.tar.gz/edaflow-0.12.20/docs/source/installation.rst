Installation Guide
==================

Requirements
------------

edaflow requires Python 3.8 or higher and the following dependencies:

* **pandas** >= 1.5.0 - Data manipulation and analysis
* **numpy** >= 1.21.0 - Numerical computing
* **matplotlib** >= 3.5.0 - Static plotting
* **seaborn** >= 0.11.0 - Statistical data visualization
* **scipy** >= 1.9.0 - Scientific computing
* **plotly** >= 5.0.0 - Interactive visualizations
* **scikit-learn** >= 1.0.0 - Machine learning library (for regression analysis)
* **statsmodels** >= 0.13.0 - Statistical analysis (for LOWESS smoothing)
* **missingno** >= 0.5.2 - Missing data visualization

Install from PyPI (Recommended)
--------------------------------

The easiest way to install edaflow is using pip from PyPI:

.. code-block:: bash

   pip install edaflow

This will automatically install all required dependencies.

Install from Source
-------------------

If you want to install the latest development version from GitHub:

.. code-block:: bash

   git clone https://github.com/evanlow/edaflow.git
   cd edaflow
   pip install -e .

Development Installation
------------------------

For development work, install with additional development dependencies:

.. code-block:: bash

   git clone https://github.com/evanlow/edaflow.git
   cd edaflow
   pip install -e ".[dev]"

This includes tools for:

* **pytest** - Testing framework
* **black** - Code formatting
* **flake8** - Linting
* **isort** - Import sorting
* **mypy** - Type checking
* **build** - Package building
* **twine** - PyPI uploading

Verify Installation
-------------------

To verify that edaflow is installed correctly:

.. code-block:: python

   import edaflow
   print(edaflow.hello())
   print(f"edaflow version: {edaflow.__version__}")

You should see:

.. code-block:: text

   Hello from edaflow! Ready for exploratory data analysis.
   edaflow version: 0.8.6

Virtual Environment (Recommended)
----------------------------------

It's recommended to install edaflow in a virtual environment:

.. code-block:: bash

   # Create virtual environment
   python -m venv edaflow_env
   
   # Activate (Windows)
   edaflow_env\\Scripts\\activate
   
   # Activate (macOS/Linux)
   source edaflow_env/bin/activate
   
   # Install edaflow
   pip install edaflow

Jupyter Notebook Setup
----------------------

For the best experience with color-coded outputs and interactive visualizations:

.. code-block:: bash

   pip install jupyter
   jupyter notebook

Then in your notebook:

.. code-block:: python

   import pandas as pd
   import edaflow
   
   # Load data
   df = pd.read_csv('your_data.csv')
   
   # Beautiful color-coded output
   edaflow.check_null_columns(df)

Troubleshooting
---------------

**Import Error**
~~~~~~~~~~~~~~~~

If you encounter import errors, ensure all dependencies are installed:

.. code-block:: bash

   pip install --upgrade edaflow

**Version Conflicts**
~~~~~~~~~~~~~~~~~~~~~

If you have dependency conflicts, create a fresh virtual environment:

.. code-block:: bash

   python -m venv fresh_env
   # Activate the environment
   pip install edaflow

**Missing Dependencies**
~~~~~~~~~~~~~~~~~~~~~~~~

If specific visualizations don't work, check for missing optional dependencies:

.. code-block:: bash

   # For interactive plots
   pip install plotly>=5.0.0
   
   # For advanced statistics
   pip install scikit-learn>=1.0.0 statsmodels>=0.13.0

**Performance Issues**
~~~~~~~~~~~~~~~~~~~~~~

For large datasets, consider:

* Using smaller samples for visualization functions
* Increasing memory allocation for Jupyter notebooks
* Using the ``verbose=False`` option in functions that support it

Getting Help
------------

If you encounter issues:

1. Check the `GitHub Issues <https://github.com/evanlow/edaflow/issues>`_
2. Create a new issue with your error details
3. Include your Python version, edaflow version, and full error traceback
