from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.trajectory_create_dimensions import TrajectoryCreateDimensions
    from ..models.trajectory_create_original_input_values_type_0 import TrajectoryCreateOriginalInputValuesType0
    from ..models.trajectory_create_trajectory_data_item import TrajectoryCreateTrajectoryDataItem


T = TypeVar("T", bound="TrajectoryCreate")


@_attrs_define
class TrajectoryCreate:
    """Schema for creating a trajectory

    Attributes:
        workflow_id (UUID):
        trajectory_data (list['TrajectoryCreateTrajectoryDataItem']):
        dimensions (TrajectoryCreateDimensions): Display dimensions when trajectory was recorded
        original_input_values (Union['TrajectoryCreateOriginalInputValuesType0', None, Unset]): Original input values
            used when trajectory was created
    """

    workflow_id: UUID
    trajectory_data: list["TrajectoryCreateTrajectoryDataItem"]
    dimensions: "TrajectoryCreateDimensions"
    original_input_values: Union["TrajectoryCreateOriginalInputValuesType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.trajectory_create_original_input_values_type_0 import TrajectoryCreateOriginalInputValuesType0

        workflow_id = str(self.workflow_id)

        trajectory_data = []
        for trajectory_data_item_data in self.trajectory_data:
            trajectory_data_item = trajectory_data_item_data.to_dict()
            trajectory_data.append(trajectory_data_item)

        dimensions = self.dimensions.to_dict()

        original_input_values: Union[None, Unset, dict[str, Any]]
        if isinstance(self.original_input_values, Unset):
            original_input_values = UNSET
        elif isinstance(self.original_input_values, TrajectoryCreateOriginalInputValuesType0):
            original_input_values = self.original_input_values.to_dict()
        else:
            original_input_values = self.original_input_values

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workflow_id": workflow_id,
                "trajectory_data": trajectory_data,
                "dimensions": dimensions,
            }
        )
        if original_input_values is not UNSET:
            field_dict["original_input_values"] = original_input_values

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.trajectory_create_dimensions import TrajectoryCreateDimensions
        from ..models.trajectory_create_original_input_values_type_0 import TrajectoryCreateOriginalInputValuesType0
        from ..models.trajectory_create_trajectory_data_item import TrajectoryCreateTrajectoryDataItem

        d = dict(src_dict)
        workflow_id = UUID(d.pop("workflow_id"))

        trajectory_data = []
        _trajectory_data = d.pop("trajectory_data")
        for trajectory_data_item_data in _trajectory_data:
            trajectory_data_item = TrajectoryCreateTrajectoryDataItem.from_dict(trajectory_data_item_data)

            trajectory_data.append(trajectory_data_item)

        dimensions = TrajectoryCreateDimensions.from_dict(d.pop("dimensions"))

        def _parse_original_input_values(
            data: object,
        ) -> Union["TrajectoryCreateOriginalInputValuesType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                original_input_values_type_0 = TrajectoryCreateOriginalInputValuesType0.from_dict(data)

                return original_input_values_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TrajectoryCreateOriginalInputValuesType0", None, Unset], data)

        original_input_values = _parse_original_input_values(d.pop("original_input_values", UNSET))

        trajectory_create = cls(
            workflow_id=workflow_id,
            trajectory_data=trajectory_data,
            dimensions=dimensions,
            original_input_values=original_input_values,
        )

        trajectory_create.additional_properties = d
        return trajectory_create

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
