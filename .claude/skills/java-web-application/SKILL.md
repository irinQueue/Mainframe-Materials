---

name: java-web-application

description: Create a Java web application using the rules listed herein.

---

When creating a Java web application, always use the following rules:

* Ensure that the web application is created using the corresponding agent skill.
* Use Maven for building the application.
* Ensure that the latest Amazon Corretto version for the current year is used for the Dockerfile, if it exists. Note that this version can be higher than the actual Java version used by the code, so that forward-compatibility is guaranteed.
* Ensure that `java -jar` is used to run the application.
* Ensure that `mvn test` is used for unit testing.
* Ensure that the application is closed by closing the `java` executable, with `taskkill` used when running on Windows.
* Ensure that the JAR file generated via `mvn package` successfully runs with `java -jar`, with special focus on not encountering circular dependencies.
* Ensure that the `pom.xml` file is configured such that running `mvn package` builds a standalone JAR file that can be executed with `java -jar`.
* Ensure that the `pom.xml` file uses `<maven.compiler.release>` in <properties> instead of `<maven.compiler.source>` and `<maven.compiler.target>`.
* Ensure that the `pom.xml` file does not specify a compiler/runtime version, and instead defers to what is set in `<maven.compiler.release>` in `<properties>`.
* Ensure that the latest stable Spring Boot version listed in `spring.io` for the current year is used as the framework.
* Ensure that Spring Boot's AspectJ mode (without configuring the AspectJ compiler and weaver in the `pom.xml` file) is used as the framework feature for async and transaction management.
* The back-end code must use the latest Java features as much as possible, like using streams over for-loops (while decomposing `forEach` terminals into its corresponding `map`, `flatMap`, `filter` and `forEach` steps, so that `forEach` only contains side-effectful operations), `Stream::toList` or `Stream::collect` over calling `Collection::add` or equivalent `Collection` methods in `forEach`, java.time classes over java.util.Date and java.util.Calendar (using java.time methods for converting to `Date`/`Calendar`, if necessary), using try-with-resources over explicit calls to `AutoCloseable::close`, using pattern matching for `switch` or `instanceof` over casting, and using switch expressions over cascading/consecutive `if` statements or `switch` statements.
* The back-end code must use @Inject instead of @Autowired in all code in main and test, whenever possible.
* The back-end code must convert all public classes to package-private classes that implement public sealed interfaces, whenever possible.
* The back-end code must convert all non-final classes to final classes, whenever possible.
* The back-end code must convert all final classes (initializers, configs, controllers, models, filters, providers, services, tests) to records, whenever possible. If the final class derives state in the constructor, write a new constructor for that purpose, then use @Inject on that constructor.
* The back-end code must group sealed interfaces and their permitted package-private implementations in their own subpackages.
* The back-end code must enable virtual thread support in Spring Boot even if the code itself sticks to Java 17, just in case it is running in a Java 21 or later JVM.
* The back-end code must use Spring's Argon2Password4jPasswordEncoder for implementing Argon2id for password encryption.
* The back-end code must use jUnit for unit tests.
* The back-end code must have a working module-info.java file to enforce modular Java code.
* The back-end code must have its module-info.java file configured to restrict access and reflection as much as possible, while still allowing the code to run.
* The back-end code must use the Jakarta JPA library for database access, with type safety enforced by calling generic methods that accept classes like `EntityManager::createQuery`.
* The back-end code must use  `ExecutorService` on every class by using `CompletableFuture` types, such that there is only one `ExecutorService` value that is injected in every class that needs one, and that `ExecutorService` instance uses virtual threads in Java 21 or later via MethodHandle::invokeExact reflection, for asynchronous processing.
