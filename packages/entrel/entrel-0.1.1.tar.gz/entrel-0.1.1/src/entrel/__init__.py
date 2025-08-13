import tomllib
import dataclasses
import enum
import typing
import itertools

TEMPLATE = r"""
\documentclass{standalone}
\usepackage{tikz}
\usetikzlibrary{shapes}
\usetikzlibrary{positioning}
\usetikzlibrary{matrix}
\usetikzlibrary{calc}
\usetikzlibrary{arrows.meta}
\begin{document}
\tikzset{
  attrs/.style={matrix of nodes, nodes={draw, ellipse, minimum width=2cm, font=\footnotesize}},
  ent/.style={draw, inner sep=2ex},
  weakent/.style={draw, double, double distance=.4ex, inner sep=2ex},
  rel/.style={draw, inner sep=2ex, diamond, aspect=2},
  weakrel/.style={draw, inner sep=1ex, diamond, double, double distance=.4ex, aspect=2},
  isarel/.style={draw, inner sep=.3ex, regular polygon, regular polygon sides=3}
}
\begin{tikzpicture}
%%INSERT%%
\end{tikzpicture}
\end{document}
"""


class LayoutData(typing.TypedDict):
    rows: int
    columns: int
    obj: dict[str, dict[str, typing.Any]]


class DefinitionData(typing.TypedDict):
    entity: dict[str, typing.Any]
    rel: dict[str, typing.Any]
    layout: LayoutData


class AttributeType(enum.Enum):
    REGULAR = "regular"
    KEY = "key"


class RelationshipType(enum.Enum):
    REGULAR = "regular"
    WEAK = "weak"
    ISA = "isa"


class EntityType(enum.Enum):
    REGULAR = "regular"
    WEAK = "weak"


class EntityConnection(enum.Enum):
    EXACTLY_ONE = "exactlyone"
    AT_MOST_ONE = "atmostone"
    MANY = "many"
    ISA_PARENT = "isaparent"
    ISA_CHILD = "isachild"


