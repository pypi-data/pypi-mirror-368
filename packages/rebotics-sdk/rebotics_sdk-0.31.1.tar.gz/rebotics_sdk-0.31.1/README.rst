============
rebotics_sdk
============

Rebotics SDK for communicating with Rebotics Services, API CLI client.

Features
--------

* Communication between Rebotics Services through provider client classes
* Two django applications for external communications through web-hooks
* CLI clients for Rebotics Services

Prerequisites
-------------

You need to have Python 3.7+ installed in your system for current system user.

Installation
------------

Linux & MacOS
~~~~~~~~~~~~~

Can be installed with pip:

.. code:: sh

   pip3 install --user --upgrade rebotics_sdk

You should have directory ~/.local/bin/ in your PATH variable in
~/.bashrc or ~/.bash_profile.

Windows
~~~~~~~

Is installed without –user flag:

.. code:: sh

   pip install --upgrade rebotics_sdk

Open environment variable settings and find PATH variable.

After installation rebotics-scripts should be located inside python3
directory.

Append the following path ``%APPDATA%\Local\Python<version>\bin\`` to
PATH variable, then log out from your system or restart your PC.

CLI Installation
~~~~~~~~~~~~~~~~

To run the commands in shell:

.. code:: sh

   pip install --upgrade --quiet --no-input rebotics_sdk[shell]

Usage
-----

After successful installation the CLI for following services should be
accessible:

-  admin
-  dataset
-  retailer
-  rebm
-  rebotics
-  fvm
-  hawkeye
-  hawkeye_camera

The “role” could be configured for these services except rebotics and hawkeye_camera.

Retailer setup
~~~~~~~~~~~~~~

For setup you need to configure role to access retailer instance with
specifying retailer server:

.. code:: sh

   retailer -r alpha configure --help

This command will prompt you to set retailer host, your username and
password.

For role you can specify anything for your own convenience.

Retailer CLI client
~~~~~~~~~~~~~~~~~~~

Usage:

.. code:: sh

   retailer [OPTIONS] COMMAND [ARGS]...

Options:

::

     -f, --format [table|id|json]

     -v, --verbose                 Enables verbose mode

     -c, --config PATH             Specify what config.json to use

     -r, --role TEXT               Key to specify what retailer to use

                                   [required]

     --api-verbosity INT           Display request detail

     --version                     Show the version and exit.

     --help                        Show this message and exit.

*Note: The same CLI structure could be used for other services. Check
the documentation on available commands at*\  `Confluence
page <https://retech.atlassian.net/wiki/spaces/REB3/pages/2703097931/Rebotics+SDK+CLI+client>`__\ *.*

Hawkeye Camera CLI client
~~~~~~~~~~~~~~~~~~~~~~~~~

Admin CLI tool to communicate with Public Hawkeye API for cameras
without authorization does not require to configure role in
rebotics_sdk. Instead, it accepts the target server url.

Example usage:

.. code:: sh

   hawkeye_camera -h https://hawkeye.rebotics.net create-capture "path_to_image.jpg" -c "camera_token"

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
