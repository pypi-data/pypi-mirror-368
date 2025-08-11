import datetime
import os
import pathlib
import sys
import shutil
import atexit
import argparse
import textwrap
import time
import socket
import errno

from conanex import util

docker_url = "10.0.11.6:8989/zbuild/ubuntu-24.04-x86_64:v1.6.4"


class Extender(argparse.Action):
    """Allows using the same flag several times in command and creates a list with the values.
    For example:
        conan install MyPackage/1.2@user/channel -o qt:value -o mode:2 -s cucumber:true
      It creates:
          options = ['qt:value', 'mode:2']
          settings = ['cucumber:true']
    """
    def __call__(self, parser, namespace, values, option_strings=None):  # @UnusedVariable
        # Need None here in case `argparse.SUPPRESS` was supplied for `dest`
        dest = getattr(namespace, self.dest, None)
        if not hasattr(dest, 'extend') or dest == self.default:
            dest = []
            setattr(namespace, self.dest, dest)
            # if default isn't set to None, this method might be called
            # with the default as `values` for other arguments which
            # share this destination.
            parser.set_defaults(**{self.dest: None})

        if isinstance(values, str):
            dest.append(values)
        elif values:
            try:
                dest.extend(values)
            except ValueError:
                dest.append(values)


def get_volume_path(path):
    paths = [f"{path}:{path}"]
    while path != "/":
        if os.path.islink(path):
            realpath = os.path.realpath(path)
            paths.append(f"{realpath}:{realpath}")
        path = os.path.dirname(path)
    return paths


def load(path, binary=False, encoding="auto"):
    """ Loads a file content """
    with open(path, 'rb') as handle:
        return handle.read()