class AttributeDirection(enum.Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


@dataclasses.dataclass
class Attribute:
    name: str
    type: AttributeType


@dataclasses.dataclass
class Entity:
    identifier: str
    label: str
    attributes: list[Attribute]
    type: EntityType


@dataclasses.dataclass
class Relationship:
    identifier: str
    label: str
    type: RelationshipType
    attributes: list[Attribute]
    entity_connections: list[tuple[EntityConnection, Entity]]


@dataclasses.dataclass
class LayoutObject:
    row_index: int
    column_index: int
    object: Entity | Relationship
    direction: AttributeDirection
    distance: str


@dataclasses.dataclass
class Layout:
    rows: int
    columns: int
    objects: dict[tuple[int, int], LayoutObject]


def generate(definition_file: str, output_file: str, template: str = TEMPLATE) -> None:
    """Generate LaTeX ER diagram from a TOML definition file.

    Args:
        definition_file: Path to the TOML definition file containing the ER diagram data.
        output_file: Path where the generated LaTeX file will be saved.
        template: LaTeX template string to use for the output. Defaults to a predefined template.
    """
    with open(definition_file, "rb") as f:
        data = _validate_data(tomllib.load(f))

    ents = {id_: _parse_entity(id_, ent) for id_, ent in data["entity"].items()}
    rels = {id_: _parse_rel(id_, rel, ents) for id_, rel in data["rel"].items()}
    layout = Layout(
        rows=data["layout"]["rows"],
        columns=data["layout"]["columns"],
        objects={
            (obj["position"][0], obj["position"][1]): LayoutObject(
                row_index=obj["position"][0],
                column_index=obj["position"][1],
                object=ents[id_] if id_ in ents else rels[id_],
                direction=AttributeDirection(obj.get("direction", "right")),
                distance=obj.get("distance", "3cm")
            )
            for id_, obj in data["layout"]["obj"].items()
        },
    )

    diagram_text = "\n".join(
        [_draw_objects(layout), _draw_attributes(layout), _draw_connections(layout)]
    )
    with open(output_file, "w+") as output:
        output_content = template.replace("%%INSERT%%", diagram_text)
        output.write(output_content)


def _validate_data(data: dict[str, typing.Any]) -> DefinitionData:
    if "entity" not in data or "rel" not in data or "layout" not in data:
        raise ValueError("Data must contain 'entity', 'rel', and 'layout' keys.")
    if (
        not isinstance(data["layout"], dict)
        or "rows" not in data["layout"]
        or "columns" not in data["layout"]
    ):
        raise ValueError("Layout must contain 'rows' and 'columns'.")
    return typing.cast(DefinitionData, data)


def _parse_entity(id_: str, ent_dict: dict[str, typing.Any]) -> Entity:
    return Entity(
        identifier=id_,
        label=ent_dict["label"],
        attributes=[_parse_attr(attr) for attr in ent_dict.get("attributes", [])],
        type=EntityType(ent_dict.get("type", "regular")),
    )


def _parse_attr(attribute: str) -> Attribute:
    return Attribute(
        name=attribute.lstrip("*"),
        type=AttributeType.KEY if attribute.startswith("*") else AttributeType.REGULAR,
    )


def _parse_rel(
    id_: str, rel: dict[str, typing.Any], ents: dict[str, Entity]
) -> Relationship:
    return Relationship(
        identifier=id_,
        type=(rel_type := RelationshipType(rel.get("type", "regular"))),
        label="isa" if rel_type == RelationshipType.ISA else rel["label"],
        attributes=[_parse_attr(attr) for attr in rel.get("attributes", [])],
        entity_connections=[_parse_conn(c, ents) for c in rel["entity_connections"]],
    )


def _parse_conn(
    connection: str, ents: dict[str, Entity]
) -> tuple[EntityConnection, Entity]:
    match connection:
        case s if s.startswith("exactlyone-"):
            return (EntityConnection.EXACTLY_ONE, ents[s[len("exactlyone-") :]])
        case s if s.startswith("atmostone-"):
            return (EntityConnection.AT_MOST_ONE, ents[s[len("atmostone-") :]])
        case s if s.startswith("many-"):
            return (EntityConnection.MANY, ents[s[len("many-") :]])
        case s if s.startswith("isaparent-"):
            return (EntityConnection.ISA_PARENT, ents[s[len("isaparent-") :]])
        case s if s.startswith("isachild-"):
            return (EntityConnection.ISA_CHILD, ents[s[len("isachild-") :]])
        case _:
            return (EntityConnection.MANY, ents[connection])


def _draw_objects(layout: Layout) -> str:
    lines = []
    lines.append(r"\matrix[matrix of nodes, row sep=1.5cm, column sep=1cm]{")
    for row in range(layout.rows):
        row_string = ""
        for col in range(layout.columns):
            column_string = ""
            obj = layout.objects.get((row, col))
            if obj:
                type_ = _get_type(obj.object.type)
                id_ = obj.object.identifier
                label = obj.object.label
                column_string += f"\\node[{type_}] ({id_}) {{{label}}}; "
            if col < layout.columns - 1:
                column_string += " & "
            row_string += column_string
        lines.append(row_string + r" \\")
    lines.append("};")
    return "\n".join(lines)


def _draw_attributes(layout: Layout):
    return "\n".join(
        [
            _draw_object_attributes(obj) 
            for row, col in itertools.product(range(layout.rows), range(layout.columns))
            if (obj:=layout.objects.get((row, col))) is not None and obj.object.attributes
        ]
    )

def _draw_object_attributes(obj: LayoutObject) -> str:
    lines ="\n".join([
            _draw_attribute(attr, obj.direction, attr == obj.object.attributes[-1])
            for attr in obj.object.attributes
    ])
    return (
        f"\\matrix ({obj.object.identifier}att) [attrs] at "
        f"{_get_attr_position(obj.direction, obj.object.identifier, obj.distance)}"
        f"{{\n{lines}\n}};"
    )


def _draw_attribute(attr: Attribute, direction: AttributeDirection, is_last: bool) -> str:
    separator = r"\\" if is_last or direction in [AttributeDirection.LEFT, AttributeDirection.RIGHT] else "&"
    text = f"\\underline{{{attr.name}}}" if attr.type == AttributeType.KEY else attr.name
    return f"{text}{separator}"



def _draw_connections(layout: Layout) -> str:
    lines = []
    for row, col in itertools.product(range(layout.rows), range(layout.columns)):
        obj = layout.objects.get((row, col))
        if obj and isinstance(obj.object, Relationship):
            id_ = obj.object.identifier
            for conn_type, entity in obj.object.entity_connections:
                entity_id = entity.identifier
                start_pos = f"({id_}{_get_suffix(conn_type)})"
                end_pos = f"({entity_id})"
                arrow = _get_arrow(conn_type)
                lines.append(f"\\draw[{arrow}] {start_pos} -- {end_pos};")
    return "\n".join(lines)


def _get_suffix(conn_type: EntityConnection) -> str:
    match conn_type:
        case EntityConnection.ISA_PARENT:
            return ".north"
        case EntityConnection.ISA_CHILD:
            return ".south"
        case _:
            return ""


def _get_arrow(conn_type: EntityConnection) -> str:
    match conn_type:
        case EntityConnection.EXACTLY_ONE:
            return r"-{Arc Barb[]}"
        case EntityConnection.AT_MOST_ONE:
            return "->"
        case EntityConnection.MANY:
            return "-"
        case EntityConnection.ISA_PARENT:
            return "-"
        case EntityConnection.ISA_CHILD:
            return "-"
        case _:
            raise ValueError(f"Unknown connection type: {conn_type}")


def _get_attr_position(direction: AttributeDirection, id_: str, distance: str):
    match direction:
        case AttributeDirection.LEFT:
            return f"($({id_}) + (-{distance}, 0)$)"
        case AttributeDirection.RIGHT:
            return f"($({id_}) + ({distance}, 0)$)"
        case AttributeDirection.UP:
            return f"($({id_}) + (0, {distance})$)"
        case AttributeDirection.DOWN:
            return f"($({id_}) + (0, -{distance})$)"
        case _:
            raise ValueError(f"Unknown attribute direction: {direction}")


def _get_type(type_: EntityType | RelationshipType) -> str:
    match type_:
        case EntityType.REGULAR:
            return "ent"
        case EntityType.WEAK:
            return "weakent"
        case RelationshipType.REGULAR:
            return "rel"
        case RelationshipType.WEAK:
            return "weakrel"
        case RelationshipType.ISA:
            return "isarel"
        case _:
            raise ValueError(f"Unknown type: {type_}")
