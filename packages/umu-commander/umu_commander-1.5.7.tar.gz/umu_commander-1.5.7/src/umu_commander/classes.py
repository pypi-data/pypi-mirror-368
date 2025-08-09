from dataclasses import dataclass
from enum import Enum


@dataclass
class Element:
    group_id: str = ""
    value: str = ""
    info: str = ""

    def as_proton_ver(self) -> "ProtonVer":
        return ProtonVer(self.group_id, self.value, self.info)

    def as_dll_override(self) -> "DLLOverride":
        return DLLOverride(self.info, self.value)


@dataclass
class ProtonVer(Element):
    def __init__(self, dir: str = "", version_num: str = "", user_count: str = ""):
        super().__init__(group_id=dir, value=version_num, info=user_count)

    @property
    def dir(self):
        return self.group_id

    @property
    def version_num(self):
        return self.value

    @property
    def user_count(self):
        return self.info


@dataclass
class DLLOverride(Element):
    def __init__(self, label: str = "", override_str: str = ""):
        super().__init__(group_id="", value=override_str, info=label)

    @property
    def override_str(self):
        return self.value

    @property
    def label(self):
        return self.info


@dataclass
class Value(Element):
    def __init__(self, value: str):
        super().__init__(value=value)


@dataclass
class Group:
    identity: str = ""
    label: str = ""
    elements: list[Element] = list


@dataclass
class ProtonDir(Group):
    @property
    def path(self):
        return self.identity

    @property
    def versions(self) -> list[ProtonVer]:
        return [e.as_proton_ver() for e in self.elements]

    @versions.setter
    def versions(self, value):
        self.elements = value


class ExitCode(Enum):
    SUCCESS = 0
    DECODING_ERROR = 1
    INVALID_SELECTION = 2
