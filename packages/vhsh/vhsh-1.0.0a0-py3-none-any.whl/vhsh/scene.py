import re
import logging
from typing import get_args, Generic, Iterable
from pathlib import Path
from enum import StrEnum
from dataclasses import dataclass

from .types import (
    GLSLBool, GLSLInt, GLSLFloat, GLSLVec2, GLSLVec3, GLSLVec4,
    UniformT, UniformLike,
)


logger = logging.getLogger(__name__)


class ParameterParserError(ValueError): ...


class Widget(StrEnum):
    COLOR = "color"
    LOG = "log"
    DRAG = "drag"


@dataclass
class Parameter(UniformLike, Generic[UniformT]):
    name: str
    type: str
    value: UniformT  # annotate optional param, but always set
    default: UniformT | None
    range: tuple[float, float, float] | None
    widget: Widget | None
    midi: int | None  # TODO -> controls: list[int]

    # delete everything but the default setting at the bottom? _type not needed
    def __post_init__(self):
        # TODO default step is dropped if not passed
        match self.type:
            case 'bool':
                _type = GLSLBool
                self.default = self.default or True
                self.range = None
            case 'int':
                _type = GLSLInt
                self.default = self.default or 1
                if self.range is None:
                    self.range = (0, 100, 1)
                elif len(self.range) == 2:
                    self.range = (*self.range, 1)
            case 'float':
                _type = GLSLFloat
                self.default = self.default or 1.0
                if self.range is None:
                    self.range = (0.0, 1.0, 0.01)
                elif len(self.range) == 2:
                    self.range = (*self.range, 0.01)
            case str() as t if t.startswith('float['):
                try:
                    m = re.match(r'float\[(\d+)\]', self.type)
                    length = int(m.group(1))  # pyright: ignore[reportOptionalMemberAccess]
                except (AttributeError, ValueError) as e:
                    raise ParameterParserError(
                        f"Unable to parse float array type '{self.type}': {e}"
                    ) from e
                _type = (float,) * length
                self.default = self.default or (0.0,) * length  # type: ignore
                self.range = None
            case 'vec2':
                _type = GLSLVec2
                self.default = self.default or (1.,)*2  # type: ignore
                if self.range is None:
                    self.range = (0.0, 1.0, 0.01)
                elif len(self.range) == 2:
                    self.range = (*self.range, 0.01)
            case 'vec3':
                _type = GLSLVec3
                self.default = self.default or (1.,)*3  # type: ignore
                if self.range is None:
                    self.range = (0.0, 1.0, 0.01)
                elif len(self.range) == 2:
                    self.range = (*self.range, 0.01)
            case 'vec4':
                _type = GLSLVec4
                self.default = self.default or (1.,)*4  # type: ignore
                if self.range is None:
                    self.range = (0.0, 1.0, 0.01)
                elif len(self.range) == 2:
                    self.range = (*self.range, 0.01)
            case _:
                raise NotImplementedError(
                    f"Uniform type '{self.type}' not implemented:"
                    f" {self.name} ({self.value})")

        uniform_type = get_args(_type) or _type
        value_type = (tuple(type(elem) for elem in self.default)
                      if isinstance(self.default, Iterable)
                      else type(self.default))
        if  value_type != uniform_type:
            raise ParameterParserError(
                f"Uniform '{self.name}' defined as"
                f" '{self.type}' ({uniform_type}), but provided value"
                f" has type '{value_type}': {self.default!r}")

        if self.value is None:
            self.value = self.default

    def __str__(self) -> str:
        s = f"uniform {self.type} {self.name};  //"
        if self.widget is not None:
            s += f' <{self.widget}>'
        s += f" ={str(self.value).replace(' ', '')}"
        if self.range is not None:
            s += f" {str(list(self.range)).replace(' ', '')}"
        if self.midi is not None:
            s += f' #{self.midi}'
        return s

    @classmethod
    def from_def(cls, definition: str) -> "Parameter":
        # TODO take line number, better error messages
        try:
            matches = re.search(
                # TODO why ^(?!\/\/)\s* not working to ignore comments?
                (R'uniform\s+(?P<type>[\w\[\]]+)\s+(?P<name>\w+)\s*;'
                 R'(?:\s*//\s*(?:'
                 R'(?P<widget><\w+>)?\s*)?'
                 R'(?P<default>=(?:\S+|\([^\)]+\)))?'
                 R'\s*(?P<range>\[[^\]]+\])?'
                 R'\s*(?P<midi>#\d+)?'
                 R')?'),
                definition
            )
            type_, name, widget, default_s, range_s, midi = matches.groups()
        except Exception as e:
            raise ParameterParserError(
                f"Syntax error in metadata defintion: {definition}") from e

        if widget is not None:
            try:
                widget = Widget(widget.strip('<>'))
            except Exception as e:
                raise ParameterParserError(
                    f"Unknown widget type '{widget}'") from e

        try:
            # TODO ast.literal_eval
            default = (eval(default_s.removeprefix('='))
                        if default_s
                        else None)
        except SyntaxError as e:
            raise ParameterParserError(
                f"Invalid 'default' metadata for uniform"
                f" '{name}': {e}: {default_s}"
            ) from e

        try:
            range = eval(range_s) if range_s else None
        except SyntaxError as e:
            raise ParameterParserError(
                f"Invalid 'range' metadata for uniform"
                f" '{name}': {e}: {range_s!r}"
            ) from e

        if midi is not None:
            try:
                midi = int(midi.removeprefix('#'))
            except ValueError as e:
                raise ParameterParserError(
                    f"Invalid 'midi' metadata for uniform"
                    f" '{name}': {e}: {midi!r}"
                ) from e

        return Parameter(name=name,
                         value=default,
                         type=type_,
                         default=default,
                         range=range,
                         widget=widget,
                         midi=midi)

    def set_value_normalized(self, value: float):
        if self.range is None:
            raise ValueError("Only parameters with .range can be set normalized")
        min_, max_, _ = self.range
        new_value = min_ + value * (max_ - min_)
        if self.type == 'int':
            new_value = int(round(new_value))
        self.value = new_value


