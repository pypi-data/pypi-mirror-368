"""Demo solver implementation for hackathon contestants.

This file contains a working example solver that contestants can study
to understand how to implement their own logistics optimization algorithms.
"""

from typing import Dict, List, Tuple, Optional

def test_solver(env):
    """
    Demo solver that demonstrates basic logistics optimization.
    
    This solver shows the essential structure that contestants need to implement:
    1. Get road network data from environment
    2. Access orders and vehicles
    3. Create routes using pathfinding
    4. Validate routes with environment
    5. Return solution in correct format
    
    Args:
        env: LogisticsEnvironment instance with problem data
        
    Returns:
        dict: Solution with 'routes' list containing route dictionaries
    """
    solution = {'routes': []}
    
    road_network = env.get_road_network_data()
    order_ids = env.get_all_order_ids()
    available_vehicles = env.get_available_vehicles()
    
    for i, order_id in enumerate(order_ids):
        if i < len(available_vehicles):
            vehicle_id = available_vehicles[i]
            order_location = env.get_order_location(order_id)
            home_warehouse = env.get_vehicle_home_warehouse(vehicle_id)
            
            if order_location is not None and home_warehouse is not None:
                # Ensure both are integers
                order_location = int(order_location)
                home_warehouse = int(home_warehouse)
                
                route = create_simple_route(home_warehouse, order_location, road_network)
                
                if route:
                    is_valid, error_msg = env.validate_single_route(vehicle_id, route)
                    
                    if is_valid:
                        solution['routes'].append({
                            'vehicle_id': vehicle_id,
                            'route': route,
                            'distance': env.get_route_distance(route),
                            'order_id': order_id
                        })
    
    return solution

def create_simple_route(home_warehouse, order_location, road_network):
    """
    Create a simple route from warehouse to order location.
    
    This is a basic pathfinding implementation using BFS.
    Contestants can replace this with their own algorithms.
    
    Args:
        home_warehouse: Starting node ID
        order_location: Destination node ID
        road_network: Road network data from environment
        
    Returns:
        list: Route as list of node IDs, or None if no path found
    """
    adjacency_list = road_network['adjacency_list']
    
    # Check if both nodes exist in the adjacency list
    if home_warehouse not in adjacency_list:
        return None
        
    if order_location not in adjacency_list:
        return None
    
    path = find_shortest_path(home_warehouse, order_location, adjacency_list)
    
    if path:
        return path + path[-2::-1]
    
    return None

def find_shortest_path(start_node, end_node, adjacency_list, max_path_length=500):
    """
    Find shortest path using Breadth-First Search.
    
    Args:
        start_node: Starting node ID
        end_node: Destination node ID
        adjacency_list: Graph adjacency list
        max_path_length: Maximum path length to prevent infinite loops
        
    Returns:
        list: Path as list of node IDs, or None if no path found
    """
    if start_node == end_node:
        return [start_node]
    
    queue = [(start_node, [start_node])]
    visited = {start_node}
    
    while queue and len(queue[0][1]) < max_path_length:
        current, path = queue.pop(0)
        
        neighbors = adjacency_list.get(current, [])
        for neighbor in neighbors:
            neighbor_int = int(neighbor) if hasattr(neighbor, '__int__') else neighbor
            
            if neighbor_int not in visited:
                if neighbor_int == end_node:
                    return path + [neighbor_int]
                
                visited.add(neighbor_int)
                queue.append((neighbor_int, path + [neighbor_int]))
    
    return None

if __name__ == "__main__":
    print("Demo solver for Robin Logistics Environment")
    print("Import and use with: from robin_logistics.solvers import test_solver")
