from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class FlowDetails:
    """Holds details about a flow.

    Flow (often named Workflow/Job/DAG) is a unit of work in a program.

    Attributes:
        name: Display name, may be a normalized version of the original name
        original_name: Name as defined in the code
        description: Description of the flow
        obj_type: Type of object defining the flow (e.g., function, method)
        obj_name: Name of the object defining the flow (e.g., function name, method name)
        obj_parent_type: Type of container for object defining the flow (e.g. class, module)
        obj_parent: Name of container for flow object (e.g., class name if method, module name if function)
        id: Unique identifier for the flow definition in memory
        module: Module name where the flow is defined
        source_path: Unambiguous path to the source file from the root of the project
        source_relative: Relative path to the source file from some known root
        import_path: Python import path to the source file
        grouping: Desired grouping of the flow in the context of the project (for navigation)
        child_attributes: Additional attributes that can be set by subclasses
    """

    name: str
    original_name: str
    description: str
    obj_type: str
    obj_name: str
    obj_parent_type: str
    obj_parent: str
    id: str
    module: str
    source_path: str
    source_relative: str
    import_path: str
    grouping: List[str]
    child_attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the FlowDetails to a dictionary suitable for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FlowDetails":
        """Create a FlowDetails instance from a dictionary representation."""
        return cls(**data)


class FlowFinder(ABC):
    """Finds flows (units of work/programs) in a given context, with implementations providing specific discovery mechanisms."""

    @abstractmethod
    def find_flows(self) -> List[FlowDetails]:
        """Method to find flows, to be implemented by subclasses."""
        pass

    def __call__(self) -> List[Dict[str, Any]]:
        return [x.to_dict() for x in self.find_flows()]
