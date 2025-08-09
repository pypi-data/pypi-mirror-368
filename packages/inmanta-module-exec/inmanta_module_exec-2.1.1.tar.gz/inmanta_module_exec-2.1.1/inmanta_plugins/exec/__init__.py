"""
Copyright 2018 Inmanta

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Contact: code@inmanta.com
"""

import shlex
import subprocess

import inmanta.agent.handler
import inmanta.export
import inmanta.plugins
import inmanta.resources
import inmanta_plugins.mitogen.abc


@inmanta.plugins.plugin()
def in_shell(command: "string") -> "string":  # type: ignore
    """Wrap the command such that it is executed in a shell"""
    return subprocess.list2cmdline(["sh", "-c", command])


@inmanta.plugins.plugin()
def shlex_join(cmd: "string[]") -> "string":  # type: ignore
    """
    Join the provided command into a safe string that can be parsed by a shell, where
    each item in the command is threated a dedicated argument.

    :param cmd: The command to join into a string
    """
    return shlex.join(cmd)


@inmanta.resources.resource("exec::Run", agent="host.name", id_attribute="command")
class Run(inmanta_plugins.mitogen.abc.ResourceABC):
    """
    This class represents a shell command
    """

    command: str
    creates: str
    cwd: str
    environment: str
    onlyif: str
    path: str
    reload: str
    reload_only: bool
    returns: list[int]
    timeout: int
    unless: str
    skip_on_fail: bool

    fields = (  # type: ignore[assignment]
        "command",
        "creates",
        "cwd",
        "environment",
        "onlyif",
        "path",
        "reload",
        "reload_only",
        "returns",
        "timeout",
        "unless",
        "skip_on_fail",
    )


@inmanta.agent.handler.provider("exec::Run", name="posix")
class PosixRunHandler(inmanta_plugins.mitogen.abc.HandlerABC[Run]):
    """
    A handler to execute commands on posix compatible systems. This is
    a very atypical resource as this executes a command. The check_resource
    method will determine based on the "reload_only", "creates", "unless"
    and "onlyif" attributes if the command will be executed.
    """

    def _execute(self, command, timeout, cwd=None, env={}):
        args = shlex.split(command)
        if env is None or len(env) == 0:
            env = None
        return self.proxy.run(args[0], args[1:], env, cwd, timeout=timeout)

    def read_resource(
        self, ctx: inmanta.agent.handler.HandlerContext, resource: Run
    ) -> None:
        # a True for a condition means that the command may be executed.
        execute = True

        if resource.creates is not None and resource.creates != "":
            # check if the file exists
            execute &= not self.proxy.file_exists(resource.creates)

        if resource.unless is not None and resource.unless != "":
            # only execute this Run if this command fails
            value = self._execute(
                resource.unless, resource.timeout, env=resource.environment
            )
            ctx.info(
                "Unless cmd %(cmd)s: out: '%(stdout)s', err: '%(stderr)s', returncode: %(retcode)s",
                cmd=resource.unless,
                stdout=value[0],
                stderr=value[1],
                retcode=value[2],
            )

            execute &= value[2] != 0

        if resource.onlyif is not None and resource.onlyif != "":
            # only execute this Run if this command is succesfull
            value = self._execute(
                resource.onlyif, resource.timeout, env=resource.environment
            )
            ctx.info(
                "Onlyif cmd %(cmd)s: out: '%(stdout)s', err: '%(stderr)s', returncode: %(retcode)s",
                cmd=resource.onlyif,
                stdout=value[0],
                stderr=value[1],
                retcode=value[2],
            )

            execute &= value[2] == 0

        ctx.set("execute", execute)
        if execute:
            raise inmanta.agent.handler.ResourcePurged()

    def create_resource(
        self, ctx: inmanta.agent.handler.HandlerContext, resource: Run
    ) -> None:
        if resource.reload_only:
            # TODO It is only reload
            return

        if self.do_cmd(ctx, resource, resource.command):
            ctx.set_created()

    def do_cmd(self, ctx, resource, cmd):
        """
        Execute the command (or reload command) if required
        """
        if ctx.get("execute"):
            cwd = None
            if resource.cwd != "":
                cwd = resource.cwd
            ctx.debug(
                "Execute %(cmd)s with timeout %(timeout)s and working dir %(cwd)s and env %(env)s",
                cmd=cmd,
                timeout=resource.timeout,
                cwd=cwd,
                env=resource.environment,
            )
            ret = self._execute(
                cmd, resource.timeout, cwd=cwd, env=resource.environment
            )
            if ret[2] not in resource.returns:
                ctx.error(
                    "Failed to execute %(cmd)s: out: '%(stdout)s', err: '%(stderr)s', returncode: %(retcode)s ",
                    cmd=cmd,
                    stdout=ret[0],
                    stderr=ret[1],
                    retcode=ret[2],
                )

                if resource.skip_on_fail:
                    raise inmanta.agent.handler.SkipResource(
                        "Failed to execute command: %s" % ret[1]
                    )
                else:
                    raise Exception("Failed to execute command: %s" % ret[1])
            else:
                ctx.info(
                    "Executed %(cmd)s: out: '%(stdout)s', err: '%(stderr)s', returncode: %(retcode)s ",
                    cmd=cmd,
                    stdout=ret[0],
                    stderr=ret[1],
                    retcode=ret[2],
                )
            return True

        return False

    def update_resource(
        self,
        ctx: inmanta.agent.handler.HandlerContext,
        changes: dict,
        resource: Run,
    ) -> None:
        raise NotImplementedError("ProxyRunHandler doesn't support update_resource !")

    def delete_resource(
        self, ctx: inmanta.agent.handler.HandlerContext, resource: Run
    ) -> None:
        raise NotImplementedError("PosixRunHandler doesn't support delete_resource !")

    def can_reload(self):
        """
        Can this handler reload?
        """
        return True

    def do_reload(self, ctx, resource):
        """
        Reload this resource
        """
        if resource.reload:
            return self.do_cmd(ctx, resource, resource.reload)

        return self.do_cmd(ctx, resource, resource.command)
