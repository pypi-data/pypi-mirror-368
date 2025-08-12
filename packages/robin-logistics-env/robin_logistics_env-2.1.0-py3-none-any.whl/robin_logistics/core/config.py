"""Operational parameters for the multi-depot problem instance."""

WAREHOUSE_LOCATIONS = [
    {"id": "WH-1", "lat": 45.0, "lon": -75.0, "name": "Main Distribution Center"},
    {"id": "WH-2", "lat": 45.5, "lon": -74.5, "name": "Secondary Hub"},
    {"id": "WH-3", "lat": 44.8, "lon": -75.2, "name": "Regional Warehouse"}
]

VEHICLE_FLEET_SPECS = [
    {
        "type": "LightVan",
        "name": "Light Delivery Van",
        "capacity_weight_kg": 800,
        "capacity_volume_m3": 6.0,
        "max_distance_km": 300,
        "cost_per_km": 0.5,
        "fixed_cost": 50,
        "description": "Small van for local deliveries"
    },
    {
        "type": "MediumTruck", 
        "name": "Medium Cargo Truck",
        "capacity_weight_kg": 2000,
        "capacity_volume_m3": 15.0,
        "max_distance_km": 500,
        "cost_per_km": 0.8,
        "fixed_cost": 100,
        "description": "Standard truck for medium loads"
    },
    {
        "type": "HeavyTruck",
        "name": "Heavy Cargo Truck", 
        "capacity_weight_kg": 5000,
        "capacity_volume_m3": 40.0,
        "max_distance_km": 800,
        "cost_per_km": 1.2,
        "fixed_cost": 200,
        "description": "Large truck for heavy loads"
    }
]

SKU_DEFINITIONS = [
    {
        'sku_id': 'Light_Item', 
        'weight_kg': 5.0, 
        'volume_m3': 0.02
    },
    {
        'sku_id': 'Medium_Item', 
        'weight_kg': 15.0, 
        'volume_m3': 0.06
    },
    {
        'sku_id': 'Heavy_Item', 
        'weight_kg': 30.0, 
        'volume_m3': 0.12
    }
]

DEFAULT_SETTINGS = {
    'num_orders': 15,
    'num_warehouses': 2,
    'order_dispersion': 100,
    'default_sku_distribution': [33.33, 33.33, 33.34],
    'default_vehicle_counts': {
        'LightVan': 2,
        'MediumTruck': 1,
        'HeavyTruck': 0
    },
    'fuel_cost_per_km': 0.5,
    'min_items_per_order': 3,
    'max_items_per_order': 8,
    'max_orders': 50
}

