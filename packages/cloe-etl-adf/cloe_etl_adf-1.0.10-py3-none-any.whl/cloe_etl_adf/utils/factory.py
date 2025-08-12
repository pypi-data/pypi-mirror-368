import logging
import uuid
from collections import deque

from cloe_metadata import base

logger = logging.getLogger(__name__)


def build_dependency_graph(
    batchsteps: list[base.Batchstep],
) -> dict[uuid.UUID, set[uuid.UUID]]:
    """
    Build a dependency graph where each node points to its dependencies
    and is pointed to by the objects that depend on it.
    """
    graph: dict[uuid.UUID, set[uuid.UUID]] = {}
    for obj in batchsteps:
        if obj.id not in graph:
            graph[obj.id] = set()
        if obj.dependencies:
            for dep in obj.dependencies:
                graph[obj.id].add(dep.dependent_on_batchstep_id)
                if dep.dependent_on_batchstep_id not in graph:
                    graph[dep.dependent_on_batchstep_id] = set()
                graph[dep.dependent_on_batchstep_id].add(obj.id)
    return graph


def find_connected_component(
    graph: dict[uuid.UUID, set[uuid.UUID]], start_id: uuid.UUID, visited: set[uuid.UUID]
) -> list[uuid.UUID]:
    """
    Function to find connected components (groups of dependent objects)
    """
    component = []
    queue = deque([start_id])

    while queue:
        current_id = queue.popleft()
        if current_id not in visited:
            visited.add(current_id)
            component.append(current_id)
            # Add all neighbors to the queue
            for neighbor in graph[current_id]:
                if neighbor not in visited:
                    queue.append(neighbor)

    return sorted(component)


def find_groups(batchsteps: list[base.Batchstep]) -> list:
    """
    Find all connected components
    """
    graph = build_dependency_graph(batchsteps)
    visited: set[uuid.UUID] = set()
    groups = []
    for obj in sorted(batchsteps, key=lambda x: x.id):
        if obj.id not in visited:
            component = find_connected_component(graph, obj.id, visited)
            groups.append(component)
    return groups


def sort_objects_into_groups(batchsteps: list[base.Batchstep]) -> list[list[uuid.UUID]]:
    groups = find_groups(batchsteps=batchsteps)

    # Ensure each group has at most 120 objects
    final_groups = []
    for group in groups:
        for i in range(0, len(group), 120):
            final_groups.append(group[i : i + 120])

    return final_groups


def minimize_groups(groups: list[list[uuid.UUID]]) -> list[list[uuid.UUID]]:
    collapsed_groups: list[list[uuid.UUID]] = []
    for group in sorted(groups, key=lambda x: (len(x), x)):
        # Try to merge the current group with any of the collapsed groups
        merged = False
        for c_group in collapsed_groups:
            if len(c_group) + len(group) <= 120:
                c_group.extend(group)
                merged = True
                break
        if not merged:
            collapsed_groups.append(group)
    return collapsed_groups


def optimize_batch(
    obj_batchsteps: list[base.Batchstep],
) -> dict[int, list[uuid.UUID]]:
    dependency_groups = sort_objects_into_groups(obj_batchsteps)
    dependency_groups = minimize_groups(dependency_groups)
    return dict(enumerate(dependency_groups))
