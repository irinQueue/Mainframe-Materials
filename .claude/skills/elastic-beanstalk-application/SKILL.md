---

name: elastic-beanstalk-application

description: Create an Elastic Beanstalk application using the rules listed herein.

---

When creating a container application, always use the following rules:

* The application must have a Dockerfile that follows the rules from the container application agent skill.
* The application's packaging command must create a Docker deployment ZIP file containing the:
  * .ebextensions directory,
  * .platform directory,
  * Dockerfile file, and
  * every file and directory referenced in the Dockerfile file.
* The application's tests must validate the Docker deployment ZIP file created by the application's packaging command.