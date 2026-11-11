---

name: python-web-application

description: Create a Python web application using the rules listed herein.

---

When creating a Python web application, always use the following rules:

* Ensure that the web application is created using the corresponding agent skill.
* Ensure that the dependencies are either pure Python, or support running on Alpine Linux on ARM in a Podman/Docker container that is built by copying the PYZ file and `requirements.txt` file in the `target` directory.
* Ensure that if the Dockerfile exists for the web application, that it uses the latest Python Alpine Linux image. If so, check if free-threading support is enabled for the latest Python Alpine Linux image. If so, update the ENTRYPOINT directive to include `-X gil=0`.
* Ensure that Python is always run with the `python -X gil=0` command from a Python virtual environment that has been setup in the .venv directory either within the application directory or one level above it. If it is not possible, print a request for the user to do so and end processing.
* Ensure that the Python application is successfully packaged as a PYZ file in the `target` directory that is built with the `shiv` library to only contain pure Python dependencies, and a `requirements.txt` file that has all of the dependencies (pure Python and non-pure Python), and that a batch file and shell script is created for packaging the application using the corresponding command. The non-pure-Python dependencies that cannot be packaged in the PYZ file must be listed in a separate `requirements.txt` file placed in the `target` directory, which should be used to install the dependencies in the Dockerfile.
* Ensure that the generated PYZ file successfully runs with `python -X gil=0`, with special focus on not encountering circular dependencies.
* Ensure that the generated PYZ file is used for integration testing.
* Ensure that the Python `unittest` library is used for unit testing.
* Ensure that the application is closed by closing the `python` executable.
* Ensure that the `requirements.txt` file is processed using the Python virtual environment.
* Ensure that Django 6 at the minimum is used as the framework.
* The back-end code must use the latest Python features as much as possible, like list comprehensions over for-loops and using the `with` keyword over explicit calls to close resources.
* The back-end code must convert all classes (initializers, configs, controllers, models, filters, providers, services, tests) to abstract base classes with private implementing frozen dataclasses with slots and caching enabled, whenever possible.
* The back-end code must use Django's argon2-cffi support for implementing Argon2id for password encryption.
* The back-end code must use the unittest library for unit tests.
* The back-end code must use the SQLAlchemy library for database access, with type safety enforced by calling typed constructors that accept dataclasses.
* The back-end code must use ASGI and `asyncio` on every class for asynchronous processing.
