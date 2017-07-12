Basically you're able to install the lambda-toolkit using pip. You can also install it manually, cloning the project from GitHub.

.. hint::

    If you're not a developer and you're not planning to contribute developing in lambda-toolkit, **we do recommend to use pip** installation mode..

---------------------
General Prerequisites
---------------------

Basically, to start to use the lambda-toolkit, you must have at least:

* Python 2.7
* Package Management System (``pip``)
* AWS Credentials

Python 2.7
==========

Python 2.7 is required to use lambda-toolkit. By this way, you should make sure that your system has a proper Python 2.7 installation available::

    $ python --version
    Python 2.7.x

or::

    $ python2.7 --version
    Python 2.7.x

If your system does not support Python 2.7, you can install `here <python27_>`_.

.. _python27: https://www.python.org/download/releases/2.7/

Package Management System (pip)
===============================

pip is required to use lambda-toolkit. By this way, you should make sure that your system has a proper pip (compatible with Python 2.7) installed::

   $ pip --version
   pip 9.0.1 from /Library/Python/2.7/site-packages/pip-9.0.1-py2.7.egg (python 2.7)

If you system does not has pip installed, you can install `here <pip_>`_.

.. _pip: https://pip.pypa.io/en/stable/installing/

AWS Credentials
===============

Lambda-toolkit can read yours credentials from the **system environment variables** or **credential files**.

If you're already using aws cli for example, credential files were generated when the command ``aws configure`` was executed.

.. hint::

    Lambda-toolkit tries first to read the environment variables, and if it is not configured, lambda-toolkit reads the credential files.

.. warning::

    We do recommend to use credential files.

Using credential files
------------------------------

Make sure that you have the files:

* ``~/.aws/credentials``
* ``~/.aws/config``

For example:

~/.aws/credentials::

   [default]
   aws_access_key_id = AAAAAAAAAAAAAAAAAAAA
   aws_secret_access_key = AWS_ACCESS_SECRET_KEY__KEEP_IT_SAFE

~/.aws/config::

   [default]
   region = eu-west-1

.. hint::

   As you can see, the example shows how to create a default credential. You can create others, and then, you can use the environment variable ``AWS_PROFILE`` to choice a specific one.
   You can also overwrite your region option, setting the environment variable ``AWS_REGION``.

Using environments variables
----------------------------

Specify the env variables below:

* ``AWS_ACCESS_KEY_ID``
* ``AWS_SECRET_ACCESS_KEY``
* ``AWS_REGION``

For example::

   $ export AWS_ACCESS_KEY_ID="AAAAAAAAAAAAAAAAAAAA"
   $ export AWS_SECRET_ACCESS_KEY="AWS_ACCESS_SECRET_KEY__KEEP_IT_SAFE"
   $ export AWS_REGION="us-east-1"

.. hint::

    Remember that you must ``export`` the variables.

.. warning::

    Lambda-toolkit only uses the environment variables, if the 3 variables are available.

---------------------
Installing
---------------------

Installing using pip
====================

The installation with pip is quick and simple. For common installation, use the command below::

   $ sudo -H pip install lambda-toolkit
   $ lt --help

.. hint::

   If you want uninstall lambda-toolkit, just run ``sudo pip uninstall lambda-toolkit``.
   To update, run ``sudo pip install lambda-toolkit -U``

Cloning the repository manually
===============================

Installing from repository is not to common users, but it is also another option. To install from repository you also need to have the ``git`` client installed.

The first step is clone the repository::

   $ git clone https://github.com/lucioveloso/lambda-toolkit

Install the requirements using pip::

   $ pip install -r lambda-toolkit/user-requirements.txt
   $ lambda-toolkit/bin/lt --help

And then, you are able to run the lambda-toolkit from current user:
