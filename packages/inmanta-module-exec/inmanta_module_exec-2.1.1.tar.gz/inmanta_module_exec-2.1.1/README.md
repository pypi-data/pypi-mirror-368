# exec adapter

Inmanta module to execute commands in a host.

## Features

This module supports:
- Environment variables.
- Commands with or without shell.
- Idempotent commands by creating files to track which commands have already been executed.
- CWD support: commands can be executed in different directories.
- Conditional command (only execute if certain condition is met).
- Command timeout.

## Usage example

Here is a simple example of command that execute sleep command in /root directory only if curl to 1.2.3.4 is successful.

```
import exec
import mitogen

exec::Run(
    host=host, 
    command="sleep 5", 
    cwd="/root",
    onlyif="curl --connect-timeout 1 --fail 1.2.3.4"
)

host = std::Host(
    name="server",
    os=std::linux,
    via=mitogen::Sudo(
        via=mitogen::Ssh(
            name="server",
            hostname="1.2.3.4",
            port=22,
            username="user",
        ),
    ),
)
```

```{toctree}
:maxdepth: 1
autodoc.rst
CHANGELOG.md
```