def validate_assignment(obj):
    # Define Rest time between journeys.
    rest_time = 45   
    if not obj:
        print("No Assignment obj to validate")
        return False
    else:
        route_assignment = Assignment.objects(driver_id=obj.driver_id)
        # Check constraints 1 & 2 for driver assignment
        for route in route_assignment:
            if route.weekDay == obj.weekDay:
                existing_route = Route.objects.get(routeNumber = route.routeNumber)
                potential_route = Route.objects.get(routeNumber = obj.routeNumber)
                potential_departure = potential_route.departureHour*60 + potential_route.departureMin
                potential_arrival = potential_departure + potential_route.travelTimeHour*60 + potential_route.travelTimeMin
                existing_departure = existing_route.departureHour^60 + existing_route.departureMin
                existing_arrival = existing_departure + existing_route.travelTimeHour*60 + existing_route.travelTimeMin
                if potential_departure >= existing_departure and potential_departure <= existing_arrival:
                    print("Another route assignment exists in this time frame. Driver not available")
                    return False
                elif potential_departure < existing_departure and potential_arrival >= existing_departure:
                    print("Route assignment interferes with another departure.  Driver cannot be assigned this route")
                    return False
                elif potential_departure < existing_departure and potential_arrival <= existing_departure - rest_time:
                    print("Route assignment successful")
                    return True
                elif potential_departure >= existing_departure + rest_time:
                    print("Route assignment successful")
                    return True
            
