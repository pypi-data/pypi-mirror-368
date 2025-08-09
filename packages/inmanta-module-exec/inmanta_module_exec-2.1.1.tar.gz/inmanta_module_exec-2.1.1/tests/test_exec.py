"""
Copyright 2017 Inmanta

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

import os

import inmanta
from pytest_inmanta.plugin import Project


# TODO: check reported changes
def test_exec(project: Project, tmpdir: str) -> None:
    test_path_1 = str(tmpdir.join("file1"))
    test_path_2 = str(tmpdir.join("file2"))

    project.compile(
        """
import unittest
import exec
import mitogen

host = std::Host(name="server", via=mitogen::Local(), os=std::linux)
exec::Run(host=host, command="/usr/bin/touch %(f)s")
        """
        % {"f": test_path_1}
    )

    assert not os.path.exists(test_path_1)

    assert project.dryrun_resource("exec::Run")
    project.deploy_resource("exec::Run")

    assert os.path.exists(test_path_1)

    project.compile(
        """
import unittest
import exec
import mitogen

host = std::Host(name="server", via=mitogen::Local(), os=std::linux)
exec::Run(host=host, command="/usr/bin/touch %(f2)s", creates="%(f1)s")
        """
        % {"f1": test_path_1, "f2": test_path_2}
    )

    assert not project.dryrun_resource("exec::Run")
    project.deploy_resource("exec::Run")

    assert os.path.exists(test_path_1)
    assert not os.path.exists(test_path_2)


def test_cwd(project: Project, tmpdir: str) -> None:
    project.compile(
        """
import unittest
import exec
import mitogen

host = std::Host(name="server", via=mitogen::Local(), os=std::linux)
exec::Run(host=host, command="/usr/bin/touch test", cwd="%(f)s")
        """
        % {"f": str(tmpdir)}
    )

    assert project.dryrun_resource("exec::Run")
    project.deploy_resource("exec::Run")

    assert tmpdir.join("test").exists()


def test_return_codes(project: Project, tmpdir: str) -> None:
    project.compile(
        """
import unittest
import exec
import mitogen

host = std::Host(name="server", via=mitogen::Local(), os=std::linux)
exec::Run(host=host, command="python -c 'import sys; sys.exit(3)'", returns=[0, 3, 5])
        """
    )

    assert project.dryrun_resource("exec::Run")
    project.deploy_resource("exec::Run")


def test_onlyif(project: Project, tmpdir: str) -> None:
    project.compile(
        """
import unittest
import exec
import mitogen

host = std::Host(name="server", via=mitogen::Local(), os=std::linux)
exec::Run(host=host, command="/usr/bin/touch test", cwd="%(f)s", onlyif="python -c 'import sys; sys.exit(1)'")
        """
        % {"f": str(tmpdir)}
    )

    # verify file is not created when only if returns with exit code 1
    assert not project.dryrun_resource("exec::Run")
    project.deploy_resource("exec::Run")
    assert not tmpdir.join("test").exists()

    project.compile(
        """
import unittest
import exec
import mitogen

host = std::Host(name="server", via=mitogen::Local(), os=std::linux)
exec::Run(host=host, command="/usr/bin/touch test", cwd="%(f)s", onlyif="python -c 'import sys; sys.exit(0)'")
        """
        % {"f": str(tmpdir)}
    )

    # verify file is created when only if returns with exit code 0
    assert project.dryrun_resource("exec::Run")
    project.deploy_resource("exec::Run")
    assert tmpdir.join("test").exists()


def test_unless(project: Project, tmpdir: str) -> None:
    project.compile(
        """
import unittest
import exec
import mitogen

host = std::Host(name="server", via=mitogen::Local(), os=std::linux)
exec::Run(host=host, command="/usr/bin/touch test", cwd="%(f)s", unless="python -c 'import sys; sys.exit(0)'")
        """
        % {"f": str(tmpdir)}
    )

    # verify file is not created when unless returns with exit code 0
    assert not project.dryrun_resource("exec::Run")
    project.deploy_resource("exec::Run")
    assert not tmpdir.join("test").exists()

    project.compile(
        """
