import shlex


class CmdParser:

    def __init__(self, cmd: str):
        try:
            params = shlex.split(cmd)
        except ValueError:
            params = []

        if not params:
            self.name = None
            self.args = None
            return
        self.name = params[0]
        self.args = params[1:]

    def get_cmd_name(self) -> str | None:
        return self.name

    def get_cmd_args(self) -> list[str] | None:
        return self.args
