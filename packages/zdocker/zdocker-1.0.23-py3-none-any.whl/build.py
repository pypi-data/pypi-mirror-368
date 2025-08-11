#!/usr/bin/env python3

import argparse
import os
import inspect
import sys
import shutil
import signal
import ctypes


from conanex import util


USER_CTRL_C = 3                         # 3: Ctrl+C
ERROR_SIGTERM = 5                       # 5: SIGTERM

conan_version = util.import_host_compile_env()
if conan_version and conan_version < "2.0.0":
    compile_installed = True
else:
    compile_installed = False


class BuildCommand:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-d', '--docker', default=False,
                                 action='store_true', help='Run zbuild in a docker environment')
        self.parser.add_argument('--docker-args', dest="docker_args", default='',
                                 help='Add argmuemt for Docker')
        self.parser.add_argument('--disable-interactive', default=False,
                                 action='store_true', help="Disable docker interactive mode")
        self.parser.add_argument('--allow-root', default=False,
                                 action='store_true', help="Allow root run to zbuild")
        self.parser.add_argument('--verbose', default=False,
                                 action='store_true', help="Verbose mode, show debugging messages")

        util.update_default_conf("docker", self.parser)
        self.subparsers = self.parser.add_subparsers()

        command = None
        argv = self.parse_args()
        for arg in argv[1:]:
            if not arg.startswith("-"):
                command = arg
                break

        for method_name, method in self.commands().items():
            if command is None or command == method_name:
                parser = method()
                util.update_default_conf(method_name, parser)

    def commands(self):
        cmds = {}
        for m in inspect.getmembers(self, predicate=inspect.ismethod):
            method_name, method = m[0], m[1]
            if method_name.startswith("cmd_"):
                cmds[method_name[4:]] = method
        return cmds

    def parse_args(self):
        argv = [argv for argv in sys.argv]

        cmd = os.path.basename(argv[0])
        if cmd == 'zb':
            count = 0
            argv[0] = os.path.join(os.path.dirname(argv[0]), "zbuild")
            for arg in argv:
                if not arg.startswith("-"):
                    count += 1
            if len(argv) > 1 and argv[1] not in self.commands():
                if '-h' not in argv and '--help' not in argv:
                    argv.insert(1, 'build')

            if util.has_docker():
                argv.insert(1, "-d")
        if 'shell' in argv:
            v = argv.index("shell")
            if v > 0:
                cmd = " ".join(argv[v+1:])
                argv = argv[:v+1]
                if cmd:
                    argv.append(cmd)
        return argv

    def run_command(self):
        argv = self.parse_args()

        opt = self.parser.parse_args(argv[1:])
        if 'func' not in opt:
            self.parser.print_help()
            exit(1)

        if os.getuid() == 0 and not opt.allow_root:
            print(util.ctext.ctext.fmt(util.ctext.ctext.R, "Running zbuild from the root account will be disabled in the next release!"))
            print("Do not allow root to run zbuild!")
            sys.exit(1)

        if opt.func.__name__ in ["conan_gitlab"]:
            if opt.func(opt):
                exit(0)
            exit(1)

        docker_env = opt.docker
        if opt.func.__name__ == "conan_shell":
            docker_env = True

        if not util.in_docker():
            if conan_version is None or conan_version >= "2.0.0":
                docker_env = True

        if util.in_docker() or not docker_env:
            if conan_version is None:
                print("Docker environment exception, please update the docker image")
            elif conan_version < "2.0.0":
                if not opt.func(opt):
                    exit(1)
            elif conan_version >= "2.0.0":
                print("Conan 2.0 is not supported, Please install conan version 1.59.0:")
                print("pip install conan-zbuild==1.65.0 -U")
        elif docker_env and shutil.which('docker'):
            exec_argv = [os.path.basename(argv[0])]
            if opt.disable_interactive:
                exec_argv.append('--disable-interactive')
            if opt.allow_root:
                exec_argv.append('--allow-root')
            for key in self.subparsers.choices.keys():
                for j in range(len(argv)):
                    if argv[j] == key:
                        if key == 'shell':
                            exec_argv.append(key)
                            for v in argv[j + 1:]:
                                exec_argv.append('"' + v + '"')
                        else:
                            exec_argv.extend(argv[j:])
                        break
            if opt.func.__name__ in ['conan_run', 'conan_shell']:
                username = os.getlogin()
            else:
                username = 'zbuild'
            username = os.getenv("DOCKER_USER") or username
            DockerRunner(opt, username).run(exec_argv)
        else:
            print('You need to install the Docker or linux development environment.')

    def cmd_shell(self):
        def conan_shell(args):
            if not args.command:
                args.command.append("/bin/zsh")
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)
            return os.system(" ".join(args.command)) == 0

        shell_parser = self.subparsers.add_parser(
            'shell', help="Execute Docker shell commands")
        shell_parser.set_defaults(func=conan_shell)
        shell_parser.add_argument('command', default=[], nargs='*',
                                  help="shell command, For example: ls")
        return shell_parser

    def run(self):
        def ctrl_c_handler(_, __):
            sys.exit(USER_CTRL_C)

        def sigterm_handler(_, __):
            sys.exit(ERROR_SIGTERM)

        libc = ctypes.CDLL('libc.so.6')
        PR_SET_PDEATHSIG = 1
        if libc.prctl(PR_SET_PDEATHSIG, signal.SIGTERM) != 0:
            print("Failed to set PR_SET_PDEATHSIG")
            return

        signal.signal(signal.SIGINT, ctrl_c_handler)
        signal.signal(signal.SIGTERM, sigterm_handler)
        try:
            self.run_command()
        except Exception as exc:
            exec_name = exc.__class__.__name__
            if (not os.getenv("ZB_DEBUG")) and exec_name in [
                            'ZbuildException', 'ConanException', 'FileNotFoundError',
                            'DockerException', 'KeyboardInterrupt']:
                for arg in exc.args:
                    if isinstance(arg, tuple):
                        for a in arg:
                            print(a)
                    else:
                        print(arg)
            else:
                import traceback
                traceback.print_exc()
            sys.exit(1)
        sys.exit(0)


def main():
    BuildCommand().run()
