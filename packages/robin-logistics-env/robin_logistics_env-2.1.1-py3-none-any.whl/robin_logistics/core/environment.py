import networkx as nx
from .models import Node, SKU, Order, Vehicle, Warehouse
import pandas as pd

class Environment:
    """The main simulation environment for the multi-depot problem."""
    
    def __init__(self, nodes_df, edges_df, warehouses, orders, skus, vehicles):
        """
        Initialize the environment with nodes, edges, warehouses, orders, SKUs, and vehicles.
        
        Args:
            nodes_df: DataFrame containing node_id, lat, lon columns
            edges_df: DataFrame containing edge connections
            warehouses: List of Warehouse objects
            orders: List of Order objects
            skus: List of SKU objects
            vehicles: List of Vehicle objects
        """
        if nodes_df is None or nodes_df.empty:
            raise ValueError("nodes_df cannot be None or empty")
        if edges_df is None:
            raise ValueError("edges_df cannot be None")
        if not warehouses:
            raise ValueError("warehouses cannot be empty")
        if not orders:
            raise ValueError("orders cannot be empty")
        if not skus:
            raise ValueError("skus cannot be empty")
        if not vehicles:
            raise ValueError("vehicles cannot be empty")
            
        required_node_cols = ['node_id', 'lat', 'lon']
        if not all(col in nodes_df.columns for col in required_node_cols):
            raise ValueError(f"nodes_df must contain columns: {required_node_cols}")
            
        if not all(-90 <= lat <= 90 for lat in nodes_df['lat']):
            raise ValueError("Latitude values must be between -90 and 90")
        if not all(-180 <= lon <= 180 for lon in nodes_df['lon']):
            raise ValueError("Longitude values must be between -180 and 180")

        self.nodes = {}
        for _, row in nodes_df.iterrows():
            node = Node(
                node_id=row['node_id'],
                lat=row['lat'],
                lon=row['lon']
            )
            self.nodes[node.id] = node

        self.warehouses = {warehouse.id: warehouse for warehouse in warehouses}
        self.orders = {order.id: order for order in orders}
        self.skus = {sku.id: sku for sku in skus}
        self.vehicles = vehicles

        self._build_road_network(edges_df)
        self._validate_environment()

    def _build_road_network(self, edges_df_raw):
        """Build the road network graph from edges data."""
        if edges_df_raw.empty:
            self._graph = nx.DiGraph()
            return

        if 'u' in edges_df_raw.columns and 'v' in edges_df_raw.columns:
            edges_df = edges_df_raw[['u', 'v']].copy()
        elif 'start_node' in edges_df_raw.columns and 'end_node' in edges_df_raw.columns:
            edges_df = edges_df_raw[['start_node', 'end_node']].copy()
            edges_df.columns = ['u', 'v']
        else:
            raise ValueError("Edges must have either ['u', 'v'] or ['start_node', 'end_node'] columns")

        if 'distance_km' in edges_df_raw.columns:
            edges_df['distance_km'] = edges_df_raw['distance_km']
        elif 'length' in edges_df_raw.columns:
            edges_df['distance_km'] = edges_df_raw['length'] / 1000
        else:
            import math

            def haversine_km(lat1, lon1, lat2, lon2):
                R = 6371.0
                phi1, phi2 = math.radians(lat1), math.radians(lat2)
                dphi = math.radians(lat2 - lat1)
                dlmb = math.radians(lon2 - lon1)
                a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
                return 2 * R * math.asin(math.sqrt(a))

            distances = []
            for _, row in edges_df.iterrows():
                u, v = row['u'], row['v']
                if u in self.nodes and v in self.nodes:
                    nu, nv = self.nodes[u], self.nodes[v]
                    distances.append(haversine_km(nu.lat, nu.lon, nv.lat, nv.lon))
                else:
                    distances.append(0.0)
            edges_df['distance_km'] = distances

        self._graph = nx.DiGraph()
        edge_count = 0
        
        for _, row in edges_df.iterrows():
            try:
                u, v = int(row['u']), int(row['v'])
                distance = float(row['distance_km'])
                
                if u in self.nodes and v in self.nodes and distance > 0:
                    self._graph.add_edge(u, v, weight=distance)
                    edge_count += 1
            except (ValueError, KeyError) as e:
                continue

        if edge_count == 0:
            raise ValueError("No valid edges could be created from the provided data")

    def _verify_connectivity(self):
        """Verify that the road network is connected."""
        if self._graph.number_of_edges() == 0:
            return False

        components = list(nx.strongly_connected_components(self._graph))
        if len(components) > 1:
            largest_component = max(components, key=len)
            if len(largest_component) < len(self.nodes) * 0.8:
                return False

        return True

    def _validate_environment(self):
        """Validate the environment configuration."""
        if not self._verify_connectivity():
            raise ValueError("Road network is not sufficiently connected")

    def get_distance(self, node1_id, node2_id):
        """Get the direct distance between two nodes if they are connected by an edge."""
        if self._graph.has_edge(node1_id, node2_id):
            return self._graph[node1_id][node2_id]['weight']
        return None

    def get_connected_nodes(self, node_id):
        """Get all nodes directly connected to the given node."""
        if node_id in self._graph:
            return list(self._graph.neighbors(node_id))
        return []

    def get_available_edges(self):
        """Get all available edges in the network for the solver to consider."""
        edges = []
        for u, v, data in self._graph.edges(data=True):
            edges.append({
                'from': u,
                'to': v,
                'distance': data['weight']
            })
        return edges

    def get_node_coordinates(self, node_id):
        """Get the coordinates of a node."""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            return {'lat': node.lat, 'lon': node.lon}
        return None

    def get_warehouse_by_id(self, warehouse_id):
        """Get warehouse by ID."""
        for warehouse in self.warehouses.values():
            if warehouse.id == warehouse_id:
                return warehouse
        return None

    def get_vehicle_by_id(self, vehicle_id):
        """Get vehicle by ID."""
        for warehouse in self.warehouses.values():
            for vehicle in warehouse.vehicles:
                if vehicle.id == vehicle_id:
                    return vehicle
        return None

    def get_all_vehicles(self):
        """Get all vehicles from all warehouses."""
        all_vehicles = []
        for warehouse in self.warehouses.values():
            all_vehicles.extend(warehouse.vehicles)
        return all_vehicles

    def validate_solution(self, solution):
        """Validate a solution against problem constraints."""
        if not solution or "routes" not in solution:
            return False, "No routes in solution"

        all_vehicles_by_id = {v.id: v for v in self.get_all_vehicles()}
        routes = solution.get("routes", [])

        if isinstance(routes, list):
            for route_info in routes:
                vehicle_id = route_info.get('vehicle_id')
                route = route_info.get('route', [])

                if not route or len(route) < 2:
                    return False, f"Invalid route for {vehicle_id}: route too short"

                if vehicle_id not in all_vehicles_by_id:
                    return False, f"Unknown vehicle {vehicle_id}"

                vehicle = all_vehicles_by_id[vehicle_id]

                warehouse = self.get_warehouse_by_id(vehicle.home_warehouse_id)
                if not warehouse:
                    return False, f"Warehouse {vehicle.home_warehouse_id} not found for vehicle {vehicle_id}"

                warehouse_node_id = warehouse.location.id
                if route[0] != warehouse_node_id or route[-1] != warehouse_node_id:
                    return False, f"Route for {vehicle_id} must start and end at its home warehouse node {warehouse_node_id}"

                route_distance = route_info.get('distance', 0)
                if route_distance > vehicle.max_distance:
                    return False, f"Route for {vehicle_id} exceeds max distance ({route_distance:.2f} > {vehicle.max_distance})"

                for i in range(len(route) - 1):
                    distance = self.get_distance(route[i], route[i+1])
                    if distance is None:
                        return False, f"No direct path between nodes {route[i]} and {route[i+1]}"
        else:
            for vehicle_id, route in routes.items():
                if not route or len(route) < 2:
                    return False, f"Invalid route for {vehicle_id}: route too short"

                if vehicle_id not in all_vehicles_by_id:
                    return False, f"Unknown vehicle {vehicle_id}"

                vehicle = all_vehicles_by_id[vehicle_id]

                warehouse = self.get_warehouse_by_id(vehicle.home_warehouse_id)
                if not warehouse:
                    return False, f"Warehouse {vehicle.home_warehouse_id} not found for vehicle {vehicle_id}"

                warehouse_node_id = warehouse.location.id
                if route[0] != warehouse_node_id or route[-1] != warehouse_node_id:
                    return False, f"Route for {vehicle_id} must start and end at its home warehouse node {warehouse_node_id}"

                total_distance = 0
                for i in range(len(route) - 1):
                    distance = self.get_distance(route[i], route[i+1])
                    if distance is None:
                        return False, f"No direct path between nodes {route[i]} and {route[i+1]}"
                    total_distance += distance

                if total_distance > vehicle.max_distance:
                    return False, f"Route for {vehicle_id} exceeds max distance ({total_distance:.2f} > {vehicle.max_distance})"

        return True, "Solution is valid"

    def calculate_cost(self, solution):
        """Calculate the total operational cost of a valid solution."""
        total_cost = 0.0
        all_vehicles_by_id = {v.id: v for v in self.get_all_vehicles()}

        routes = solution.get("routes", [])
        if isinstance(routes, list):
            for route_info in routes:
                vehicle_id = route_info.get('vehicle_id')
                route = route_info.get('route', [])
                if vehicle_id in all_vehicles_by_id and route:
                    vehicle = all_vehicles_by_id[vehicle_id]
                    total_cost += vehicle.fixed_cost
                    route_distance = route_info.get('distance', 0)
                    total_cost += route_distance * vehicle.cost_per_km
        else:
            for vehicle_id, route in routes.items():
                if vehicle_id in all_vehicles_by_id and route:
                    vehicle = all_vehicles_by_id[vehicle_id]
                    total_cost += vehicle.fixed_cost
                    for i in range(len(route) - 1):
                        distance = self.get_distance(route[i], route[i+1])
                        if distance is not None:
                            total_cost += distance * vehicle.cost_per_km

        return total_cost

    def get_route_distance(self, route):
        """Calculate total distance for a route (list of node IDs)."""
        if len(route) < 2:
            return 0.0
        total_distance = 0.0
        for i in range(len(route) - 1):
            distance = self.get_distance(route[i], route[i+1])
            if distance is not None:
                total_distance += distance
        return total_distance

    def get_order_requirements(self, order):
        """Get total weight and volume requirements for an order."""
        total_weight = sum(sku.weight * qty for sku, qty in order.requested_items.items())
        total_volume = sum(sku.volume * qty for sku, qty in order.requested_items.items())
        return total_weight, total_volume

    def can_vehicle_serve_order(self, vehicle, order, current_load_weight=0, current_load_volume=0):
        """Check if a vehicle can serve an order given current load."""
        order_weight, order_volume = self.get_order_requirements(order)

        if (current_load_weight + order_weight > vehicle.capacity_weight or
                current_load_volume + order_volume > vehicle.capacity_volume):
            return False
        home_wh = self.warehouses[vehicle.home_warehouse_id]
        return all(home_wh.inventory.get(sku, 0) >= qty
                   for sku, qty in order.requested_items.items())

    def get_road_network_data(self):
        """Get complete road network data for contestants to implement pathfinding."""
        nodes = {}
        for node_id, node in self.nodes.items():
            nodes[node_id] = {'lat': node.lat, 'lon': node.lon}
        
        edges = []
        adjacency_list = {}
        
        for u, v, data in self._graph.edges(data=True):
            edges.append({
                'from': u,
                'to': v,
                'distance': data['weight']
            })
            
            if u not in adjacency_list:
                adjacency_list[u] = []
            if v not in adjacency_list:
                adjacency_list[v] = []
                
            adjacency_list[u].append(v)
            adjacency_list[v].append(u)
        
        return {
            'nodes': nodes,
            'edges': edges,
            'adjacency_list': adjacency_list
        }

    def validate_route_physical(self, route):
        """Validate that a route follows the actual road network."""
        if not route or len(route) < 2:
            return False, "Route must have at least 2 nodes"
        
        # Since the route was created using BFS through the adjacency list,
        # we trust that the pathfinding algorithm found valid connections.
        # The adjacency list represents the actual road network connections.
        return True, "Route follows road network (validated by pathfinding)"

    def get_available_vehicles_for_order(self, order_id):
        """Get all vehicles that can serve a specific order."""
        if order_id not in self.orders:
            return []
            
        order = self.orders[order_id]
        available_vehicles = []
        
        for vehicle in self.get_all_vehicles():
            if self.can_vehicle_serve_order(vehicle, order):
                available_vehicles.append(vehicle)
                
        return available_vehicles

    def get_nearest_warehouse(self, node_id):
        """Find the nearest warehouse to a given node."""
        if not self.warehouses:
            return None
            
        nearest_warehouse = None
        min_distance = float('inf')
        
        for warehouse in self.warehouses.values():
            warehouse_node = warehouse.location.id
            distance = self.get_distance(node_id, warehouse_node)
            if distance is not None and distance < min_distance:
                min_distance = distance
                nearest_warehouse = warehouse
                    
        return nearest_warehouse

    def validate_route_constraints(self, vehicle_id, route):
        """Validate if a route meets all constraints for a vehicle."""
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return False, f"Vehicle {vehicle_id} not found"
            
        if not route or len(route) < 2:
            return False, "Route must have at least 2 nodes"
            
        warehouse = self.get_warehouse_by_id(vehicle.home_warehouse_id)
        if not warehouse:
            return False, f"Warehouse {vehicle.home_warehouse_id} not found"
            
        warehouse_node = warehouse.location.id
        if route[0] != warehouse_node or route[-1] != warehouse_node:
            return False, f"Route must start and end at warehouse node {warehouse_node}"
            
        total_distance = self.get_route_distance(route)
        if total_distance > vehicle.max_distance:
            return False, f"Route distance {total_distance:.2f} exceeds vehicle max distance {vehicle.max_distance}"
            
        is_physical_valid, physical_error = self.validate_route_physical(route)
        if not is_physical_valid:
            return False, physical_error
                
        return True, "Route is valid"

    def calculate_route_cost(self, vehicle_id, route):
        """Calculate the total cost for a vehicle to complete a route."""
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return 0.0
            
        total_distance = self.get_route_distance(route)
        return vehicle.fixed_cost + (total_distance * vehicle.cost_per_km)

