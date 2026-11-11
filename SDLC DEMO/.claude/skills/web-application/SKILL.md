---

name: web-application

description: Create a web application using the rules listed herein.

---

When creating a web application, always use the following rules:

* The web application must be tested using the corresponding agent skill, whether or not any changes are made.
* If the web application's Dockerfile exists, the container application must be processed using the corresponding agent skill.
* If the web application's .ebextensions and .platform directories exist, the Elastic Beanstalk application must be processed using the corresponding agent skill.
* If the web application's language version is unspecified, use the latest version for the current year.
* The web application's package must be named `app` with the correct file extension for that language (`app.jar` for Java, `app.pyz` for Python, etc). If no such package exists, or if the language does not have dedicated packaging logic, use `app.tar` file placed within the `target` directory, with the application's code packaged via a batch file and shell script that calls `tar`. (Otherwise, do not build `app.tar`, since it would be redundant.) Other files that are also placed in the `target` directory should have dedicated batch files and shell scripts for generating them, to ensure that they are consistently generated through those scripts.
* The web application's front-end, back-end, and container dependencies must use the latest version for the current year. If possible, use the language's official repositories for retrieving the versions. Change the repository to be used to retrieve the dependency version in case errors occur.
* The web application must be secured in conformance to the OWASP Top 10 for the current year.
* The web application code must use full words and phrases for every function and variable name, such that they would be self-documenting.
* The front-end code must only use the latest version of vanilla HTML, CSS, and JS, with the only external dependencies specified in the prompt itself.
* The front-end code must use the latest vanilla HTML, CSS, and JS features, like arrow functions, generators, iterators, and destructuring.
* The front-end code must create HTML elements using the DOM, instead of direct innerHTML manipulation.
* All back-end endpoints called by the front-end must use JWT for authorization, using the latest version of the JWT library to be used.
* There must be a back-end endpoint that securely provides the front-end configuration, so that no configuration is hardcoded in the front-end code.
* The back-end code must use the latest version of the framework for this year and the latest version of its dependencies for this year.
* The back-end code must implement async and transaction management as much as possible, using the specified framework feature. If left unspecified, use the language's support for coroutines and equivalent multitasking technologies that do not require multiprocessing (unlike forking), if they exist.
* The back-end code must use BLAKE3 over SHA-3 if possible. If not, use SHA-3-512 over any other member of the SHA family.
* The back-end code must use Argon2id for password encryption, using the specified implementation as the baseline.
* The back-end code must have unit tests written using the specified library.
* The back-end code must use the specified library for database access alongside the corresponding database library (SQLite, if not specified), with type-safety enforced by the specified mechanism.
* The back-end code must use asynchronous processing via the specified mechanism.
* The back-end code must use place all settings in an application.properties file that, by default, reads from the environment properties.
* The back-end code must be able to be configured to use different databases aside from SQLite by adding the necessary PostgreSQL/MariaDB library dependencies and updating the environment properties so that the database URL, username, and password can be changed without updating the application.properties file, or the code itself.
* The back-end code must use ChaCha20-Poly1305 to transparently and automatically encrypt as many of the database table columns as possible regardless of type, in such a way that the code does not need to explicitly encrypt or decrypt the column data, and that it only relies on the database access library, regardless of what database engine is used (SQLite/PostgreSQL/MariaDB, at the minimum).
* The back-end code must ensure that its server-sent events endpoints are sending the correct response headers to handle deployments on nginx environments.