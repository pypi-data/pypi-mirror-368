# uvartage

_A wrapper around **[uv]** for usage with artifact storage in airgapped environments_

The **uvartage** command starts a [REPL] (read-eval-print loop) using the
[Python cmd module] where environment variables have been set for **uv** and **uvx**
to use an artifact storage that requires authentication.

> Please note: so far, only [Artifactory] is supported as such an artifact storage backend.


For convenience, the **git** command is also supported.

Own command implementations include:

*   **cd** changes directories
*   **env** prints the available environment variables
*   **list** partially implements the functionality
    of the Unix **ls** command (ie. list files and/or directories)
*   **pwd** prints the working directory path
*   **sh** can be used to run arbitrary commands using the shell interpreter

The credentials for the user are asked at start time,
and stored in environment variables for each repository.

The REPL features a simple history, and tab completion for a subset of the commands
(currently, only **list** and **sh**, based on paths in the file system).

The loop can be left in different ways, depending on the operating system:

* Unix: Ctrl-D
* Windows: Ctrl-Z followed by the enter key
* as an anternative, you could enter `EOF` literally and press the enter key to exit. This method should always work.



## Prerequisites

[uv] has to be installed,
but otherwise, only standard library modules are used.


## Usage

### Built.in usage information

```console
[osuser@workstation workdir]$ uvartage --help
usage: uvartage [-h] [--version] [-v ] [--backend {artifactory}] [--ca-file CA_FILE] [--user USER]
                [USER@]HOSTNAME ...

Wrapper for uv with artifact storage in airgapped environments

positional arguments:
  [USER@]HOSTNAME       the artifact storage hostname, or user and hostname combined by '@'.
  repositories          the package repositories (default first). If not at least one repository name
                        is provided, the value of the environment variable UVARTAGE_DEFAULT_REPOSITORY
                        will be used.

options:
  -h, --help            show this help message and exit
  --version             print version and exit
  -v , --verbose        show more messages
  --backend {artifactory}
                        the artifact storage backend type (default and currently the only supported
                        backend: artifactory)
  --ca-file CA_FILE     a CA cert bundle file to be provided via SSL_CERT_FILE.
  --user USER           username for the artifact storage backend if the hostname is not explicitly
                        specified as USER@HOSTNAME; default is 'osuser'.

[osuser@workstation workdir]$
```


### Example REPL start

> ... with examiniation of the environment variables set for **uv**

``` console
[osuser@workstation workdir]$ uvartage artuser@artifacts.example.com defaultrepo extrarepo1 extrarepo2
| Neither the environment variable SSL_CERT_FILE has been set, nor a CA file through --ca-file.
| You might encounter problems if using a non-standard (i.e. organization internal) certificate authority.
Please enter the password for artuser on artifacts.example.com (input is hidden):
Welcome to the uv wrapper shell. Type help or ? to list commands.

«uvartage» [osuser@workstation workdir] env UV*
UV_DEFAULT_INDEX=primary=https://artifacts.example.com/artifactory/api/pypi/defaultrepo/simple
UV_INDEX=extra1=https://artifacts.example.com/artifactory/api/pypi/extrarepo1/simple extra2=https://artifacts.example.com/artifactory/api/pypi/extrarepo2/simple
UV_INDEX_EXTRA1_PASSWORD=[masked: entered password]
UV_INDEX_EXTRA1_USERNAME=artuser
UV_INDEX_EXTRA2_PASSWORD=[masked: entered password]
UV_INDEX_EXTRA2_USERNAME=artuser
UV_INDEX_PRIMARY_PASSWORD=[masked: entered password]
UV_INDEX_PRIMARY_USERNAME=artuser
«uvartage» [osuser@workstation workdir]
```


### Supported commands in the REPL

```
«uvartage» [osuser@workstation workdir] help

Documented commands (type help <topic>):
========================================
EOF  cd  env  git  help  list  ls  pwd  sh  uv  uvx

«uvartage» [osuser@workstation workdir] help EOF
Exit the REPL by EOF (eg. Ctrl-D on Unix)
«uvartage» [osuser@workstation workdir] help cd
Change directory
«uvartage» [osuser@workstation workdir] help env
Print the environment variables
«uvartage» [osuser@workstation workdir] help git
Run git with the provided arguments
«uvartage» [osuser@workstation workdir] help help
List available commands with "help" or detailed help with "help cmd".
«uvartage» [osuser@workstation workdir] help list
Print directory contents (emulation)
«uvartage» [osuser@workstation workdir] help ls
Deprecated POSIX platform only external ls command
«uvartage» [osuser@workstation workdir] help pwd
Print working directory
«uvartage» [osuser@workstation workdir] help sh
Run an arbitrary command through the shell
«uvartage» [osuser@workstation workdir] help uv
Run uv with the provided arguments
«uvartage» [osuser@workstation workdir] help uvx
Run uvx with the provided arguments
«uvartage» [osuser@workstation workdir]
```


* * *
[uv]: https://docs.astral.sh/uv/
[REPL]: https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop
[Python cmd module]: https://docs.python.org/3/library/cmd.html
[Artifactory]: https://jfrog.com/artifactory/
