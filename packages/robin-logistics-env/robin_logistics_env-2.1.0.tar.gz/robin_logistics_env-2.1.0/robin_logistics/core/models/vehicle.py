
class Vehicle:
    """Represents a single delivery vehicle with dynamic state."""
    
    def __init__(self, vehicle_id, v_type, home_warehouse_id, **kwargs):
        """
        Initialize a Vehicle.
        
        Args:
            vehicle_id: Unique identifier for the vehicle
            v_type: Type/category of the vehicle
            home_warehouse_id: ID of the warehouse where the vehicle is based
            **kwargs: Additional vehicle specifications
        """
        self.id = vehicle_id
        self.type = v_type
        self.home_warehouse_id = home_warehouse_id
        self.capacity_weight = float(kwargs['capacity_weight_kg'])
        self.capacity_volume = float(kwargs['capacity_volume_m3'])
        self.max_distance = float(kwargs['max_distance_km'])
        self.cost_per_km = float(kwargs['cost_per_km'])
        self.fixed_cost = float(kwargs['fixed_cost'])

        self.current_inventory = {}
        self.current_weight = 0.0
        self.current_volume = 0.0

    def load_item(self, sku, quantity):
        """
        Load items onto the vehicle, updating its state.
        
        Args:
            sku: SKU object to load
            quantity: Number of items to load
        """
        self.current_inventory[sku] = self.current_inventory.get(sku, 0) + quantity
        self.current_weight += sku.weight * quantity
        self.current_volume += sku.volume * quantity

    def unload_order(self, order):
        """
        Unload an order's items from the vehicle.
        
        Args:
            order: Order object containing items to unload
        """
        for sku, quantity in order.requested_items.items():
            self.current_inventory[sku] -= quantity
            self.current_weight -= sku.weight * quantity
            self.current_volume -= sku.volume * quantity

    def __repr__(self):
        return f"Vehicle({self.id} from {self.home_warehouse_id})"