@dataclass
class Preset:
    name: str
    index: int
    parameters: dict[str, Parameter]

    def __str__(self) -> str:
        # to Preset.__str__
        presets = f"/// // {self.name}\n"
        presets += '\n'.join(f"/// {parameter}"
                             for parameter in self.parameters.values())
        presets += '\n'
        return presets


class Scene:
    def __init__(self, path: Path):
        self.path = path
        self.name = self.path.stem.replace('_', ' ').replace('-', ' ').title()
        self.reload()

    def __str__(self) -> str:
        # TODO ext
        return self.path.name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.path}>"

    # TODO reload
    @staticmethod
    def _read_file(path: Path) -> str:
        with open(path) as f:
            return f.read()

    @staticmethod
    def _load_presets(source: str) -> list[Preset]:
        presets = [Preset(name="<current>", index=0, parameters={})]
        for n, line in enumerate(source.split('\n')):
            line = line.strip()

            # <current> uniforms
            if line.startswith('uniform'):
                parameter = Parameter.from_def(line)
                presets[0].parameters[parameter.name] = parameter

            # presets
            elif line.startswith('///'):
                line_content = line.lstrip('/ ').strip()
                if line.startswith('/// uniform'):
                    parameter = Parameter.from_def(line_content)
                    presets[-1].parameters[parameter.name] = parameter

                else:
                    index = len(presets)
                    presets.append(Preset(name=line_content or str(index),
                                          index=index,
                                          parameters={}))

        return presets

    def reload(self):
        self.source = self._read_file(self.path)
        self._preset_index = 0
        self.presets = self._load_presets(self.source)

    @property
    def parameters(self) -> dict[str, Parameter]:
        current_preset = self.presets[self.preset_index]
        return current_preset.parameters

    @property
    def preset_index(self):
        return self._preset_index

    @preset_index.setter
    def preset_index(self, value):
        self._preset_index = value % len(self.presets)
        logger.info("current preset: %s",
                    self.presets[self.preset_index])

    def prev_preset(self, n: int = 1):
        self.preset_index = (self.preset_index - n) % len(self.presets)

    def next_preset(self, n: int = 1):
        self.preset_index = (self.preset_index + n) % len(self.presets)

    def write_file(self, new_preset: str | None = None):
        if new_preset is not None:
            self.presets.append(Preset(name=new_preset,
                                       parameters=self.parameters.copy(),
                                       index=len(self.presets)-1))

        presets = '\n'.join(str(preset) for preset in self.presets[1:]) + '\n'
        lines = [line for line in self.source.splitlines()
                 if not line.startswith('///')]
        self.source = presets + '\n'.join(lines) + '\n'

        if self._preset_index == 0:
            for parameter in self.parameters.values():
                parameter.default = parameter.value
                self.source = re.sub(f'^uniform \\w+ {parameter.name}.*$',
                                     str(parameter),
                                     self.source,
                                     flags=re.MULTILINE)

        self.path.write_text(self.source)
        logger.info(f"wrote presets to '{self.path}'")