def save(path, content, only_if_modified=False, encoding="utf-8"):
    """
    Saves a file with given content
    Params:
        path: path to write file to
        content: contents to save in the file
        only_if_modified: file won't be modified if the content hasn't changed
        encoding: target file text encoding
    """
    dir_path = os.path.dirname(path)
    if not os.path.isdir(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as error:
            if error.errno not in (errno.EEXIST, errno.ENOENT):
                raise OSError("The folder {} does not exist and could not be created ({})."
                              .format(dir_path, error.strerror))
        except Exception:
            raise

    new_content = content

    if only_if_modified and os.path.exists(path):
        old_content = load(path, binary=True, encoding=encoding)
        if old_content == new_content:
            return

    with open(path, "wb") as handle:
        handle.write(new_content)


def save_if_not_exists(path, content):
    if not os.path.exists(path):
        save(path, content)


def generate_temp_name():
    username = os.getlogin()
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = '{:04x}'.format(abs(hash(timestamp) % (1 << 16)))
    temp_filename = f"{username}_{timestamp}_{random_part}"

    return temp_filename


class DockerContainer:
    def __init__(self):
        uid = os.getuid()
        gid = os.getgid()

        self.name = generate_temp_name()
        self.image = os.getenv("DOCKER_IMAGE") or docker_url
        self.version = self.image.split(':')[-1].lstrip('v')
        self.working_dir = os.getenv("PWD")
        self.user = f"{uid}:{gid}"
        self.stdin_open = True
        self.volumes = get_volume_path(self.working_dir)
        home_dir = os.path.expanduser('~')
        if home_dir != self.working_dir:
            self.volumes.append(f"{home_dir}:{home_dir}")

        self.devices = []
        self.environment = []
        self.ports = {}
        self.cap_add = ['SYS_ADMIN']
        self.network_mode = None
        self.command = ''
        self.tty = sys.stdout.isatty()
        self.auto_remove = True
        self.privileged = True
        self.hostname = 'docker'
        self.set_env("DOCKER_IMAGE", self.image)
        self.set_env("DOCKER_VERSION", self.version)

    def parse_args(self, text):
        parser = argparse.ArgumentParser()
        parser.add_argument('--name', default=self.name,
                            help="Assign a name to the container")
        parser.add_argument('--hostname', default=self.hostname,
                            help="Assign a hostname to the container")
        parser.add_argument('-e', '--env', default=[], nargs='*',
                            action=Extender, help="Set environment variables")
        parser.add_argument('-d', '--device', default=[], nargs='*',
                            action=Extender, help="Add a host device to the container")
        parser.add_argument('-v', '--volume', default=[], nargs='*',
                            action=Extender, help="Bind mount a volume")
        parser.add_argument('-p', '--publish', default=[], nargs='*',
                            action=Extender, help="Publish a container's ports to the host")
        parser.add_argument('--network', default=None, help="Connect a container to a network")
        args = parser.parse_args(text)

        self.environment.extend(args.env)
        self.devices.extend(args.device)
        self.volumes.extend(args.volume)
        for port in args.publish:
            self.add_port(port)
        self.network_mode = args.network or self.network_mode
        self.name = args.name or self.name
        if args.hostname == "_":
            self.hostname = socket.gethostname()
        else:
            self.hostname = args.hostname or self.hostname

    def add_port(self, publish):
        parts = publish.split(':')
        if len(parts) == 2:
            port_protocol = parts[1].split('/')
            key, val = port_protocol[0] + '/' + (port_protocol[1] if len(port_protocol) > 1 else 'tcp'), int(parts[0])
        elif len(parts) == 3:
            port_protocol = parts[2].split('/')
            key, val = port_protocol[0] + '/' + (port_protocol[1] if len(port_protocol) > 1 else 'tcp'), (parts[0], int(parts[1]))
        else:
            raise ValueError('Invalid publish format')
        self.ports[key] = val

    def set_env(self, name, value=None):
        if value is None:
            value = os.getenv(name)
        if value:
            self.environment.append(f"{name}={value}")

    def run(self, verbose=False):
        import docker
        import dockerpty
        from docker.errors import ImageNotFound
        from docker.models.containers import Container

        def verbose_show(prompt, values):
            if values:
                print(util.ctext.fmt(util.ctext.B, prompt))
                if isinstance(values, list):
                    for v in values:
                        print("  ", v)
                elif isinstance(values, dict):
                    for k, v in values.items():
                        print(f"  {k}: {v}")
                elif isinstance(values, str):
                    print("  ", values)

        docker_client = docker.from_env()

        if self.network_mode == 'host':
            self.ports = None

        self.devices = list(set(self.devices))
        self.volumes = list(set(self.volumes))
        self.environment = list(set(self.environment))
        if verbose:
            verbose_show("Devices:", self.devices)
            verbose_show("Volumes:", self.volumes)
            verbose_show("Environment:", self.environment)
            verbose_show("net ports:", self.ports)
            verbose_show("kernel capabilities:", self.cap_add)
            for k, v in self.__dict__.items():
                if isinstance(v, str):
                    verbose_show(k + ':', v)

        try:
            container: Container = docker_client.containers.get(self.name)
            container.remove(force=True)
        except Exception:
            pass

        try:
            self.container: Container = docker_client.containers.create(**self.__dict__)
        except ImageNotFound:
            docker_client.images.pull(self.image)
            self.container: Container = docker_client.containers.create(**self.__dict__)

        status_code = 0
        try:
            dockerpty.start(docker_client.api, self.container.id)
            status = self.container.wait()
            status_code = status['StatusCode']
        except Exception:
            pass
        finally:
            self.container_remove(True)
        return status_code

    def container_remove(self, force=True):
        if hasattr(self, 'container') and self.container:
            try:
                self.container.remove(force=force)
                self.container = None
            except Exception:
                pass

    def __del__(self):
        self.container_remove(True)


class DockerRunner(object):
    def __init__(self, opt, username=None):
        self.opt = opt
        self.USER = username or "zbuild"
        self.UID = os.getuid()
        self.GID = os.getgid()
        self.home = os.path.expanduser('~')

        self.docker = DockerContainer()

        self.user_passwd_group()
        self.local_path()
        self.parser_opts(opt)

    def parser_opts(self, opt):
        if hasattr(opt, 'func') and (opt.func.__name__ in ["conan_shell", "conan_run"]):
            self.docker.stdin_open = not opt.disable_interactive
            if os.path.exists('/dev/net/tun'):
                self.docker.devices.append('/dev/net/tun:/dev/net/tun')
                self.docker.cap_add.append('NET_ADMIN')
                self.docker.network_mode = 'host'

        if hasattr(opt, 'serial_device'):
            serial_device = util.probe_serial_device(opt.serial_device)
            if serial_device and os.path.exists(serial_device):
                self.docker.devices.append(serial_device)

        if hasattr(opt, 'ethernet'):
            ip, _ = util.get_enternet_ip(opt.ethernet)
            if ip:
                host_ip_file = os.path.join(self.home, '.docker_local/hostconf')
                with open(host_ip_file, 'w', encoding='utf-8') as file:
                    file.write(ip.address + ':' + ip.netmask)

        if hasattr(opt, 'docker_args') and opt.docker_args:
            args = opt.docker_args.split()
            if args:
                self.docker.parse_args(args)

        if hasattr(opt, 'socat') and opt.socat:
            def kill_socat_proc():
                if hasattr(self, 'socat_proc') and self.socat_proc:
                    util.subprocess_terminate(self.socat_proc)
                    self.socat_proc.wait()
                    self.socat_proc = None

            socat = shutil.which('socat')
            if not socat:
                print('socat not found!')
                sys.exit(1)
            if os.path.exists(opt.socat):
                os.remove(opt.socat)

            qemu_pty = "qemu_pty_" + str(os.getuid())
            tmp_qemu_pty = f"/tmp/{qemu_pty}"
            if os.path.exists(tmp_qemu_pty):
                os.remove(tmp_qemu_pty)

            cmd = f'{socat} -dd pty,raw,echo=0,link={tmp_qemu_pty},ignoreeof,mode=660 ' \
                  f'pty,raw,echo=0,link={opt.socat},ignoreeof,mode=660'
            _, self.socat_proc = util.subprocess_execute(cmd, wait_return=False)
            atexit.register(kill_socat_proc)
            while True:
                if os.path.exists(tmp_qemu_pty):
                    break
                time.sleep(0.5)
            pts_1 = os.readlink(tmp_qemu_pty)
            self.docker.volumes.append(f"{pts_1}:/dev/{qemu_pty}")

        if hasattr(opt, 'env'):
            for env in opt.env:
                key, name = env.split("=")
                if 'source-path' in key:
                    source_path = os.path.realpath(os.path.expanduser(name))
                    if not os.path.exists(source_path):
                        raise Exception(f"source-path {source_path} not exists")
                    self.docker.volumes.append(f"{source_path}:{source_path}")

    def local_path(self):
        LOCAL_PATH = os.path.join(self.home, '.docker_local')
        BOARD_YML = os.path.join(self.home, '.local/board.yml')
        SSH_CFG_FILE = os.path.join(self.home, '.ssh/zbuild_sshcfg')
        BASHRC_FILE = os.path.join(LOCAL_PATH, '.bashrc')
        ZSHRC_FILE = os.path.join(LOCAL_PATH, '.zshrc')
        HOSTS_FILE = os.path.join(LOCAL_PATH, '.hosts')
        build_cmd_file = pathlib.Path(LOCAL_PATH, 'bin/zbuild')
        build_cmd_file.parent.mkdir(parents=True, exist_ok=True)

        self.docker.set_env('PATH', f"{self.home}/.local/bin:/usr/local/riscv-toolchain/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")
        self.docker.set_env('https_proxy')
        self.docker.set_env('http_proxy')
        self.docker.set_env('http_proxy')
        self.docker.set_env('BOARD_NAME')

        for env, value in os.environ.items():
            if env.startswith("ZB_") or env in [
                "MAIN_SERVER_ADDR",
                "MAKE_PROGRAM",
                "CONAN_USER_HOME",
                "ARCH",
                "CROSS_COMPILE",
            ]:
                self.docker.set_env(env, value)
            if env.startswith("CONAN_"):
                self.docker.set_env(env, value)

        conan_user_home = os.getenv('CONAN_USER_HOME')
        if conan_user_home:
            self.docker.volumes.append(f"{conan_user_home}:{conan_user_home}")
        if os.path.exists("/home/public"):
            self.docker.volumes.append("/home/public:/home/public")

        save_if_not_exists(BASHRC_FILE, "PS1='\\[\\e[01;32m\\]\\u@\\h\\[\\e[m\\]:\\[\\e[01;34m\\]\\w\\[\\e[m\\]\\$ '\n")
        save_if_not_exists(SSH_CFG_FILE, textwrap.dedent("""\
            Host *
              StrictHostKeyChecking no
        """))
        save_if_not_exists(ZSHRC_FILE, textwrap.dedent("""\
            ZSH_DISABLE_COMPFIX=true
            source /usr/share/zsh/config/zshrc
            export PROMPT='$CYAN%n@$YELLOW$(hostname):$FG[039]$GREEN$(_fish_collapsed_pwd)%f > '
        """))
        save_if_not_exists(HOSTS_FILE, load("/etc/hosts") + "127.0.1.1 docker\n")

        self.docker.volumes.extend([
            f"/dev/null:{self.home}/.profile",
            f"{LOCAL_PATH}:{self.home}/.local",
            f"{SSH_CFG_FILE}:{self.home}/.ssh/config",
            f"{BASHRC_FILE}:{self.home}/.bashrc",
            f"{ZSHRC_FILE}:{self.home}/.zshrc",
            f"{HOSTS_FILE}:/etc/hosts",
            "/schema:/schema",
            "/tmp:/tmp",
        ])

        localtime_file = os.path.realpath("/etc/localtime")
        if os.path.exists(localtime_file):
            self.docker.volumes.append(f"{localtime_file}:/etc/localtime")

        timezone_file = os.path.realpath("/etc/timezone")
        if os.path.exists(timezone_file):
            self.docker.volumes.append(f"{timezone_file}:/etc/timezone")

        if os.path.isfile(BOARD_YML):
            self.docker.volumes.append(f"{BOARD_YML}:{BOARD_YML}")

    def user_passwd_group(self):
        PASSWD_FILE = os.path.join(self.home, '.local/passwd')
        GROUP_FILE = os.path.join(self.home, '.local/group')
        save(PASSWD_FILE, textwrap.dedent(f"""\
            root:x:0:0:root:/root:/bin/bash
            {self.USER}:x:{self.UID}:{self.GID}:,,,:{self.home}:/bin/zsh
        """), only_if_modified=True)
        save(GROUP_FILE, textwrap.dedent(f"""\
            root:x:0:
            dialout:x:20:{self.USER}
            {self.USER}:x:{self.GID}:
        """), only_if_modified=True)
        self.docker.volumes.extend([
            f"{PASSWD_FILE}:/etc/passwd:ro",
            f"{GROUP_FILE}:/etc/group:ro",
            f"{GROUP_FILE}:/etc/group-:ro",
        ])

    def run(self, args):
        if sys.stdout.isatty() and self.docker.hostname == 'docker':
            print("Running in Docker %s ..." % self.docker.image)

        for arg in args:
            if ' ' in arg:
                arg = '"' + arg + '"'
            self.docker.command += ' ' + arg

        status_code = self.docker.run(self.opt.verbose)

        sys.exit(status_code)
