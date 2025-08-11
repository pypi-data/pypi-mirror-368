"""
Please, read this to get used to (and understand) the jargon used in the code of this module.

Custom utilities for reading `.yaml` files, specifically, report templates

- A `.yaml` file is represented internally as a `MappingNode` *object*
- A `MappingNode` has a `value` *attribute*, that is a **list of 2-tuples**
- Each tuple on the list is composed by two `Node` *objects*.
    - A `MappingNode` is a *subclass* of a `Node` by the way.
    - Another subclass of of `Node` is `ScalarNode`, more about that later.
- The first `Node` of the tuple is called *key node*.
- The second `Node` of the tuple is called *value node*.

Example:

Given this yaml document snippet

```yaml
key1: "value1"
key2: !custom_tag
  subkey: "subvalue"
```

It will be represented as a `MappingNode` whose `value` attribute will be a list of length 2 like the following

- (`key_node1`, `value_node1`)
- (`key_node2`, `value_node2`)

Let's analyze it:

- `key_node1` is a `ScalarNode` object, which has a `value` attribute of "key1" and and *implicit* `tag` attribute indicating it is a string. `value_node1` is similar, but with a `value` of "value1"

- `key_node2` is similar to the previously analyzed nodes, but `value_node2` is, instead of a `ScalarNode`, another `MappingNode`.
    - This `MappingNode` object has an *explicit* and *custom* `tag` attribute called "!custom_tag". It is customary to name custom tags starting with "!".
    - The `value` attribute is a list of length 1 containing a tuple of `ScalarNodes` as the previously analyzed.
"""

from collections.abc import Hashable
from io import TextIOWrapper as _ReadStream
from pathlib import Path
from typing import Any

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode

# implicit tag for string `ScalarNode`
STR_TAG = "tag:yaml.org,2002:str"

type NodeContents = list[tuple[Node, Node]]


def _to_mapping_node(scalar_node: ScalarNode) -> MappingNode:
    return MappingNode(tag=scalar_node.tag, value=[])


class TemplateLoader(yaml.FullLoader):
    """This is a custom `.yaml` file loader to make our life easier when reading report templates."""

    def __init__(self, stream: _ReadStream):
        """Remember the path of the file it is reading"""
        super().__init__(stream)
        self._path: Path = Path(stream.name).parent

    def construct_mapping(
        self, node: MappingNode, deep: bool = False
    ) -> dict[Hashable, Any]:
        """
        This function it is not meant to be called directly by us, it will usually be called indirectly by code such as `yaml.load(file, Loader=loader)`.

        For each `MappingNode` with a custom tag in the `.yaml` file, insert an additional tuple in its `value` attribute with an "id" string `ScalarNode` as *key node* and the same value as its associated *key node*.

        For example, `.yaml` file

        ```yaml
        key: !custom_tag
            subkey: "subvalue"
        ```

        will be transformed to:

        ```yaml
        key: !custom_tag
            id: key
            subkey: "subvalue"
        ```

        Parameters
        ----------
        node : MappingNode
            Current `MappingNode` being parsed.
        deep : bool, optional
            Controls if all the child nodes should be built recursively or only shallowly, by default False

        Returns
        -------
        dict[Hashable, Any]
            Result dictionary
        """
        mapping: dict[Hashable, Any] = {}
        node_contents: NodeContents = node.value

        for subkey_node, subvalue_node in node_contents:
            subkey: str = self.construct_object(subkey_node, deep=deep)
            if subvalue_node.tag.startswith("!"):
                if isinstance(subvalue_node, ScalarNode):
                    subvalue_node = _to_mapping_node(subvalue_node)
                id_name = ScalarNode(tag=STR_TAG, value="id")
                id_value = ScalarNode(tag=STR_TAG, value=str(subkey))
                subcontents: NodeContents = subvalue_node.value
                subcontents.insert(0, (id_name, id_value))
            value = self.construct_object(subvalue_node, deep=deep)
            mapping[subkey] = value

            # artificial imports of other `.yaml` files
            if subkey == "imports":
                imports: NodeContents = subvalue_node.value
                self.imports = {}
                for asset_key_node, asset_path_node in imports:
                    asset_key: str = self.construct_object(
                        asset_key_node, deep=deep
                    )
                    asset_path: Path = Path(
                        self.construct_object(asset_path_node, deep=deep)
                    )
                    self.imports[asset_key] = self._path / asset_path
        return mapping
