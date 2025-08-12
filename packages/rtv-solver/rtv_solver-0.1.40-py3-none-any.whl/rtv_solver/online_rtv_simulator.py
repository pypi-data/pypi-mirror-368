from handlers.request_handler import RequestHandler
from handlers.network_handler import NetworkHandler
from handlers.vehicle_handler import VehicleHandler
from handlers.trip_handler import TripHandler
from handlers.payload_parser import PayloadParser

class OnlineRTVSimulator:

    def __init__(self,server_url,SHAREABLE_COST_FACTOR=1,RTV_TIMEOUT=30, LARGEST_TSP = 10):
        self.ILP_SOLVER_TIMEOUT = 10 # seconds
        self.RTV_TIMEOUT = RTV_TIMEOUT #seconds
        self.PENALTY = 1000000 # penalty for not serving a trip
        self.SHAREABLE_COST_FACTOR = SHAREABLE_COST_FACTOR
        self.MAX_CARDINALITY = 4
        self.MAX_THREAD_CNT = 500
        self.REBALANCING = False
        self.RH_FACTOR = 0
        self.DWELL_PICKUP = 180
        self.DWELL_ALIGHT = 60
        self.LARGEST_TSP = LARGEST_TSP
        # NetworkHandler.init(True,server_url)

    def simulate_vehicles(self, payload, current_time):
        payload_object = PayloadParser.get_payload_object(payload,False)
        start_of_the_day = payload_object.start_of_the_day
        request_handler = RequestHandler(payload_object.requests, start_of_the_day, self.DWELL_PICKUP, self.DWELL_ALIGHT)
        vehicle_handler = VehicleHandler(payload_object.depot, payload_object.driver_runs,None,start_of_the_day,LARGEST_TSP=self.LARGEST_TSP)
        vehicle_handler.add_manifest_to_vehicles(current_time,start_of_the_day,payload_object.driver_runs,boarded_requests,boarded_trips,self.DWELL_ALIGHT, self.DWELL_PICKUP)
        completed_stops, picked_requests, completed_requests = vehicle_handler.simulate_vehicles(current_time)
        for req_id in picked_requests:
            boarded_requests[req_id] = active_requests[req_id]
            active_requests.pop(req_id)
        for req_id in completed_requests:
            boarded_requests.pop(req_id)
            
    def solve_rtv(self, payload):
        payload_object = PayloadParser.get_payload_object(payload,False)
        start_of_the_day = payload_object.start_of_the_day
        request_handler = RequestHandler(payload_object.requests, start_of_the_day, self.DWELL_PICKUP, self.DWELL_ALIGHT)
        temp_batch = request_handler.get_all_requests()
        batch = []
        active_requests = {}
        boarded_requests = {}
        for req in temp_batch:
            req_id = req.id
            if req_id in payload_object.boarded_requests:
                boarded_requests[req_id] = req
            else:
                if req_id in payload_object.active_requests:
                    active_requests[req_id] = req
                batch.append(req)

        current_time = payload_object.current_time
        iteration = 0
        boarded_trips = TripHandler.create_trip_for_picked_requests(boarded_requests,iteration)

        vehicle_handler = VehicleHandler(payload_object.depot, payload_object.driver_runs,None,start_of_the_day,LARGEST_TSP=self.LARGEST_TSP)
        vehicle_handler.add_manifest_to_vehicles(current_time,start_of_the_day,payload_object.driver_runs,boarded_requests,boarded_trips,self.DWELL_ALIGHT, self.DWELL_PICKUP)

        iteration+=1
        trip_handler = TripHandler(current_time,vehicle_handler.vehicles,batch, active_requests, iteration, self.ILP_SOLVER_TIMEOUT,self.PENALTY,self.MAX_CARDINALITY,self.MAX_THREAD_CNT,self.SHAREABLE_COST_FACTOR,self.REBALANCING,self.RTV_TIMEOUT)
        for vehicle_id in trip_handler.vehicle_assignment:
            vehicle = vehicle_handler.vehicles[vehicle_id]
            trips = trip_handler.vehicle_assignment[vehicle_id]
            VehicleHandler.add_new_trips(current_time, vehicle, trips, add=True)

        # create updated driver runs
        updated_driver_runs = []
        for driver_run in payload_object.driver_runs:
            new_state = driver_run[PayloadParser.DRIVER_STATE]
            manifest = driver_run[PayloadParser.DRIVER_MANIFEST]
            new_manifest = []
            current_order = new_state[PayloadParser.DRIVER_STATE_LOC_SERV]
            if len(manifest) > 0:
                new_manifest.append(manifest[0])
                current_order=manifest[0][PayloadParser.DRIVER_STATE_ORDER]
            vehicle = vehicle_handler.vehicles[new_state[PayloadParser.DRIVER_STATE_RUN_ID]]
            new_manifest.extend(VehicleHandler.get_manifest(vehicle,current_order,start_of_the_day))
            new_state[PayloadParser.DRIVER_STATE_T_LOCS] = new_state[PayloadParser.DRIVER_STATE_T_LOCS] + len(new_manifest) - len(manifest)
            new_driver_run = {PayloadParser.DRIVER_STATE:new_state,PayloadParser.DRIVER_MANIFEST:new_manifest}
            updated_driver_runs.append(new_driver_run)

        new_payload = payload
        new_payload["driver_runs"] = updated_driver_runs
        new_payload["requests"] = []
        return new_payload
