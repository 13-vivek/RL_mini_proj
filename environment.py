import random

class ElevatorEnv:
    def __init__(self):
        self.max_floor = 5
        self.reset()

    def reset(self, specific_people=None):
        self.current_floor = 1
        self.inside_people = [] # List of target floors for people inside
        
        if specific_people is not None:
            self.waiting_people = specific_people
        else:
            self.waiting_people = []
            num_people = random.randint(1, 3)
            for _ in range(num_people):
                start = random.randint(1, 5)
                target = random.randint(1, 5)
                while start == target:
                    target = random.randint(1, 5)
                # Ensure we don't have exact duplicate starting floors to simplify UI later
               
                if not any(p[0] == start for p in self.waiting_people):
                    self.waiting_people.append((start, target))
            
        return self._get_state()

    def _get_state(self):
       
        requests = tuple(any(p[0] == f for p in self.waiting_people) for f in range(1, 6))
        destinations = tuple(any(t == f for t in self.inside_people) for f in range(1, 6))
        return (self.current_floor, requests, destinations)

    def step(self, action):
        reward = -1 # Base time penalty
        done = False
        
        # Actions: 0 = UP, 1 = DOWN, 2 = OPEN DOORS
        if action == 0:
            if self.current_floor < 5:
                self.current_floor += 1
            else:
                reward -= 10 # Penalty for hitting the roof
        elif action == 1:
            if self.current_floor > 1:
                self.current_floor -= 1
            else:
                reward -= 10 # Penalty for hitting the basement
        elif action == 2:
            opened_for_reason = False
            
            # Unload people whose target is the current floor
            if self.current_floor in self.inside_people:
                count = self.inside_people.count(self.current_floor)
                reward += 30 * count # Big reward for dropoff
                self.inside_people = [t for t in self.inside_people if t != self.current_floor]
                opened_for_reason = True
                
            # Load people waiting on this floor
            waiting_here = [p for p in self.waiting_people if p[0] == self.current_floor]
            if waiting_here:
                for p in waiting_here:
                    self.inside_people.append(p[1]) # Add their target to inside
                    self.waiting_people.remove(p)
                    reward += 15 # Reward for pickup
                opened_for_reason = True
                
            if not opened_for_reason:
                reward -= 10 # Heavy penalty for opening doors needlessly

        # Episode ends when all people are delivered
        if len(self.waiting_people) == 0 and len(self.inside_people) == 0:
            done = True
            
        return self._get_state(), reward, done