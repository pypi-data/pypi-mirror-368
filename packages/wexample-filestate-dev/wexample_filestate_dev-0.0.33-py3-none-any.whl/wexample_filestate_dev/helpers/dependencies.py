from typing import Dict, List, Set, TypeVar, Callable

SortableType = TypeVar('SortableType')

def dependencies_sort(
    items: List[SortableType],
    get_dependencies: Callable[[SortableType], Set[SortableType]]
) -> List[SortableType]:
    """
    Sort a list of items based on their dependencies.
    """
    # Build dependency map
    dependencies: Dict[SortableType, Set[SortableType]] = {
        item: get_dependencies(item)
        for item in items
    }
    
    # Copy dependencies to avoid modifying the original
    remaining_deps = {k: set(v) for k, v in dependencies.items()}
    sorted_items = []
    
    while remaining_deps:
        # Find items with no remaining dependencies
        deployable = [
            item for item, deps in remaining_deps.items()
            if not deps
        ]
        
        if not deployable:
            cycles = [str(item) for item in remaining_deps.keys()]
            raise ValueError(
                f"Circular dependencies detected between: {', '.join(cycles)}"
            )
        
        # Add deployable items to the result (sort for stability)
        sorted_items.extend(sorted(deployable, key=str))
        
        # Remove deployed items
        for item in deployable:
            del remaining_deps[item]
            
        # Remove deployed items from remaining dependencies
        for deps in remaining_deps.values():
            deps.difference_update(deployable)
    
    return sorted_items
