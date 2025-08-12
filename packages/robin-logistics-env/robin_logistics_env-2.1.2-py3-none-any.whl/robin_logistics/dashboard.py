"""Dashboard interface for the Robin Logistics Environment."""

import streamlit as st
import pandas as pd
import folium
from robin_logistics.core import config as config_module

from robin_logistics.core.config import (
    SKU_DEFINITIONS,
    WAREHOUSE_LOCATIONS,
    VEHICLE_FLEET_SPECS,
    DEFAULT_SETTINGS
)

def run_dashboard(env, solver_function=None):
    """
    Main dashboard function.
    
    Args:
        env: LogisticsEnvironment instance
        solver_function: Optional solver function to use instead of default demo solver
    """
    st.set_page_config(
        page_title="Robin Logistics Environment",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("Robin Logistics Environment")
    st.write("Configure and solve multi-depot vehicle routing problems with real-world constraints.")

    # Set solver (custom or default)
    if solver_function:
        current_solver = solver_function
    else:
        from robin_logistics.solvers import test_solver
        current_solver = test_solver

    st.header("Fixed Infrastructure")

    st.subheader("SKU Types")
    sku_data = []
    for sku_info in SKU_DEFINITIONS:
        sku_data.append({
            'SKU ID': sku_info['sku_id'],
            'Weight (kg)': sku_info['weight_kg'],
            'Volume (m³)': sku_info['volume_m3']
        })

    if sku_data:
        st.dataframe(pd.DataFrame(sku_data), use_container_width=True)

    st.subheader("Vehicle Fleet Specifications")
    vehicle_data = []
    for vehicle_spec in VEHICLE_FLEET_SPECS:
        vehicle_data.append({
            'Type': vehicle_spec['type'],
            'Name': vehicle_spec['name'],
            'Weight Capacity (kg)': vehicle_spec['capacity_weight_kg'],
            'Volume Capacity (m³)': vehicle_spec['capacity_volume_m3'],
            'Max Distance (km)': vehicle_spec['max_distance_km'],
            'Cost per km': f"${vehicle_spec['cost_per_km']:.2f}",
            'Fixed Cost': f"${vehicle_spec['fixed_cost']:.2f}",
            'Description': vehicle_spec['description']
        })

    if vehicle_data:
        st.dataframe(pd.DataFrame(vehicle_data), use_container_width=True)

    st.subheader("Warehouse Locations")
    warehouse_data = []
    for warehouse in WAREHOUSE_LOCATIONS:
        warehouse_data.append({
            'ID': warehouse['id'],
            'Name': warehouse['name'],
            'Latitude': f"{warehouse['lat']:.4f}",
            'Longitude': f"{warehouse['lon']:.4f}"
        })

    if warehouse_data:
        st.dataframe(pd.DataFrame(warehouse_data), use_container_width=True)

    st.divider()

    tab1, tab2 = st.tabs(["Demand Configuration", "Supply Configuration"])

    with tab1:
        st.subheader("Demand Configuration")

        num_orders = st.number_input(
            "Number of Orders",
            min_value=5,
            max_value=DEFAULT_SETTINGS.get('max_orders', 50),
            value=DEFAULT_SETTINGS['num_orders'],
            key="main_num_orders",
            help="Total number of customer orders to generate"
        )

        min_items_per_order = st.number_input(
            "Min Items per Order",
            min_value=1,
            max_value=10,
            value=DEFAULT_SETTINGS['min_items_per_order'],
            key="main_min_items_per_order",
            help="Minimum number of items in each order"
        )

        max_items_per_order = st.number_input(
            "Max Items per Order",
            min_value=1,
            max_value=20,
            value=DEFAULT_SETTINGS['max_items_per_order'],
            key="main_max_items_per_order",
            help="Maximum number of items in each order"
        )

        order_dispersion = st.slider(
            "Order Dispersion (km)",
            min_value=10,
            max_value=300,
            value=DEFAULT_SETTINGS['order_dispersion'],
            step=10,
            key="main_order_dispersion",
            help="How far orders are dispersed from each other (max distance between any two orders)"
        )

        st.subheader("SKU Distribution (%)")
        sku_names = [sku_info['sku_id'] for sku_info in SKU_DEFINITIONS]

        sku_percentages = []
        remaining_percentage = 100.0

        for i in range(len(sku_names)):
            if i == len(sku_names) - 1:
                current_value = remaining_percentage
                max_value = remaining_percentage
            else:
                max_value = remaining_percentage - (len(sku_names) - i - 1)
                max_value = max(1.0, max_value)
                current_value = DEFAULT_SETTINGS['default_sku_distribution'][i]
                current_value = min(current_value, max_value)

            slider_max = max(1, int(max_value))
            percentage = st.slider(
                f"{sku_names[i]}",
                min_value=0,
                max_value=slider_max,
                value=int(current_value),
                step=1,
                key=f"demand_sku_{i}_percentage",
                help=f"Percentage of {sku_names[i]} in total demand"
            )

            sku_percentages.append(percentage)
            remaining_percentage -= percentage

            if remaining_percentage < 0:
                st.error(f"Total exceeds 100%! Current: {100-remaining_percentage:.1f}%")
                break
            elif remaining_percentage > 0 and i < len(sku_names) - 1:
                st.info(f"Remaining: {remaining_percentage:.1f}%")

        st.subheader("Demand SKU Summary")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**SKU Distribution:**")
            for i, sku_name in enumerate(sku_names):
                st.write(f"• {sku_name}: {sku_percentages[i]}%")

        with col2:
            total_percentage = sum(sku_percentages)
            if total_percentage == 100:
                st.success(f"Total: {total_percentage}% (Valid)")
            else:
                st.error(f"Total: {total_percentage}% (Must equal 100%)")

    with tab2:
        st.subheader("Supply Configuration")

        num_warehouses = st.number_input(
            "Number of Warehouses to Use",
            min_value=1,
            max_value=len(WAREHOUSE_LOCATIONS),
            value=DEFAULT_SETTINGS['num_warehouses'],
            key="main_num_warehouses",
            help=f"Select how many of the {len(WAREHOUSE_LOCATIONS)} available warehouses to use"
        )

        warehouse_tabs = st.tabs([f"Warehouse {i+1}" for i in range(num_warehouses)])
        warehouse_configs = []

        for i in range(num_warehouses):
            with warehouse_tabs[i]:
                st.write(f"**Warehouse {i+1} Configuration**")

                st.subheader("SKU Inventory Distribution")
                sku_inventory_percentages = []

                for j in range(len(sku_names)):
                    demand_percentage = sku_percentages[j]
                    allocated_so_far = sum(warehouse_configs[k]['sku_inventory_percentages'][j]
                                           for k in range(i) if k < len(warehouse_configs))
                    remaining_for_sku = demand_percentage - allocated_so_far

                    if i == num_warehouses - 1:
                        current_value = int(remaining_for_sku)
                        max_value = int(remaining_for_sku)
                    else:
                        max_value = int(remaining_for_sku)
                        remaining_warehouses = num_warehouses - i
                        current_value = int(remaining_for_sku / remaining_warehouses)
                        current_value = min(current_value, max_value)

                    if max_value > 0:
                        percentage = st.slider(
                        f"{sku_names[j]} % (Demand: {demand_percentage}%, Remaining: {remaining_for_sku:.1f}%)",
                        min_value=0,
                        max_value=max_value,
                        value=current_value,
                        step=1,
                        key=f"warehouse_{i}_sku_{j}_percentage",
                        help=f"Percentage of {sku_names[j]} demand supplied by this warehouse (0% = not supplied)"
                    )
                    else:
                        st.write(f"{sku_names[j]} % (Demand: {demand_percentage}%, Remaining: 0%) - No allocation needed")
                        percentage = 0

                    sku_inventory_percentages.append(percentage)

                st.subheader("Vehicle Fleet")
                vehicle_counts = {}

                for vehicle_spec in VEHICLE_FLEET_SPECS:
                    vehicle_type = vehicle_spec['type']
                    current_count = DEFAULT_SETTINGS['default_vehicle_counts'].get(vehicle_type, 0)

                    count = st.number_input(
                        f"Number of {vehicle_type}",
                        min_value=0,
                        max_value=10,
                        value=current_count,
                        key=f"warehouse_{i}_vehicle_{vehicle_type}",
                        help=f"Number of {vehicle_type} vehicles in this warehouse"
                    )

                    vehicle_counts[vehicle_type] = count

                warehouse_configs.append({
                    'sku_inventory_percentages': sku_inventory_percentages,
                    'vehicle_counts': vehicle_counts
                })

        st.subheader("Warehouse Allocation Summary")

        all_complete = all(
            sum(warehouse_configs[i]['sku_inventory_percentages'][j]
                for i in range(len(warehouse_configs))) == sku_percentages[j]
            for j in range(len(sku_names))
        )

        if all_complete:
            st.success("All SKU demand is fully allocated across warehouses!")
        else:
            st.warning("Some SKU demand is not fully allocated across warehouses")

    st.divider()

    st.header("Configuration Summary")

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        st.metric("Orders", num_orders, delta=f"{min_items_per_order}-{max_items_per_order} items each")
        st.metric("Warehouses", num_warehouses, delta=f"of {len(WAREHOUSE_LOCATIONS)} available")
        st.metric("Dispersion", f"{order_dispersion} km", delta="max order distance")

        st.write("**Vehicle Fleet:**")
        vehicle_type_counts = {}
        for config in warehouse_configs:
            for vehicle_type, count in config['vehicle_counts'].items():
                vehicle_type_counts[vehicle_type] = vehicle_type_counts.get(vehicle_type, 0) + count

        for vehicle_type, count in vehicle_type_counts.items():
            if count > 0:
                st.write(f"• {vehicle_type}: {count}")

    with summary_col2:
        avg_items = (min_items_per_order + max_items_per_order) / 2
        expected_total_items = num_orders * avg_items
        st.metric("Expected Items", f"{expected_total_items:.0f}", delta=f"~{avg_items:.1f} per order")

        st.write("**Inventory Coverage by SKU:**")
        for j, sku_name in enumerate(sku_names):
            sku_demand = sku_percentages[j]
            sku_supply = sum(warehouse_configs[i]['sku_inventory_percentages'][j]
                             for i in range(len(warehouse_configs)))
            status = "Complete" if sku_supply == sku_demand else f"Incomplete {sku_supply}/{sku_demand}%"
            st.write(f"• {sku_name}: {status}")

        st.write("**Warehouse Breakdown:**")
        for i, config in enumerate(warehouse_configs):
            warehouse_total = sum(config['sku_inventory_percentages'])
            st.write(f"• WH{i+1}: {warehouse_total}% of total demand")

        all_valid = True
        validation_messages = []

        for j, sku_name in enumerate(sku_names):
            sku_demand = sku_percentages[j]
            sku_supply = sum(warehouse_configs[i]['sku_inventory_percentages'][j]
                             for i in range(len(warehouse_configs)))

            if sku_supply != sku_demand:
                all_valid = False
                validation_messages.append(f"Error: {sku_name}: Demand {sku_demand}% ≠ Supply {sku_supply}%")
            else:
                validation_messages.append(f"Valid: {sku_name}: Demand {sku_demand}% = Supply {sku_supply}%")

        if all_valid:
            st.success("Configuration Valid - All SKU supply matches demand")
        else:
            st.error("Configuration Invalid - SKU supply doesn't match demand")
            for msg in validation_messages:
                st.write(msg)

    if st.button("Run Simulation", type="primary", key="run_sim"):
        st.info("Configuration captured! Updating vehicle fleet and running solver...")
        st.info("Regenerating environment with new demand configuration...")

        custom_config = {
            'num_orders': num_orders,
            'min_items_per_order': min_items_per_order,
            'max_items_per_order': max_items_per_order,
            'order_dispersion': order_dispersion,
            'sku_percentages': sku_percentages,
            'warehouse_configs': warehouse_configs,
            'num_warehouses': num_warehouses
        }

        from robin_logistics.core.data_generator import generate_scenario_from_config
        from robin_logistics.core.environment import Environment

        try:
            class BaseConfig:
                SKU_DEFINITIONS = config_module.SKU_DEFINITIONS
                WAREHOUSE_LOCATIONS = config_module.WAREHOUSE_LOCATIONS
                VEHICLE_FLEET_SPECS = config_module.VEHICLE_FLEET_SPECS
                DEFAULT_SETTINGS = config_module.DEFAULT_SETTINGS

            base_config = BaseConfig()

            # Use proper package data paths
            import os
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            nodes_df = pd.read_csv(os.path.join(data_dir, 'nodes.csv'))
            edges_df = pd.read_csv(os.path.join(data_dir, 'edges.csv'))

            scenario_data = generate_scenario_from_config(
                base_config,
                nodes_df,
                edges_df,
                custom_config
            )

            nodes_df = pd.DataFrame([
                {'node_id': node.id, 'lat': node.lat, 'lon': node.lon}
                for node in scenario_data['nodes']
            ])

            all_vehicles = []
            for warehouse in scenario_data['warehouses']:
                all_vehicles.extend(warehouse.vehicles)

            from robin_logistics import LogisticsEnvironment
            
            custom_config = {
                'num_orders': num_orders,
                'num_warehouses': len(scenario_data['warehouses']),
                'order_dispersion': order_dispersion,
                'sku_percentages': sku_percentages,
                'warehouse_configs': warehouse_configs
            }
            
            env = LogisticsEnvironment()
            env = env.generate_scenario_from_config(custom_config)

            st.session_state['env'] = env
            st.success("Environment regenerated successfully!")

        except Exception as e:
            st.error(f"Failed to regenerate environment: {str(e)}")
            st.error("Using existing environment...")
            env = st.session_state.get('env')

        if env:
            try:
                solution = current_solver(env)

                if solution and solution.get('routes'):
                    st.success("Solver completed successfully!")
                    st.session_state['solution'] = solution
                    st.session_state['env'] = env

                    st.divider()
                    st.subheader("Solution Analysis")

                    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                        "Solution Overview",
                        "Inventory Management",
                        "Vehicle Status",
                        "Route Visualization",
                        "Cost Analysis",
                        "Orders View"
                    ])

                    with tab1:
                        st.subheader("Solution Overview")

                        total_routes = len(solution['routes'])
                        total_distance = sum(route.get('distance', 0) for route in solution['routes'])
                        orders_served = len(solution['routes'])
                        total_orders = env.num_orders
                        fuel_cost = DEFAULT_SETTINGS.get('fuel_cost_per_km', 0.5)
                        total_cost = total_distance * fuel_cost

                        avg_distance_per_order = total_distance / orders_served if orders_served > 0 else 0
                        avg_cost_per_order = total_cost / orders_served if orders_served > 0 else 0
                        utilization_rate = (orders_served / total_orders) * 100 if total_orders > 0 else 0

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Cost", f"${total_cost:.2f}", delta=f"${avg_cost_per_order:.2f}/order")
                        with col2:
                            st.metric("Total Distance", f"{total_distance:.2f} km", delta=f"{avg_distance_per_order:.2f} km/order")
                        with col3:
                            st.metric("Orders Served", f"{orders_served}/{total_orders}", delta=f"{utilization_rate:.1f}%")
                        with col4:
                            st.metric("Active Vehicles", total_routes, delta=f"{total_routes/env.num_warehouses:.1f}/warehouse")

                        st.divider()
                        if total_routes > 0:
                            st.success(f"**Solution Status**: Successfully served {orders_served} out of {total_orders} orders using {total_routes} vehicles")

                            col1, col2, col3 = st.columns(3)
                            with col1:
                                if utilization_rate >= 90:
                                    st.success(f"**Utilization**: {utilization_rate:.1f}% (Excellent)")
                                elif utilization_rate >= 70:
                                    st.info(f"**Utilization**: {utilization_rate:.1f}% (Good)")
                                else:
                                    st.warning(f"**Utilization**: {utilization_rate:.1f}% (Needs Improvement)")

                            with col2:
                                efficiency_threshold = DEFAULT_SETTINGS.get('efficiency_threshold_km', 20)
                                if avg_distance_per_order <= efficiency_threshold * 0.5:
                                    st.success(f"**Efficiency**: {avg_distance_per_order:.2f} km/order (Excellent)")
                                elif avg_distance_per_order <= efficiency_threshold:
                                    st.info(f"**Efficiency**: {avg_distance_per_order:.2f} km/order (Good)")
                                else:
                                    st.warning(f"**Efficiency**: {avg_distance_per_order:.2f} km/order (High)")

                            with col3:
                                cost_threshold = DEFAULT_SETTINGS.get('cost_threshold_usd', 25)
                                if avg_cost_per_order <= cost_threshold * 0.6:
                                    st.success(f"**Cost Efficiency**: ${avg_cost_per_order:.2f}/order (Excellent)")
                                elif avg_cost_per_order <= cost_threshold:
                                    st.info(f"**Cost Efficiency**: ${avg_cost_per_order:.2f}/order (Good)")
                                else:
                                    st.warning(f"**Cost Efficiency**: ${avg_cost_per_order:.2f}/order (High)")

                            st.divider()
                            st.write("**Additional Performance Metrics:**")

                            if total_routes > 0:
                                avg_route_length = total_distance / total_routes
                                route_efficiency = orders_served / total_routes if total_routes > 0 else 0

                                total_capacity_weight = sum(
                                    sum(v.capacity_weight for v in wh.vehicles)
                                    for wh in env.warehouses.values()
                                )
                                total_capacity_volume = sum(
                                    sum(v.capacity_volume for v in wh.vehicles)
                                    for wh in env.warehouses.values()
                                )

                                total_weight_delivered = 0
                                total_volume_delivered = 0
                                for route in solution['routes']:
                                    order_id = route['order_id']
                                    if order_id in env.orders:
                                        order = env.orders[order_id]
                                        for sku_id, quantity in order.requested_items.items():
                                            for sku in env.skus.values():
                                                if sku.id == sku_id:
                                                    total_weight_delivered += sku.weight * quantity
                                                    total_volume_delivered += sku.volume * quantity
                                                    break

                                capacity_weight_utilization = (total_weight_delivered / total_capacity_weight * 100) if total_capacity_weight > 0 else 0
                                capacity_volume_utilization = (total_volume_delivered / total_capacity_volume * 100) if total_capacity_volume > 0 else 0

                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Route Efficiency", f"{route_efficiency:.2f}", delta="orders per route")
                                with col2:
                                    st.metric("Avg Route Length", f"{avg_route_length:.2f} km", delta="per route")
                                with col3:
                                    st.metric("Weight Capacity", f"{capacity_weight_utilization:.1f}%", delta=f"{total_weight_delivered:.1f}/{total_capacity_weight:.1f} kg")
                                with col4:
                                    st.metric("Volume Capacity", f"{capacity_volume_utilization:.1f}%", delta=f"{total_volume_delivered:.3f}/{total_capacity_volume:.3f} m³")
                            else:
                                st.error("**Solution Status**: No routes found - check vehicle constraints and order distances")

                            if total_routes > 0:
                                st.divider()
                                st.write("Route Distribution by Vehicle Type")

                                vehicle_type_counts = {}
                                for route in solution['routes']:
                                    vehicle_id = route['vehicle_id']
                                    vehicle_type = vehicle_id.split('_')[0]
                                    vehicle_type_counts[vehicle_type] = vehicle_type_counts.get(vehicle_type, 0) + 1

                                if vehicle_type_counts:
                                    cols = st.columns(len(vehicle_type_counts))
                                    for i, (vehicle_type, count) in enumerate(vehicle_type_counts.items()):
                                        with cols[i]:
                                            st.metric(vehicle_type, count, delta=f"{count/total_routes*100:.1f}%")

                            if total_routes > 0:
                                st.divider()
                                st.write("Distance Analysis")

                                distances = [route.get('distance', 0) for route in solution['routes']]
                                if distances:
                                    min_dist = min(distances)
                                    max_dist = max(distances)
                                    avg_dist = sum(distances) / len(distances)

                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Shortest Route", f"{min_dist:.2f} km")
                                    with col2:
                                        st.metric("Longest Route", f"{max_dist:.2f} km")
                                    with col3:
                                        st.metric("Average Route", f"{avg_dist:.2f} km")

                            if total_routes > 0:
                                st.divider()
                                st.write("Resource Utilization")

                                total_warehouses = len(env.warehouses.values())
                                active_warehouse_ids = set()
                                for route_info in solution['routes']:
                                    vehicle_id = route_info['vehicle_id']
                                    for wh in env.warehouses.values():
                                        for v in wh.vehicles:
                                            if v.id == vehicle_id:
                                                active_warehouse_ids.add(v.home_warehouse_id)
                                                break
                                        if vehicle_id in [v.id for v in wh.vehicles]:
                                            break

                                active_warehouses = len(active_warehouse_ids)
                                warehouse_utilization_rate = (active_warehouses / total_warehouses) * 100 if total_warehouses > 0 else 0

                                total_vehicles = sum(len(wh.vehicles) for wh in env.warehouses.values())
                                vehicle_utilization_rate = (total_routes / total_vehicles) * 100 if total_vehicles > 0 else 0

                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Warehouse Utilization", f"{warehouse_utilization_rate:.1f}%",
                                              delta=f"{active_warehouses}/{total_warehouses} active")
                                with col2:
                                    st.metric("Vehicle Utilization", f"{vehicle_utilization_rate:.1f}%",
                                              delta=f"{total_routes}/{total_vehicles} used")

                    with tab2:
                        st.subheader("Inventory Management")

                        st.write("Warehouse Inventory Status:")
                        for i, warehouse in enumerate(env.warehouses.values()):
                            if i < len(warehouse_configs):
                                st.write(f"**WH{i+1} ({warehouse.id}):**")

                                inventory_data = []
                                for sku_id, quantity in warehouse.inventory.items():
                                    inventory_data.append({
                                        'SKU': sku_id,
                                        'Available': quantity,
                                        'Status': 'In Stock' if quantity > 0 else 'Out of Stock'
                                    })

                                if inventory_data:
                                    st.dataframe(pd.DataFrame(inventory_data), use_container_width=True)
                                else:
                                    st.info("No inventory data available")

                        st.write("SKU Distribution Across Warehouses:")
                        sku_distribution = {}
                        for warehouse in env.warehouses.values():
                            for sku_id, quantity in warehouse.inventory.items():
                                if sku_id not in sku_distribution:
                                    sku_distribution[sku_id] = {}
                                sku_distribution[sku_id][warehouse.id] = quantity

                        if sku_distribution:
                            sku_data = []
                            for sku_id, warehouse_data in sku_distribution.items():
                                row = {'SKU': sku_id}
                                for warehouse_id in [wh.id for wh in env.warehouses.values()]:
                                    row[warehouse_id] = warehouse_data.get(warehouse_id, 0)
                                sku_data.append(row)

                            if sku_data:
                                sku_df = pd.DataFrame(sku_data)
                                st.dataframe(sku_df, use_container_width=True)

                        st.write("Vehicle Assignments:")
                        vehicle_data = []
                        for route_info in solution['routes']:
                            vehicle_id = route_info['vehicle_id']
                            order_id = route_info['order_id']
                            distance = route_info.get('distance', 0)

                            vehicle = None
                            for wh in env.warehouses.values():
                                for v in wh.vehicles:
                                    if v.id == vehicle_id:
                                        vehicle = v
                                        break
                                if vehicle:
                                    break

                            if vehicle:
                                vehicle_data.append({
                                    'Vehicle ID': vehicle_id,
                                    'Type': vehicle.type,
                                    'Home Warehouse': vehicle.home_warehouse_id,
                                    'Assigned Order': order_id,
                                    'Route Distance': f"{distance:.2f} km",
                                    'Status': 'Active' if distance > 0 else 'Inactive'
                                })

                        if vehicle_data:
                            vehicle_df = pd.DataFrame(vehicle_data)
                            st.dataframe(vehicle_df, use_container_width=True)
                        else:
                            st.info("No vehicle assignments available")

                    with tab3:
                        st.subheader("Vehicle Status")

                        st.write("All Vehicles and Their Status:")
                        all_vehicles = []
                        for warehouse in env.warehouses.values():
                            for vehicle in warehouse.vehicles:
                                is_active = any(route['vehicle_id'] == vehicle.id for route in solution['routes'])

                                all_vehicles.append({
                                    'Vehicle ID': vehicle.id,
                                    'Type': vehicle.type,
                                    'Home Warehouse': vehicle.home_warehouse_id,
                                    'Status': 'Active' if is_active else 'Inactive',
                                    'Capacity Weight': f"{vehicle.capacity_weight} kg",
                                    'Capacity Volume': f"{vehicle.capacity_volume} m³"
                                })

                        if all_vehicles:
                            vehicle_df = pd.DataFrame(all_vehicles)
                            st.dataframe(vehicle_df, use_container_width=True)
                        else:
                            st.info("No vehicles available")

                    with tab4:
                        st.subheader("Route Visualization")

                        if env.warehouses and env.orders:
                            all_lats = [wh.location.lat for wh in env.warehouses.values()] + [order.destination.lat for order in env.orders.values()]
                            all_lons = [wh.location.lon for wh in env.warehouses.values()] + [order.destination.lon for order in env.orders.values()]

                            center_lat = sum(all_lats) / len(all_lats)
                            center_lon = sum(all_lons) / len(all_lons)

                            m = folium.Map(
                                location=[center_lat, center_lon],
                                zoom_start=DEFAULT_SETTINGS.get('map_zoom_start', 10)
                            )

                            for warehouse in env.warehouses.values():
                                folium.Marker(
                                    [warehouse.location.lat, warehouse.location.lon],
                                    popup=f"Warehouse {warehouse.id}",
                                    icon=folium.Icon(color='red', icon='warehouse')
                                ).add_to(m)

                            for order_id, order in env.orders.items():
                                folium.Marker(
                                    [order.destination.lat, order.destination.lon],
                                    popup=f"Order {order_id}",
                                    icon=folium.Icon(color='blue', icon='info-sign')
                                ).add_to(m)

                            if solution and 'routes' in solution:
                                vehicle_types = {}
                                for route in solution['routes']:
                                    vehicle_id = route['vehicle_id']
                                    vehicle_type = vehicle_id.split('_')[0]
                                    if vehicle_type not in vehicle_types:
                                        vehicle_types[vehicle_type] = []
                                    vehicle_types[vehicle_type].append(vehicle_id)
                                
                                colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'darkblue', 'darkgreen']
                                
                                for i, route in enumerate(solution['routes']):
                                    vehicle_id = route['vehicle_id']
                                    vehicle_type = vehicle_id.split('_')[0]
                                    color_idx = list(vehicle_types.keys()).index(vehicle_type) % len(colors)
                                    color = colors[color_idx]
                                    
                                    route_coords = []
                                    for node_id in route['route']:
                                        if node_id in env.nodes:
                                            node = env.nodes[node_id]
                                            route_coords.append([node.lat, node.lon])
                                        elif node_id in env.warehouses:
                                            warehouse = env.warehouses[node_id]
                                            route_coords.append([warehouse.location.lat, warehouse.location.lon])
                                        elif node_id in env.orders:
                                            order = env.orders[node_id]
                                            route_coords.append([order.destination.lat, order.destination.lon])
                                    
                                    if len(route_coords) >= 2:
                                        folium.PolyLine(
                                            route_coords,
                                            color=color,
                                            weight=3,
                                            opacity=0.8,
                                            popup=f"Route {i+1}: {vehicle_id} ({route.get('distance', 0):.1f} km)"
                                        ).add_to(m)
                                        
                                        for j, coord in enumerate(route_coords):
                                            if j == 0:
                                                folium.CircleMarker(
                                                    coord,
                                                    radius=8,
                                                    color=color,
                                                    fill=True,
                                                    popup=f"Start: {vehicle_id}"
                                                ).add_to(m)
                                            elif j == len(route_coords) - 1:
                                                folium.CircleMarker(
                                                    coord,
                                                    radius=8,
                                                    color=color,
                                                    fill=True,
                                                    popup=f"End: {vehicle_id}"
                                                ).add_to(m)
                                            else:
                                                folium.CircleMarker(
                                                    coord,
                                                    radius=6,
                                                    color=color,
                                                    fill=True,
                                                    popup=f"Order {route.get('order_id', 'Unknown')}"
                                                ).add_to(m)
                                
                                legend_html = '''
                                <div style="position: fixed; 
                                            bottom: 50px; left: 50px; width: 200px; height: auto; 
                                            background-color: white; border:2px solid grey; z-index:9999; 
                                            font-size:14px; padding: 10px; border-radius: 5px;">
                                <p><b>Vehicle Routes</b></p>
                                '''
                                
                                for i, (vehicle_type, vehicle_ids) in enumerate(vehicle_types.items()):
                                    color = colors[i % len(colors)]
                                    legend_html += f'<p><i class="fa fa-circle" style="color:{color}"></i> {vehicle_type}</p>'
                                
                                legend_html += '</div>'
                                m.get_root().html.add_child(folium.Element(legend_html))

                            st.markdown("""
                                <style>
                                .map-container {
                                    width: 100% !important;
                                    max-width: none !important;
                                }
                                </style>
                                """, unsafe_allow_html=True)

                            with st.container():
                                st.components.v1.html(m._repr_html_(), height=600, scrolling=False)
                            
                            if solution and 'routes' in solution:
                                st.divider()
                                st.subheader("Detailed Route Information")
                                
                                for i, route in enumerate(solution['routes']):
                                    vehicle_id = route['vehicle_id']
                                    route_nodes = route['route']
                                    distance = route.get('distance', 0)
                                    order_id = route.get('order_id', 'Unknown')
                                    
                                    with st.expander(f"Vehicle {vehicle_id} - Route {i+1} ({distance:.2f} km)", expanded=True):
                                        
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Vehicle", vehicle_id)
                                        with col2:
                                            st.metric("Total Distance", f"{distance:.2f} km")
                                        with col3:
                                            st.metric("Order Served", order_id)
                                        
                                        st.write("**Path Details:**")
                                        path_data = []
                                        
                                        delivery_node_id = None
                                        if order_id in env.orders:
                                            delivery_node_id = env.get_order_location(order_id)

                                        for j, node_id in enumerate(route_nodes):
                                            if j == 0:
                                                node_type = "Warehouse (Start)"
                                            elif j == len(route_nodes) - 1:
                                                node_type = "Warehouse (Return)"
                                            elif delivery_node_id is not None and node_id == delivery_node_id:
                                                node_type = f"Delivery - Order {order_id}"
                                            else:
                                                node_type = "Path Node"

                                            if node_id in env.nodes:
                                                n = env.nodes[node_id]
                                                lat, lon = n.lat, n.lon
                                            else:
                                                lat, lon = "N/A", "N/A"

                                            leg_distance = 0.0
                                            if j < len(route_nodes) - 1:
                                                next_node_id = route_nodes[j + 1]
                                                d = env.get_distance(node_id, next_node_id)
                                                if d is None:
                                                    for edge in env.get_available_edges():
                                                        if (edge['from'] == node_id and edge['to'] == next_node_id) or \
                                                           (edge['from'] == next_node_id and edge['to'] == node_id):
                                                            d = edge['distance']
                                                            break
                                                leg_distance = float(d) if d is not None else 0.0

                                            path_data.append({
                                                'Step': j + 1,
                                                'Node ID': node_id,
                                                'Type': node_type,
                                                'Coordinates': f"({lat:.4f}, {lon:.4f})" if lat != "N/A" else "N/A",
                                                'Leg Distance': f"{leg_distance:.2f} km" if j < len(route_nodes) - 1 else "End"
                                            })
                                        
                                        path_df = pd.DataFrame(path_data)
                                        st.dataframe(path_df, use_container_width=True)
                                        
                                        st.write("**Route Statistics:**")
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Total Stops", len(route_nodes))
                                        with col2:
                                            st.metric("Delivery Points", len(route_nodes) - 2)
                                        with col3:
                                            if len(route_nodes) > 1:
                                                avg_leg_distance = distance / (len(route_nodes) - 1)
                                                st.metric("Avg Leg Distance", f"{avg_leg_distance:.2f} km")
                                            else:
                                                st.metric("Avg Leg Distance", "0 km")
                        else:
                            st.info("No location data available for map visualization")

                    with tab5:
                        st.subheader("Cost Analysis")

                        st.write("Cost Breakdown:")

                        cost_by_vehicle = {}
                        for route in solution['routes']:
                            vehicle_id = route['vehicle_id']
                            vehicle_type = vehicle_id.split('_')[0]
                            distance = route.get('distance', 0)

                            vehicle_specs = None
                            for spec in VEHICLE_FLEET_SPECS:
                                if spec['type'] == vehicle_type:
                                    vehicle_specs = spec
                                    break

                            if vehicle_specs:
                                route_cost = (vehicle_specs['cost_per_km'] * distance) + vehicle_specs['fixed_cost']

                                if vehicle_type not in cost_by_vehicle:
                                    cost_by_vehicle[vehicle_type] = {'total_cost': 0, 'total_distance': 0, 'routes': 0}

                                cost_by_vehicle[vehicle_type]['total_cost'] += route_cost
                                cost_by_vehicle[vehicle_type]['total_distance'] += distance
                                cost_by_vehicle[vehicle_type]['routes'] += 1

                        if cost_by_vehicle:
                            cost_data = []
                            for vehicle_type, data in cost_by_vehicle.items():
                                cost_data.append({
                                    'Vehicle Type': vehicle_type,
                                    'Routes': data['routes'],
                                    'Total Distance': f"{data['total_distance']:.2f} km",
                                    'Total Cost': f"${data['total_cost']:.2f}",
                                    'Avg Cost per Route': f"${data['total_cost']/data['routes']:.2f}"
                                })

                            cost_df = pd.DataFrame(cost_data)
                            st.dataframe(cost_df, use_container_width=True)
                        else:
                            st.info("No cost data available")

                    with tab6:
                        st.subheader("Orders View")

                        st.write("All Orders:")
                        orders_data = []
                        for order_id, order in env.orders.items():
                            is_served = any(route['order_id'] == order_id for route in solution['routes'])

                            orders_data.append({
                                'Order ID': order_id,
                                'Location': f"({order.destination.lat:.4f}, {order.destination.lon:.4f})",
                                'Items': len(order.requested_items),
                                'Status': "Served" if is_served else "Pending",
                                'Details': str(order.requested_items)
                            })

                        if orders_data:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Orders", len(orders_data))
                            with col2:
                                served_count = sum(1 for order in orders_data if order['Status'] == "Served")
                                st.metric("Orders Served", served_count, delta=f"{served_count}/{len(orders_data)}")
                            with col3:
                                pending_count = len(orders_data) - served_count
                                st.metric("Orders Pending", pending_count, delta=f"{pending_count}/{len(orders_data)}")

                            orders_df = pd.DataFrame(orders_data)
                            st.dataframe(orders_df, use_container_width=True)
                        else:
                            st.info("No orders available")

                else:
                    st.error("Solver failed or returned no routes")
                    st.session_state['solution'] = None

            except Exception as e:
                st.error(f"Solver failed with exception: {str(e)}")
                st.error(f"Exception type: {type(e).__name__}")
                import traceback
                st.error(f"Full traceback: {traceback.format_exc()}")
                st.session_state['solution'] = None

    st.divider()

    st.header("How to Use")
    st.write("""
    1. **Review Infrastructure**: Examine the fixed SKU types, vehicle fleet, and warehouse locations above
    2. **Configure Demand**: Set order count, items per order, and SKU distribution in the Demand tab
    3. **Configure Supply**: Set inventory distribution and vehicle fleet for each warehouse in the Supply tab
    4. **Run Simulation**: Click "Run Simulation" to generate and solve the problem
    5. **Analyze Results**: The comprehensive dashboard will open with detailed analysis tabs

    **Tip**: Start with smaller problems (5-10 orders) to test your solver, then scale up!
    """)

if __name__ == "__main__":
    if 'env' not in st.session_state:
        st.session_state['env'] = None
    if 'solution' not in st.session_state:
        st.session_state['solution'] = None

    if st.session_state.get('env') is None:
        try:
            from robin_logistics import LogisticsEnvironment
            st.session_state['env'] = LogisticsEnvironment()
        except Exception as e:
            st.error(f"Failed to create environment: {str(e)}")
            st.stop()

    run_dashboard(st.session_state.get('env'))
