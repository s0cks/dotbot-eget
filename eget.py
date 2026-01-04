import subprocess, dotbot


def exec_command(cmd):
    command = cmd if isinstance(cmd, list) else [cmd]
    result = subprocess.run(
        [" ".join(command)], shell=True, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def which(cmd):
    return exec_command(["which", cmd])


def eget_version(exec):
    return exec_command([exec, "--version"])


class EgetItem:
    def __init__(
        self,
        item,
        to=None,
        pre_releases=False,
        source=False,
        tag=None,
        quiet=False,
        download_only=False,
        show_sha256=False,
        verify_sha256=None,
        disable_ssl=False,
    ):
        if isinstance(item, str):
            self._item = item
            self._to = to
            self._pre_releases = pre_releases
            self._source = source
            self._tag = tag
            self._quiet = quiet
            self._download_only = download_only
            self._show_sha256 = show_sha256
            self._verify_sha256 = verify_sha256
            self._disable_ssl = disable_ssl
        elif isinstance(item, dict):
            if not "item" in item:
                raise Exception(f"invalid eget item: {item}, missing item key")
            self._item = item["item"]
            self._to = item["to"] if "to" in item else to
            self._pre_releases = (
                item["pre_releases"] if "pre_releases" in item else pre_releases
            )
            self._source = item["source"] if "source" in item else source
            self._tag = item["tag"] if "tag" in item else tag
            self._quiet = item["quiet"] if "quiet" in item else quiet
            self._download_only = (
                item["download_only"] if "download_only" in item else download_only
            )
            self._show_sha256 = (
                item["show_sha256"] if "show_sha256" in item else show_sha256
            )
            self._verify_sha256 = (
                item["verify_sha256"] if "verify_sha256" in item else verify_sha256
            )
            self._disable_ssl = (
                item["disable_ssl"] if "disable_ssl" in item else disable_ssl
            )
        else:
            raise Exception(f"invalid eget item: {item}")

    def get_command(self):
        command = []
        if self._to != None:
            command.append("--to=" + self._to)
        if self._tag != None:
            command.append("--tag=" + self._tag)
        if self._pre_releases:
            command.append("--pre-release")
        if self._source:
            command.append("--source")
        if self._quiet:
            command.append("--quiet")
        if self._download_only:
            command.append("--download-only")
        if self._show_sha256:
            command.append("--sha256")
        if self._verify_sha256 != None:
            command.append("--verify-sha256=" + self._verify_sha256)
        if self._disable_ssl:
            command.append("--disable-ssl")
        command.append(self._item)
        return command

    def __str__(self):
        return self._item


class DotbotPlugin(dotbot.Plugin):
    __directive__ = "eget"
    __version__ = "0.0.1"

    def __init__(self, ctx):
        super().__init__(ctx)
        try:
            self._eget_exec = which("eget")
        except Exception as ex:
            raise Exception(f"failed to find eget executable in PATH", ex)
        try:
            version = eget_version(self._eget_exec)
            self._log.debug(f"found eget v{version}: {self._eget_exec}")
        except Exception as ex:
            raise Exception(f"failed to get eget version from: {self._eget_exec}")

    def can_handle(self, directive):
        return directive == self.__directive__

    def handle(self, directive, data):
        if not self.can_handle(directive):
            return False

        if isinstance(data, str):
            # single instance get
            self._eget(EgetItem(data))
            return True
        elif isinstance(data, list):
            for item in data:
                self._eget(EgetItem(item))
            return True
        elif not isinstance(data, dict):
            raise Exception(f"invalid eget data: {data}")
        self._dest = data["to"] if "to" in data else None
        if not "items" in data:
            raise Exception(f"data {data} needs key 'items'")
        for item in data["items"]:
            self._eget(EgetItem(item, to=self._dest))
        return True

    def _eget(self, item):
        command = [self._eget_exec]
        command += item.get_command()
        self._log.debug(f"executing eget w/ args: {' '.join(command)}")
        exec_command(command)
