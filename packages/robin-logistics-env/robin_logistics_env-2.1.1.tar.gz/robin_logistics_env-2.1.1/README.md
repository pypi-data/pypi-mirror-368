# Robin Logistics Environment

**A professional logistics optimization environment for hackathons and competitions.**

## Quick Start

### **For Developers (Local Testing)**
```bash
# Clone and setup
git clone <repository>
cd Environment

# Run dashboard with local environment
python main.py
```

### **For Contestants (Using Published Package)**
```bash
# Install package
pip install robin-logistics-env

# Run contestant example
cd contestant_example
python main.py
```

## Architecture

### **Clean Separation of Concerns**
- **Environment**: Pure data management and validation (no solver logic)
- **Dashboard**: Flexible interface that accepts any solver function
- **Solvers**: Contestants implement their own optimization algorithms
- **Demo Solver**: Working example for contestants to study

### **How It Works**
```python
from robin_logistics import LogisticsEnvironment
from robin_logistics.dashboard import run_dashboard
from my_solver import my_solver

# Create environment (pure data)
env = LogisticsEnvironment()

# Run dashboard with your solver
run_dashboard(env, solver_function=my_solver)
```

## Implementing Your Solver

### **Solver Structure**
Your solver must be a function that takes an environment and returns a solution:

```python
def my_solver(env):
    """
    Your logistics optimization algorithm.
    
    Args:
        env: LogisticsEnvironment instance
        
    Returns:
        dict: Solution with 'routes' list
    """
    solution = {'routes': []}
    
    # 1. Get problem data
    road_network = env.get_road_network_data()
    orders = env.get_all_order_ids()
    vehicles = env.get_available_vehicles()
    
    # 2. Implement your algorithm
    # ... your optimization logic here ...
    
    # 3. Create routes
    for vehicle_id, order_id in assignments:
        route = create_route(vehicle_id, order_id, road_network)
        
        # 4. Validate route
        is_valid, error = env.validate_single_route(vehicle_id, route)
        if is_valid:
            solution['routes'].append({
                'vehicle_id': vehicle_id,
                'route': route,
                'distance': env.get_route_distance(route),
                'order_id': order_id
            })
    
    return solution
```

### **Solution Format**
```python
{
    'routes': [
        {
            'vehicle_id': 'vehicle_1',
            'route': [warehouse_node, path_nodes..., warehouse_node],
            'distance': total_distance_km,
            'order_id': 'order_1'
        },