import unittest
import exec
import mitogen

host = std::Host(name="server", via=mitogen::Local(), os=std::linux)
exec::Run(host=host, command="/usr/bin/touch test", cwd="%(f)s", unless="python -c 'import sys; sys.exit(1)'")
        """
        % {"f": str(tmpdir)}
    )

    # verify file is created when only if returns with exit code 1
    assert project.dryrun_resource("exec::Run")
    project.deploy_resource("exec::Run")
    assert tmpdir.join("test").exists()


def test_timeout(project: Project, tmpdir: str) -> None:
    project.compile(
        """
import unittest
import exec
import mitogen

host = std::Host(name="server", via=mitogen::Local(), os=std::linux)
exec::Run(host=host, command="sleep 2", timeout=1)
        """
    )

    e = project.get_resource("exec::Run")
    ctx = project.deploy(e)
    assert ctx.status == inmanta.const.ResourceState.failed
    assert ctx.change == inmanta.const.Change.nochange


def test_4_java_home(project: Project, tmpdir: str) -> None:
    test_path_1 = str(tmpdir.join("outqput"))
    assert os.path.exists(str(tmpdir))
    print(test_path_1)

    project.compile(
        """
import unittest
import exec
import mitogen

environment_vars = {"JAVA_HOME": "/usr/local/sbin:/usr/local/bin:/usr/bin:/usr/sbin:/sbin:/bin"}

host = std::Host(name="server", via=mitogen::Local(), os=std::linux)
exec::Run(host=host, command="sh -c 'env >%(f)s 2>&1'", environment=environment_vars)
        """
        % {"f": test_path_1}
    )

    assert not os.path.exists(test_path_1)

    assert project.dryrun_resource("exec::Run")
    project.deploy_resource("exec::Run")
    assert os.path.exists(test_path_1)
    with open(test_path_1) as fh:
        assert (
            "/usr/local/sbin:/usr/local/bin:/usr/bin:/usr/sbin:/sbin:/bin" in fh.read()
        )


def test_4_java_home_3(project: Project, tmpdir: str) -> None:
    test_path_1 = str(tmpdir.join("output"))
    assert os.path.exists(str(tmpdir))
    print(test_path_1)

    project.compile(
        """
        import unittest
        import exec
        import mitogen

        environment_vars = {
        "JAVA_HOME" : "/usr/lib/jvm/jre-1.7.0-openjdk/",
        "JAVA_TOOL_OPTIONS" : "-Dfile.encoding=UTF8 >> /home/inmanta/install.log"
        }

        host = std::Host(name="server", via=mitogen::Local(), os=std::linux)
        exec::Run(
        host=host,
        command="sh -c 'export PATH=$PATH:/usr/lib/jvm/jre-1.7.0-openjdk/bin; env >%(f)s 2>&1'", environment=environment_vars)
        """
        % {"f": test_path_1}
    )

    assert not os.path.exists(test_path_1)

    assert project.dryrun_resource("exec::Run")
    project.deploy_resource("exec::Run")
    assert os.path.exists(test_path_1)
    with open(test_path_1) as fh:
        content = fh.read()
        assert "/usr/lib/jvm/jre-1.7.0-openjdk/" in content
        assert "-Dfile.encoding=UTF8 >> /home/inmanta/install.log" in content
        print(content)


def test_in_shell(project: Project, tmpdir: str) -> None:
    test_path_1 = str(tmpdir.join("output"))
    assert os.path.exists(str(tmpdir))
    print(test_path_1)

    project.compile(
        """
import unittest
import exec
import mitogen

host = std::Host(name="server", via=mitogen::Local(), os=std::linux)
exec::Run(host=host, command=exec::in_shell("export PATH=$PATH:/floem; env>%(f)s"))
        """
        % {"f": test_path_1}
    )

    assert not os.path.exists(test_path_1)

    assert project.dryrun_resource("exec::Run")
    project.deploy_resource("exec::Run")
    assert os.path.exists(test_path_1)
    with open(test_path_1) as fh:
        content = fh.read()
        assert "/floem" in content
        print(content)
