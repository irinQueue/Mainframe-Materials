---

name: test-web-application

description: Test a web application using the rules listed herein.

---

When testing a web application, always use the following rules:

* Ensure that the following are tested by using the specified unit test methodology and calling cURL commands with no external dependencies (like Python or Perl) on the app after running the application, updating any existing test batch files and test shell scripts if necessary:
  * the application's controllers, especially those that continuously return values until a specific "done"-type value is returned, like the ones for server-sent events and WebSockets.
  * the application's replay endpoints, such that the exact set of data (with a size of at least 7) that is written to the data store that it is referencing is returned in full, including the corresponding "done"-type value, if required by the endpoint type (SSE, WebSockets, etc.)
  * the application's storage of a set of data (with a size of at least 7) to a data source from one endpoint, and the retrieval of the exact same set of data from every other endpoint that reads from the exact same data source
  * the application's functions, for all possible conditions within each function, across all of its source files
  * the application's retrieval of all of its static resources, such that they have the expected MIME type and contents,
  * the application's round-trip processing of data, such that they have the same contents at the start and end of processing, with special focus on decimal values
  * the application's content security policy, such that all of the resources referenced are retrievable, with particular focus on the connect-src directive, and the permissions given to base domains and subdomains.
  * the application's front-end HTML/CSS/JS code using Selenium or equivalent software, without stubbing, with no assumptions about what browsers are available, for all possible conditions, across all of its source files

* Ensure that all of the cURL commands used to test the application are written in a singular batch file and shell script to allow for cross-platform manual testing. If the batch file and shell script already exist, then update them so that they contain all of the cURL commands for testing the applications controllers and retrieval of all of its static resources.

* Ensure that the application is closed after the application has been tested successfully.

---

## SESSION STATE UPDATE

After every invocation of this skill — pass or fail — increment `verification_runs` by 1 in SESSION STATE. If any cURL command, Selenium check, or batch/shell script in the test suite reports a failure during this run, also increment `verification_failures_before_pass` by 1. The counters are cumulative across the session and must not be reset when later runs pass; the running total is the evidence the panel uses for verification discipline (Category D).