from __future__ import annotations
import math

import evaluation
from rescue_core.actions import ACTION_ORDER


class Agent:
    def get_action(self, game_state):
        raise NotImplementedError


# === Q1 SELF-REFLECTION (1 point) ===
# Write 3-5 sentences below, at least 25 words total.
# This is a no-GenAI/coding-assistant assignment.
# State that you did not use GenAI, AI tools, coding assistants,
# posted solutions, or online resources that solve this project.
# Say how you checked your answer using course/local project resources.
# Include at least one concrete project detail, such as a function name,
# file name, map name, test id, or command you ran.
# Include one sentence explaining the Q1 reflex-agent concept in your own words.
#
# YOUR RESPONSE:
# I did not use GenAI, AI tools, coding assistants, posted solutions, or online resources that solve this project.
# I use the "python3.13 rescue.py --map training_corner --agent reflex" test and the "python3.13 autograder.py -q q1" test to check my response.
# The reflex-agent is that the agent only exaime the current state using the weight I assinged, chosing the highest score returned without planning to the future states. 
# === END Q1 SELF-REFLECTION ===

class ReflexRescueAgent(Agent):
    """A reflex agent chooses one action by scoring immediate successors."""

    def get_action(self, game_state):
        legal = game_state.get_legal_actions(0)
        if not legal:
            return "Stop"
        scores = [(self.evaluation_function(game_state, action), action) for action in legal]
        return max(scores, key=lambda item: (item[0], -ACTION_ORDER.index(item[1])))[1]

    def evaluation_function(self, current_game_state, action):
        """Return a number describing how desirable this immediate action is.

        Useful features include:
        - successor score,
        - distance to the nearest remaining survivor,
        - distance back to triage base after all survivors are secured,
        - distance to the nearest hazard,
        - remaining battery.
        """
        # TODO: Question 1
        
        successor = current_game_state.generate_successor(0, action)

        # Get Scores
        score = successor.get_score()
        robot = successor.get_robot_position()
        survivors = successor.get_survivor_positions()
        hazards = successor.get_hazard_positions()
        base = successor.get_base_position()
        battery = successor.get_battery()

        # Edge Case: Make terminal action (wining & losing action) substantial compared to the normal action
        if successor.is_win():
            return 999999
        if successor.is_loss():
            return -999999

        # Rescuing survivors: Since sucessfully rescusing a survivor add 30 to the offical game score, 
        # my evaluation funciton is designed to add 40 per rescue to the heuristics. 
        old_survivors = current_game_state.get_survivor_positions()
        SucessfullyRescued = len(old_survivors) - len(survivors)
        score += 40 * SucessfullyRescued

        # Prioritized moving toward the nearest survivors
        if survivors:
            distance_s = []
            for s in survivors:
                distance_ts = abs(robot.row - s.row) + abs(robot.col - s.col)
                distance_s.append(distance_ts)
            score = score - 4 * min(distance_s)

        # If no survivors left, Prioritized moving toward the base
        else: 
            distance_s = abs(robot.row - base.row) + abs(robot.col - base.col)
            score = score - 4 * distance_s #Shorter distance better score

        # Avoiding getting close to hazards
        if hazards:
            distance_h = []
            for h in hazards:
                distance_th = abs(robot.row - h.row) + abs(robot.col - h.col)
                distance_h.append(distance_th)       
            nearest_distanceToHaz = min(distance_h)
            
            if nearest_distanceToHaz <= 1:
                score = score - 30
            elif nearest_distanceToHaz == 2:
                score = score - 5

        return score
    

class MultiAgentSearchAgent(Agent):
    """Common settings for minimax, alpha-beta, and expectimax agents.

    depth counts RescueBot moves. A depth of 2 means RescueBot plans two of
    its own actions ahead, with every hazard agent moving after each one.
    """

    def __init__(self, eval_fn="score_evaluation_function", depth=2):
        if isinstance(eval_fn, str):
            self.evaluation_function = getattr(evaluation, eval_fn)
        else:
            self.evaluation_function = eval_fn
        self.depth = int(depth)


# === Q2 SELF-REFLECTION (1 point) ===
# Write 3-5 sentences below, at least 25 words total.
# This is a no-GenAI/coding-assistant assignment.
# State that you did not use GenAI, AI tools, coding assistants,
# posted solutions, or online resources that solve this project.
# Say how you checked your answer using course/local project resources.
# Include at least one concrete project detail, such as a function name,
# file name, map name, test id, or command you ran.
# Include one sentence explaining the Q2 minimax concept in your own words.
#
# YOUR RESPONSE:
# I did not use GenAI, AI tools, coding assistants, posted solutions, or online resources that solve this project.
# I use the "python3.13 autograder.py -q q2" test to check my response.
# The robot is the maximize agent who makes actions based on the minimizing agent, the hazards; Unlike Q1 which consider the immeditae score,
# Q2 use recursion to calculate future states up to the assigned depth. 
# === END Q2 SELF-REFLECTION ===

