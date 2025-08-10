from __future__ import annotations
import copy
from typing import Any, Dict, List, get_type_hints
import dataclasses
from gradio.components.base import Component
from gradio_propertysheet.helpers import extract_prop_metadata
from gradio_client.documentation import document

def prop_meta(**kwargs) -> dataclasses.Field:
    """
    A helper function to create a dataclass field with Gradio-specific metadata.
    
    Returns:
        A dataclasses.Field instance with the provided metadata.
    """
    return dataclasses.field(metadata=kwargs)
@document()
class PropertySheet(Component):
    """
    A Gradio component that renders a dynamic UI from a Python dataclass instance.
    It allows for nested settings and automatically infers input types.
    """
    EVENTS = ["change", "input", "expand", "collapse"]

    def __init__(
        self, 
        value: Any | None = None, 
        *,  
        label: str | None = None,
        root_label: str = "General",
        show_group_name_only_one: bool = True,
        disable_accordion: bool = False,
        visible: bool = True,
        open: bool = True,
        elem_id: str | None = None,
        scale: int | None = None,
        width: int | str | None = None,
        height: int | str | None = None,
        min_width: int | None = None,
        container: bool = True,
        elem_classes: list[str] | str | None = None,
        **kwargs
    ):
        """
        Initializes the PropertySheet component.

        Args:
            value: The initial dataclass instance to render.
            label: The main label for the component, displayed in the accordion header.
            root_label: The label for the root group of properties.
            show_group_name_only_one: If True, only the group name is shown when there is a single group.
            disable_accordion: If True, disables the accordion functionality.
            visible: If False, the component will be hidden.
            open: If False, the accordion will be collapsed by default.
            elem_id: An optional string that is assigned as the id of this component in the DOM.
            scale: The relative size of the component in its container.
            width: The width of the component in pixels.
            height: The maximum height of the component's content area in pixels before scrolling.
            min_width: The minimum width of the component in pixels.
            container: If True, wraps the component in a container with a background.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the DOM.
        """
        if value is not None and not dataclasses.is_dataclass(value):
            raise ValueError("Initial value must be a dataclass instance")
        
        # Store the current dataclass instance and its type.
        # These might be None if the component is initialized without a value.
        self._dataclass_value = copy.deepcopy(value) if value is not None else None
        self._dataclass_type = type(value) if dataclasses.is_dataclass(value) else None
        
        self.width = width
        self.height = height
        self.open = open
        self.root_label = root_label
        self.show_group_name_only_one = show_group_name_only_one
        self.disable_accordion = disable_accordion
        
        super().__init__(
            label=label, visible=visible, elem_id=elem_id, scale=scale,
            min_width=min_width, container=container, elem_classes=elem_classes,
            value=self._dataclass_value, **kwargs
        )

    
    @document()
    def postprocess(self, value: Any) -> List[Dict[str, Any]]:
        """
        Converts the Python dataclass instance into a JSON schema for the frontend.

        Crucially, this method also acts as a "state guardian". When Gradio calls it
        with a valid dataclass (e.g., during a `gr.update` that makes the component visible),
        it synchronizes the component's internal state (`_dataclass_value` and `_dataclass_type`),
        ensuring the object is "rehydrated" and ready for `preprocess`.
        
        Args:
            value: The dataclass instance to process.
        Returns:
            A list representing the JSON schema for the frontend UI.
        """
        if dataclasses.is_dataclass(value):
            self._dataclass_value = copy.deepcopy(value)
            # Restore the dataclass type if it was lost (e.g., on re-initialization).
            if self._dataclass_type is None:
                self._dataclass_type = type(value)
        
        current_value = self._dataclass_value

        if current_value is None or not dataclasses.is_dataclass(current_value): 
            return []
            
        json_schema, root_properties = [], []
      
        used_group_names = set()

        # Process nested dataclasses first
        for field in dataclasses.fields(current_value):      
            field_type = get_type_hints(type(current_value)).get(field.name)
            is_nested_dataclass = dataclasses.is_dataclass(field_type) if isinstance(field_type, type) else False

            if is_nested_dataclass:
                group_obj = getattr(current_value, field.name)
                group_props = []
                for group_field in dataclasses.fields(group_obj):
                    metadata = extract_prop_metadata(group_obj, group_field)
                    metadata["name"] = f"{field.name}.{group_field.name}"
                    group_props.append(metadata)
                                
                base_group_name = field.name.replace("_", " ").title()
                unique_group_name = base_group_name
                counter = 2
                # If the name is already used, append a counter until it's unique
                while unique_group_name in used_group_names:
                    unique_group_name = f"{base_group_name} ({counter})"
                    counter += 1
                
                used_group_names.add(unique_group_name) # Add the final unique name to the set
                json_schema.append({"group_name": unique_group_name, "properties": group_props})
            else:
                # Collect root properties to be processed later
                root_properties.append(extract_prop_metadata(current_value, field))
        
        # Process root properties, if any exist
        if root_properties:           
            base_root_label = self.root_label
            unique_root_label = base_root_label
            counter = 2
            # Apply the same logic to the root label
            while unique_root_label in used_group_names:
                unique_root_label = f"{base_root_label} ({counter})"
                counter += 1
            
            # No need to add to used_group_names as it's the last one
            json_schema.insert(0, {"group_name": unique_root_label, "properties": root_properties})

        return json_schema
    
    @document()
    def preprocess(self, payload: Any) -> Any:
        """
        Processes the payload from the frontend to create an updated dataclass instance.

        This method is stateless regarding the instance value. It reconstructs the object
        from scratch using the `_dataclass_type` (which is reliably set by `postprocess`)
        and then applies the changes from the payload.
        
        Args:
            payload: The data received from the frontend, typically a list of property groups.
        Returns:
            A new, updated instance of the dataclass.
        """        
        if self._dataclass_type is None or payload is None:
            return None

        reconstructed_obj = self._dataclass_type()
        value_map = {}

        if isinstance(payload, list):
            for group in payload:
                # We need to handle the potentially renamed root group
                group_name_key = None
                # Find the corresponding field name in the dataclass for this group
                # This logic is a bit complex, it matches "General (Root)" back to the correct field
                potential_root_name = group["group_name"].replace(" (Root)", "")
                if potential_root_name == self.root_label:
                    # This is the root group, properties are at the top level
                    group_name_key = None
                else:
                    for f in dataclasses.fields(reconstructed_obj):
                        if f.name.replace("_", " ").title() == group["group_name"]:
                            group_name_key = f.name
                            break

                for prop in group.get("properties", []):
                    # Reconstruct the full key path
                    full_key = prop["name"]
                    if '.' not in full_key and group_name_key is not None:
                        # This case is less likely with our current postprocess, but is a safeguard
                        full_key = f"{group_name_key}.{prop['name']}"
                    
                    value_map[full_key] = prop["value"]
        
        elif isinstance(payload, dict):
            value_map = payload

        # Populate the fresh object using the flattened value_map
        for field in dataclasses.fields(reconstructed_obj):
            if dataclasses.is_dataclass(field.type):
                group_obj = getattr(reconstructed_obj, field.name)
                for group_field in dataclasses.fields(group_obj):
                    nested_key = f"{field.name}.{group_field.name}"
                    if nested_key in value_map:
                        setattr(group_obj, group_field.name, value_map[nested_key])
            else:
                root_key = field.name
                if root_key in value_map:
                    setattr(reconstructed_obj, root_key, value_map[root_key])

        self._dataclass_value = reconstructed_obj
        return reconstructed_obj
    
    def api_info(self) -> Dict[str, Any]:
        """
        Provides API information for the component for use in API docs.
        """
        return {"type": "object", "description": "A key-value dictionary of property settings."}

    def example_payload(self) -> Any:
        """
        Returns an example payload for the component's API.
        """
        return {"seed": 12345}