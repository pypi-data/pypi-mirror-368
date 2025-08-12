
import copy

class SimulationEngine:
    """Runs a stateful, dynamic simulation of a logistics plan."""
    def __init__(self, environment, solution):
        self.env = copy.deepcopy(environment)
        self.solution = copy.deepcopy(solution)
        self.all_vehicles_by_id = {v.id: v for v in self.env.get_all_vehicles()}

    def run_simulation(self):
        """Executes the entire simulation and returns the final state and logs."""
        logs = {}
        total_cost = 0

        routes = self.solution.get("routes", [])
        if isinstance(routes, list):
            for route_info in routes:
                vehicle_id = route_info.get('vehicle_id')
                route = route_info.get('route', [])
                vehicle = self.all_vehicles_by_id[vehicle_id]
                log, route_cost, is_valid, message = self._simulate_route(vehicle, route)
                logs[vehicle_id] = log
                if not is_valid:
                    final_state = self._get_final_state(is_valid=False, message=message, total_cost=total_cost, orders_delivered=0)
                    return final_state, logs
                total_cost += route_cost
        else:
            for vehicle_id, route in routes.items():
                vehicle = self.all_vehicles_by_id[vehicle_id]
                log, route_cost, is_valid, message = self._simulate_route(vehicle, route)
                logs[vehicle_id] = log
                if not is_valid:
                    final_state = self._get_final_state(is_valid=False, message=message, total_cost=total_cost, orders_delivered=0)
                    return final_state, logs
                total_cost += route_cost
        
        delivered_orders = set()
        if isinstance(routes, list):
            for route_info in routes:
                route = route_info.get('route', [])
                orders_on_route = [o for o in self.env.orders.values() if o.destination.id in route]
                delivered_orders.update([o.id for o in orders_on_route])
        else:
            for vehicle_id, route in routes.items():
                orders_on_route = [o for o in self.env.orders.values() if o.destination.id in route]
                delivered_orders.update([o.id for o in orders_on_route])
        
        if len(delivered_orders) != len(self.env.orders):
            msg = f"Not all orders were delivered. Required: {len(self.env.orders)}, Delivered: {len(delivered_orders)}"
            final_state = self._get_final_state(is_valid=False, message=msg, total_cost=total_cost, orders_delivered=len(delivered_orders))
            return final_state, logs

        final_state = self._get_final_state(is_valid=True, message="All routes valid and all orders delivered.", total_cost=total_cost, orders_delivered=len(delivered_orders))
        return final_state, logs

    def _simulate_route(self, vehicle, route):
        """Simulates a single vehicle's route, updating state dynamically."""
        log = [f"### Journey for **{vehicle.id}** from Warehouse **{vehicle.home_warehouse_id}**"]
        total_dist = 0

        orders_on_route = [o for o in self.env.orders.values() if o.destination.id in route]
        pickup_plan = self._plan_pickups(orders_on_route)
        for wh_id, items in pickup_plan.items():
            wh_node = self.env.warehouses[wh_id].location.id
            log.append(f"**→ Travel to {wh_id} for pickup**")
            for sku, qty in items.items():

                if not self.env.warehouses[wh_id].pickup_items(sku, qty):
                    return log, 0, False, f"Inventory error at {wh_id}: Not enough {sku.id}."
                vehicle.load_item(sku, qty)
                log.append(f"  - **Action:** Picked up `{qty}x {sku.id}`.")

        log.append(f"  - **Load Status:** {vehicle.current_weight:.1f}kg, {vehicle.current_volume:.2f}m³")


        if vehicle.current_weight > vehicle.capacity_weight or vehicle.current_volume > vehicle.capacity_volume:
            return log, 0, False, "Vehicle overloaded after pickups."


        for i in range(len(route) - 1):
            start_node, end_node = route[i], route[i+1]
            dist = self.env.get_distance(start_node, end_node)
            total_dist += dist


            for order in orders_on_route:
                if order.destination.id == end_node:
                    log.append(f"**→ Travel {dist:.2f} km to Customer**")
                    log.append(f"  - **Action:** Deliver Order `{order.id}`.")
                    vehicle.unload_order(order)
                    log.append(f"  - **New Load Status:** {vehicle.current_weight:.1f}kg, {vehicle.current_volume:.2f}m³")


        if total_dist > vehicle.max_distance:
            return log, 0, False, f"Exceeded max distance ({total_dist:.2f}/{vehicle.max_distance} km)."

        route_cost = vehicle.fixed_cost + (total_dist * vehicle.cost_per_km)
        log.append(f"**End of Route. Total Distance: {total_dist:.2f} km, Cost: {route_cost:.2f}**")
        return log, route_cost, True, "Route successful."

    def _plan_pickups(self, orders):
        """Creates an optimal plan to pick up all items for a set of orders."""

        required_items = {}
        for order in orders:
            for sku, qty in order.requested_items.items():
                required_items[sku] = required_items.get(sku, 0) + qty

        pickup_plan = {}
        for sku, total_qty in required_items.items():
            best_wh, min_dist = None, float('inf')
            for wh in self.env.warehouses:
                if wh.inventory.get(sku, 0) >= total_qty:
                    dist = self.env.get_distance(self.env.warehouses[0].location.id, wh.location.id)
                    if dist < min_dist:
                        min_dist, best_wh = dist, wh

            if best_wh:
                if best_wh.id not in pickup_plan:
                    pickup_plan[best_wh.id] = {}
                pickup_plan[best_wh.id][sku] = total_qty

        return pickup_plan

    def _get_final_state(self, is_valid, message, total_cost=0.0, orders_delivered=0):
        """Assembles the final results dictionary."""
        return {
            "is_valid": is_valid,
            "message": message,
            "total_cost": total_cost,
            "vehicles_used": len(self.solution.get("routes", {})),
            "orders_delivered": orders_delivered
        }