import gym
import matplotlib.pyplot as plt
import numpy as np
import random



def main(n_trials=500):
    legalActions = (0, 1)
    features = {"cartPosition":0, "cartVelocity":0, "poleAngle":0, "poleVelocity":0}
    weights = {"cartPosition":0, "cartVelocity":0, "poleAngle":0, "poleVelocity":0}

    gamma = 0.8
    alpha = 0.1

    # Epsilon should drop out at about 17 episodes
    epsilon = [0]
    epsilonMin = 0.01
    epsilonDecay = 0.999

    testEnv = gym.make('CartPole-v0').env
    testEnv.reset()

    numberFails = []


    def computeAction(observation):
        testValues = {action:computeValueFromAction(action, observation) for action in legalActions}
        return random.choice(legalActions) if (np.random.random() <= epsilon[0]) else max(testValues, key = testValues.get)


    # What is the qValue of the next state for taking this action
    def computeValueFromAction(action, observation):
        # Set testEnv state to current actual state
        testEnv.state = observation

        # Take hypothetical step in testEnv
        (testObservation, _, done, _) = testEnv.step(action)
        testEnv.reset()

        # Make features from future state
        futureFeatures = {"cartPosition":1, "cartVelocity":1, "poleAngle":1, "poleVelocity":1}
        getFeatures(futureFeatures, testObservation)
        return getQValue(futureFeatures) if done else 1 + getQValue(futureFeatures)


    # The sum of all features multiplied by their weights for this state
    # Used by both acutal features and futureFeatures
    def getQValue(features):
        return sum([weights[key] * features[key] for key in weights.keys()])


    # Update the weights
    def update(observation, step_reward, action, features):
        difference = (step_reward + gamma * computeValueFromAction(action, observation)) - getQValue(features)
        for key in weights.keys():
            weights[key] = weights[key] + alpha * features[key] * difference
        # return {key:weights[key] + alpha * features[key] * difference for key in weights.keys()}


    def decayEpsilon(epsilon):
        if epsilon[0] > epsilonMin:
            epsilon[0] *= epsilonDecay


    def getFeatures(features, observation):
        (cartPosition, cartVelocity, poleAngle, poleVelocity) = observation
        features["poleAngle"] = abs(poleAngle)
        features["poleVelocity"] = 3 - abs(poleVelocity)
        features["cartPosition"] = abs(cartPosition)
        features["cartVelocity"] = abs(cartVelocity)


    def episode_reward(weights, epsilon, env=gym.make('CartPole-v0')):
        observation = env.reset()
        total_reward = 0

        # try to last 200 steps
        for _ in range(200):
            # Update features based on observation
            getFeatures(features, observation)
            # Find best action
            action = computeAction(observation)

            # Step environment based on best action
            (observation, step_reward, done, info) = env.step(action)

            total_reward += step_reward

            decayEpsilon(epsilon)
            update(observation, step_reward, action, features)

            # env.render()
            if done:
                return total_reward


    def train(trial_nbr):
        reward = episode_reward(weights, epsilon)
        # Process failed trials
        if reward < 200:
            numberFails.append(trial_nbr)
        return reward


    def print_plot_results(max_episodes):
        print('\nmax steps: {}; avg steps: {}'. \
              format(max_episodes, round(sum(trainResults)/n_trials, 1)))
        plt.plot(trainResults)
        plt.xlabel('Trial number')
        plt.ylabel('Reward')
        plt.title('Pole Features Learning')
        plt.show()

    def runWeights(weights, env=gym.make('CartPole-v0')):
        env._max_episode_steps = 20000
        observation = env.reset()
        total_reward = 0

        # see how long it lasts
        for _ in range(20000):
            # Update features based on observation
            getFeatures(features, observation)
            # Find best action
            action = computeAction(observation)

            # Step environment based on best action
            (observation, step_reward, done, info) = env.step(action)

            total_reward += step_reward

            env.render()
            if done:
                return total_reward

    trainResults = [train(trial_nbr + 1) for trial_nbr in range(n_trials)]

    print('final weights:')
    for key in weights.keys():
        print('{}: {}, '.format(key, round(weights[key], 4)))
    print('number of failed trials: {}'.format(len(numberFails)))
    # print_plot_results(max(trainResults))

    runResults = [runWeights(weights)]
    print(runResults)
main()
