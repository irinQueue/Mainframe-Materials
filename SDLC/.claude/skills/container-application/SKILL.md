---

name: container-application

description: Create a container application using the rules listed herein.

---

When creating a container application, always use the following rules:

* Any container scripts created for this application should be added to any workflows setup for it, such that local and CI container runs behave the exact same way.
* Tests that are run using the corresponding agent skill should also run under the container, using scripts that are run both local and in CI.
* Close all instances of the non-container version of the application before continuing, with `taskkill` used when running on Windows.
* Confirm if Podman or Docker is available for building then running containers.
* Build then run the container using the container application's Dockerfile, then prove that this has been done for the current session.
* The container application's Dockerfile must only use the latest Alpine Linux image that supports aarch64, either from a derived image recommended by the other skill agent rules whose version supports automatic latest patch, or from installing the dependencies using `apk` on the Alpine Linux image without compiling from source, if no skill agent rules are applicable. If neither option is possible, print a message indicating what prevents any of the options from being used, then exit.
* The container application's Dockerfile should not use any non-Alpine Linux derived images, and must be updated if it does.
* The container application's Dockerfile should be used on Podman/Docker to build an image named `app` with all layers squashed, and with the smallest possible image size, build time, and layer count, in order of decreasing priority.
* The container application's image should be run in a detached auto-removed Podman/Docker container named `app` with the published port being the same as the one used in the non-container run.
* The container application's container should be used when running the application, and testing the web application using the corresponding agent skill.
* The container application's container should be stopped once done, ensured that the container is automatically removed, and that the container images are pruned.
* The Dockerfile should use the `RUN` directive only after all of the `ADD` and `COPY` directives.
* The Dockerfile should use the `COPY` directive for copying files to the container, and only use the `ADD` directive to extract compatible archives in the container (instead of using the `COPY` and `RUN` directives with the `tar` and `chown` commands). Any directives that use `ADD` to only copy files to the container (even if they are archives) should be replaced with `COPY` instead.
* The Dockerfile should minimize the amount of `COPY` and `ADD` directives used by merging multiple directives into one, as long as the logic is maintained.
* The application's `app` package should be copied by the Dockerfile to the container, without building the package within the container, to minimize the layers within the container image further.
* The application code must use the language's foreign-function interface features like native C calls, instead of creating helper C code then compiling them directly. Ensure that any usage of helper C code is proven to be irreplaceable with the native equivalent, based on the language documentation and in the language's Alpine Linux package's APKBUILD and build logs, if applicable.