class MinimaxAgent(MultiAgentSearchAgent):
    """Worst-case planner.

    RescueBot is agent 0 and maximizes value. Each hazard agent minimizes
    value. Cycle agent indices 0, 1, ..., get_num_agents() - 1; decrement
    depth only when the next turn returns to RescueBot.
    """

    def get_action(self, game_state):
        # TODO: Question 2

        number_agents = game_state.get_num_agents()
        
        def minimaxalgorithm(state, agent, depth):
            # Base Case
            if state.is_win() or state.is_loss() or depth == 0:
                return self.evaluation_function(state)
            actions = state.get_legal_actions(agent)

            # Agent Switching
            next_agent = agent + 1
            next_depth = depth # Hazards' move don't count as the Robot's move
            if next_agent == number_agents:
                next_agent = 0
                next_depth = depth - 1

            # Calculate Score
            scores = []
            for action in actions:
                next_state = state.generate_successor(agent, action)
                score = minimaxalgorithm(next_state, next_agent, next_depth)
                scores.append(score)
                
            # Define Min/Max Agent
            if agent == 0:
                return max(scores)
            else:
                return min(scores)

        # Chose the actions
        actions = game_state.get_legal_actions(0)

        #Initialize
        best_action = actions[0]
        best_score = float(-999999999)
        next_agent = 1 % number_agents
        next_depth = self.depth
            
        for action in actions:
            next_state = game_state.generate_successor(0, action)
            score = minimaxalgorithm(next_state, next_agent, next_depth)

        # Compare the scores
            if score > best_score:
                best_score = score
                best_action = action
        return best_action


# === Q3 SELF-REFLECTION (1 point) ===
# Write 3-5 sentences below, at least 25 words total.
# This is a no-GenAI/coding-assistant assignment.
# State that you did not use GenAI, AI tools, coding assistants,
# posted solutions, or online resources that solve this project.
# Say how you checked your answer using course/local project resources.
# Include at least one concrete project detail, such as a function name,
# file name, map name, test id, or command you ran.
# Include one sentence explaining the Q3 alpha-beta concept in your own words.
#
# YOUR RESPONSE:
# I did not use GenAI, AI tools, coding assistants, posted solutions, or online resources that solve this project.
# I use the  "python3.13 autograder.py -q q3" test to check my response.
# The alpha/beta use similar algorithm and rules compared with the Minmax, but it use less computational power by pruning, which break the recursion by comparing the alpha and beta value. Namely, alphabeta can avoid exploring future states that cannot affect the final decision.
# === END Q3 SELF-REFLECTION ===

class AlphaBetaAgent(MultiAgentSearchAgent):
    """Minimax with alpha-beta pruning.

    Return the same action as MinimaxAgent while pruning branches that
    cannot change the decision. Carry alpha across RescueBot's root actions
    as well as through recursive max nodes.
    """

    def get_action(self, game_state):
        # TODO: Question 3

        number_agents = game_state.get_num_agents()
        
        def alphabetaAlgorithm(state, agent, depth, alpha, beta):
            # Base Case
            if state.is_win() or state.is_loss() or depth == 0:
                return self.evaluation_function(state)
            actions = state.get_legal_actions(agent)

            # Agent Switching
            next_agent = agent + 1
            next_depth = depth # Hazards' move don't count as the Robot's move
            if next_agent == number_agents:
                next_agent = 0
                next_depth = depth - 1

            # Robot (Max Agent)
            if agent == 0:
                current_best_score = float("-inf")

                for action in actions:
                    next_state = state.generate_successor(agent, action)
                    score = alphabetaAlgorithm(next_state, next_agent, next_depth, alpha, beta)
                    current_best_score = max(current_best_score, score)
                    alpha = max(alpha, current_best_score)
                    if alpha >= beta:
                        break
                return current_best_score

            # Hazard (Min Agent)
            else: 
                current_best_score = float("inf")
                
                for action in actions:
                    next_state = state.generate_successor(agent, action)
                    score = alphabetaAlgorithm(next_state, next_agent, next_depth, alpha, beta)
                    current_best_score = min(current_best_score, score)
                    beta = min(beta, current_best_score)
                    if alpha >= beta:
                        break
                return current_best_score

        # 5. Choose the best action
        actions = game_state.get_legal_actions(0)
        
        # Initialize
        best_action = actions[0]
        current_best_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")
        next_agent = 1 % number_agents
        next_depth = self.depth

        
        for action in actions:
            next_state = game_state.generate_successor(0, action)
            score = alphabetaAlgorithm(next_state, next_agent, next_depth, alpha, beta)

            if score > current_best_score:
                current_best_score = score
                best_action = action
            alpha = max(alpha, current_best_score)
            
        return best_action

            

# === Q4 SELF-REFLECTION (1 point) ===
# Write 3-5 sentences below, at least 25 words total.
# This is a no-GenAI/coding-assistant assignment.
# State that you did not use GenAI, AI tools, coding assistants,
# posted solutions, or online resources that solve this project.
# Say how you checked your answer using course/local project resources.
# Include at least one concrete project detail, such as a function name,
# file name, map name, test id, or command you ran.
# Include one sentence explaining the Q4 expectimax concept in your own words.
#
# YOUR RESPONSE:
# Write your response here.
# === END Q4 SELF-REFLECTION ===

class ExpectimaxAgent(MultiAgentSearchAgent):
    """Expected-value planner.

    RescueBot is still a max agent. Hazard nodes are chance nodes: average
    all legal successor values, including when there are multiple hazards.
    """

    def get_action(self, game_state):
        # TODO: Question 4
        raise NotImplementedError
