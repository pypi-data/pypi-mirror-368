"""Main API interface for hackathon contestants."""

import os
from typing import Dict, List, Tuple, Optional
import pandas as pd

from .core.data_generator import generate_scenario_from_config
from .core.environment import Environment
from .core import config


class LogisticsEnvironment:
    """
    Main interface for hackathon contestants.
    Provides clean access to problem data and solution validation.
    """
    
    def __init__(self, problem_config: Optional[Dict] = None):
        """
        Initialize the logistics environment.
        
        Args:
            problem_config: Optional configuration override. If None, uses default config.
        """
        self._config = problem_config or config.DEFAULT_SETTINGS
        self._load_problem_instance()
        
    def _load_problem_instance(self):
        """Load and initialize the problem instance."""
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        nodes_df = pd.read_csv(os.path.join(data_dir, 'nodes.csv'))
        edges_df = pd.read_csv(os.path.join(data_dir, 'edges.csv'))
        
        # Use config from core/config.py
        warehouse_configs = [
            {
                'vehicle_counts': config.DEFAULT_SETTINGS['default_vehicle_counts'],
                'sku_inventory_percentages': [50, 50, 0]
            },
            {
                'vehicle_counts': config.DEFAULT_SETTINGS['default_vehicle_counts'],
                'sku_inventory_percentages': [0, 0, 100]
            }
        ]
        
        default_config = {
            'num_orders': config.DEFAULT_SETTINGS['num_orders'],
            'num_warehouses': config.DEFAULT_SETTINGS['num_warehouses'],
            'order_dispersion': config.DEFAULT_SETTINGS['order_dispersion'],
            'sku_percentages': config.DEFAULT_SETTINGS['default_sku_distribution'],
            'warehouse_configs': warehouse_configs
        }
        
        problem_data = generate_scenario_from_config(config, nodes_df, edges_df, default_config)
        
        all_vehicles = []
        for warehouse in problem_data['warehouses']:
            all_vehicles.extend(warehouse.vehicles)
        
        self._env = Environment(
            nodes_df=pd.DataFrame([(n.id, n.lat, n.lon) for n in problem_data['nodes']], 
                                columns=['node_id', 'lat', 'lon']),
            edges_df=edges_df,
            warehouses=problem_data['warehouses'],
            orders=problem_data['orders'],
            skus=problem_data['skus'],
            vehicles=all_vehicles
        )
        
        self._nodes_df = nodes_df
        self._edges_df = edges_df
        self._last_solution = None
    
    def generate_scenario_from_config(self, custom_config: Dict):
        """Generate a new problem instance from custom configuration."""
        # Create a base config object with the custom configuration
        from .core import config as base_config
        
        problem_data = generate_scenario_from_config(base_config, self._nodes_df, self._edges_df, custom_config)
        
        all_vehicles = []
        for warehouse in problem_data['warehouses']:
            all_vehicles.extend(warehouse.vehicles)
        
        self._env = Environment(
            nodes_df=pd.DataFrame([(n.id, n.lat, n.lon) for n in problem_data['nodes']], 
                                columns=['node_id', 'lat', 'lon']),
            edges_df=self._edges_df,
            warehouses=problem_data['warehouses'],
            orders=problem_data['orders'],
            skus=problem_data['skus'],
            vehicles=all_vehicles
        )
        
        return self
    
    # Core contestant data access properties
    @property
    def warehouses(self):
        """Get all warehouse objects."""
        return self._env.warehouses
    
    @property  
    def orders(self):
        """Get all order objects."""
        return self._env.orders
        
    @property
    def skus(self):
        """Get all SKU objects."""
        return self._env.skus
        
    @property
    def vehicles(self):
        """Get all vehicle objects as a dictionary."""
        all_vehicles = self._env.get_all_vehicles()
        return {v.id: v for v in all_vehicles}
    
    @property
    def nodes(self):
        """Get all road network nodes."""
        return self._env.nodes
    
    @property
    def num_orders(self):
        """Get total number of orders."""
        return len(self.orders)
    
    @property  
    def num_warehouses(self):
        """Get total number of warehouses."""
        return len(self.warehouses)
    
    @property
    def num_vehicles(self):
        """Get total number of vehicles."""
        return len(self.vehicles)
    
    # Core contestant methods
    def get_road_network_data(self) -> Dict:
        """
        Get complete road network data for pathfinding.
            
        Returns:
            Dict containing nodes, edges, and adjacency list
        """
        return self._env.get_road_network_data()
    
    def validate_route_constraints(self, route: Dict) -> bool:
        """
        Validate if a route meets all constraints.
        
        Args:
            route: Route dictionary with vehicle_id, orders, path, distance
            
        Returns:
            True if route is valid, False otherwise
        """
        if not isinstance(route, dict) or 'routes' not in route:
            raise ValueError("Solution must be a dictionary with 'routes' key")
        
        for route_item in route['routes']:
            if not self._validate_single_route(route_item):
                return False
        return True
    
    def validate_single_route(self, vehicle_id: str, route: List[int]) -> Tuple[bool, str]:
        """
        Validate if a single route meets all constraints.
        
        Args:
            vehicle_id: ID of the vehicle assigned to this route
            route: List of node IDs representing the route
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        return self._env.validate_route_constraints(vehicle_id, route)
    
    def validate_route_physical(self, route: List[int]) -> bool:
        """
        Validate if a route follows the physical road network.
        
        Args:
            route: List of node IDs representing the route
            
        Returns:
            True if route is physically valid, False otherwise
        """
        return self._env.validate_route_physical(route)
    
    def calculate_route_cost(self, route: Dict) -> float:
        """
        Calculate the total cost of a route.
        
        Args:
            route: Route dictionary
            
        Returns:
            Total cost in USD
        """
        return self._env.calculate_route_cost(route)
    
    def get_route_distance(self, route: List[int]) -> float:
        """
        Calculate the total distance of a route.
        
        Args:
            route: List of node IDs representing the route
            
        Returns:
            Total distance in kilometers
        """
        return self._env.get_route_distance(route)
    
    # Essential helper methods for solvers and dashboard
    def get_all_order_ids(self) -> List[str]:
        """Get list of all order IDs."""
        return list(self.orders.keys())
    
    def get_available_vehicles(self) -> List[str]:
        """Get list of all available vehicle IDs."""
        return list(self.vehicles.keys())
    
    def get_order_location(self, order_id: str) -> int:
        """Get the delivery location node ID for an order."""
        if order_id in self.orders:
            return self.orders[order_id].destination.id
        raise ValueError(f"Order {order_id} not found")
    
    def get_vehicle_home_warehouse(self, vehicle_id: str) -> int:
        """Get the home warehouse node ID for a vehicle."""
        if vehicle_id in self.vehicles:
            vehicle = self.vehicles[vehicle_id]
            warehouse_id = vehicle.home_warehouse_id
            
            # Find the warehouse and get its actual node location
            for warehouse in self.warehouses.values():
                if warehouse.id == warehouse_id:
                    return warehouse.location.id
            
            raise ValueError(f"Warehouse {warehouse_id} not found for vehicle {vehicle_id}")
        raise ValueError(f"Vehicle {vehicle_id} not found")
    
    def get_order_requirements(self, order_id: str) -> Tuple[float, float]:
        """Get total weight and volume requirements for an order."""
        if order_id in self.orders:
            order = self.orders[order_id]
            total_weight = 0.0
            total_volume = 0.0
            for sku, quantity in order.requested_items.items():
                total_weight += sku.weight * quantity
                total_volume += sku.volume * quantity
            return total_weight, total_volume
        return 0.0, 0.0
    
    def can_vehicle_serve_orders(self, vehicle_id: str, order_ids: List[str], 
                               current_weight: float = 0, current_volume: float = 0) -> bool:
        """Check if a vehicle can serve a set of orders given current load."""
        if vehicle_id not in self.vehicles:
            return False
            
        vehicle = self.vehicles[vehicle_id]
        total_weight = current_weight
        total_volume = current_volume
        
        for order_id in order_ids:
            if order_id not in self.orders:
                return False
            order_weight, order_volume = self.get_order_requirements(order_id)
            total_weight += order_weight
            total_volume += order_volume
            
        return (total_weight <= vehicle.capacity_weight and 
                total_volume <= vehicle.capacity_volume)
    
    def get_distance(self, node1: int, node2: int) -> float:
        """Get direct distance between two connected nodes."""
        return self._env.get_distance(node1, node2)
    
    def get_available_edges(self) -> List[Dict]:
        """Return the road network edges with distances for solver use."""
        return self._env.get_available_edges()
    
    def _validate_single_route(self, route_item: Dict) -> bool:
        """Validate a single route item."""
        required_keys = ['vehicle_id', 'orders', 'path', 'distance']
        if not all(key in route_item for key in required_keys):
            return False
        
        # Check if vehicle exists
        if route_item['vehicle_id'] not in self.vehicles:
            return False
        
        # Check if path is physically valid
        if not self.validate_route_physical(route_item['path']):
            return False
        
        # Check if orders exist
        for order_id in route_item['orders']:
            if order_id not in self.orders:
                return False
        
        return True