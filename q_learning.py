import numpy as np
from environment import ElevatorEnv
import random

env = ElevatorEnv()


q_table = {}

alpha = 0.1
gamma = 0.95
epsilon = 0.5 
def get_q(state, action):
    if state not in q_table:
        q_table[state] = [0.0, 0.0, 0.0]
    return q_table[state][action]

def get_max_q(state):
    if state not in q_table:
        q_table[state] = [0.0, 0.0, 0.0]
    return np.max(q_table[state])

def get_best_action(state):
    if state not in q_table:
        q_table[state] = [0.0, 0.0, 0.0]
    return int(np.argmax(q_table[state]))

def train(episodes=15000):
    global epsilon, q_table
    
    for e in range(episodes):
        state = env.reset()
        done = False
        steps = 0
        
        while not done and steps < 60: # Limit steps to prevent infinite loops early on
            if random.uniform(0, 1) < epsilon:
                action = random.randint(0, 2)
            else:
                action = get_best_action(state)
                
            next_state, reward, done = env.step(action)
            
            old_q = get_q(state, action)
            next_max = get_max_q(next_state)
            
            # Q-Learning Formula
            new_q = old_q + alpha * (reward + gamma * next_max - old_q)
            q_table[state][action] = new_q
            
            state = next_state
            steps += 1
            
        # Decay epsilon to favor exploitation over time
        if epsilon > 0.05:
            epsilon *= 0.9995