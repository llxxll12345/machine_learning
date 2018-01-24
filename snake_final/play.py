import snaky as game
import cv2
import numpy as np
import tensorflow as tf
import random
from collections import deque
import time

class DQN:
    def __init__(self, DISCFT, FLAG, INIT_EPSILON, FIN_EPSILON, REPLAY_MEMORY, BATCH_SIZE, ACTIONS):
        # current epoch and episode
        self.epoch = 0
        self.episode = 0
        # minimun number of observes before training
        self.observe = 10000
        # discount factor
        self.discft = DISCFT
        # mark the training status
        self.flag = FLAG
        # initial epsilon
        self.epsilon = INIT_EPSILON
        # final epsilon
        self.final_epsilon = FIN_EPSILON
        # sizse of replay memory
        self.REPLAYMEM = REPLAY_MEMORY
        # size of a sample batch
        self.batchsize = BATCH_SIZE
        # action list
        self.actions = ACTIONS
        self.repmem = deque()
        # structure of the network
        # network layer 1 -> weight and bias
        self.w1 = tf.Variable(tf.truncated_normal([8, 8, 4, 32], stddev = 0.01))
        self.b1 = tf.Variable(tf.constant(0.01, shape = [32]))
        # network layer 2 -> weight and bias
        self.w2 = tf.Variable(tf.truncated_normal([4, 4, 32, 64], stddev=0.01))
        self.b2 = tf.Variable(tf.constant(0.01, shape = [64]))
        # network layer 3 -> weight and bias
        self.w3 = tf.Variable(tf.truncated_normal([3, 3, 64, 64], stddev = 0.01))
        self.b3 = tf.Variable(tf.constant(0.01, shape = [64]))
        # weight and bias of fully connected layer
        self.wfc = tf.Variable(tf.truncated_normal([2304, 512], stddev = 0.01))
        self.bfc = tf.Variable(tf.constant(0.01, shape = [512]))
        # weight and bias of the layer to result
        self.wto = tf.Variable(tf.truncated_normal([512, self.actions], stddev = 0.01))
        self.bto = tf.Variable(tf.constant(0.01, shape = [self.actions]))
        self.init_conv_net()
        self.init_nn()
    
    def init_conv_net(self):
    	# methods of the network
    	# placeholder of input
        self.input = tf.placeholder("float", [None, 84, 84, 4])
        
        # Convolutional Neural Network
        # zero-padding
        # 84 x 84 x 4
        # 8 x 8 x 4 with 32 Filters
        # Stride 4 -> Output 21 x 21 x 32 -> max_pool 11 x 11 x 32
        tf.nn.conv2d(self.input, self.w1, strides = [1, 4, 4, 1], padding = "SAME")
        convolute_1 = tf.nn.relu(tf.nn.conv2d(self.input, self.w1, strides = [1, 4, 4, 1], padding = "SAME") + self.b1)
        pooling = tf.nn.max_pool(convolute_1, ksize = [1, 2, 2, 1], strides = [1, 2, 2, 1], padding = "SAME")
        
        # 11 x 11 x 32
        # 4 x 4 x 32 with 64 Filters
        # Stride 2 -> Output 6 x 6 x 64
        convolute_2 = tf.nn.relu(tf.nn.conv2d(pooling, self.w2, strides = [1, 2, 2, 1], padding = "SAME") + self.b2)
        
        # 6 x 6 x 64
        # 3 x 3 x 64 with 64 Filters
        # Stride 1 -> Output 6 x 6 x 64
        convolute_3 = tf.nn.relu(tf.nn.conv2d(convolute_2, self.w3, strides = [1, 1, 1, 1], padding = "SAME") + self.b3)
        
        # 6 x 6 x 64 = 2304
        c3_reshaped = tf.reshape(convolute_3, [-1, 2304])

        # Matrix (1, 2304) * (2304, 512)
        fully_connected = tf.nn.relu(tf.matmul(c3_reshaped, self.wfc) + self.bfc)

        # output(Q) layer
        # Matrix (1, 512) * (512, ACTIONS) -> (1, ACTIONS)
        self.output = tf.matmul(fully_connected, self.wto) + self.bto

    def init_nn(self):
    	# initialize 
        self.action = tf.placeholder("float", [None, self.actions])
       	# real reward
        self.y = tf.placeholder("float", [None]) 
        # evaluate the action using the network
        output_action = tf.reduce_sum(tf.multiply(self.output, self.action), reduction_indices = 1)
        # calculate cost
        self.cost = tf.reduce_mean(tf.square(self.y - output_action))
        # minimize cost
        elf.cost_minimizer = tf.train.AdamOptimizer(1e-6).minimize(self.cost)
        # initialize the saver
        self.saver = tf.train.Saver()
        self.session = tf.InteractiveSession()
        self.session.run(tf.initialize_all_variables())
        checkpoint = tf.train.get_checkpoint_state("saved")
        # restore network from saved files
        if checkpoint and checkpoint.model_checkpoint_path:
            self.saver.restore(self.session, checkpoint.model_checkpoint_path)
    
    def train(self):
    	# get the sample batch
        minibatch = random.sample(self.repmem, self.batchsize)
        sc_0_batch = [data[0] for data in minibatch]
        action_batch = [data[1] for data in minibatch]
        reward_batch = [data[2] for data in minibatch]
        sc_1_batch = [data[3] for data in minibatch]
        y_batch = []
        qval_batch = self.output.eval(feed_dict={self.input : sc_1_batch})
        for i in range(0,self.batchsize):
            done = minibatch[i][4]
            # process the reward
            if done:
                y_batch.append(reward_batch[i])
            else:
                y_batch.append(reward_batch[i] + self.discft * np.max(qval_batch[i]))

        # run the cost minimizer
        self.cost_minimizer.run(feed_dict={self.y : y_batch, self.action : action_batch, self.input : sc_0_batch})
        # save the trained network
        if self.epoch % 30000 == 0:
            self.saver.save(self.session, 'saved_snake_game', global_step = self.epoch)

    def add_replay(self, screen_1, action, reward, done):
    	# add a frame replay
    	# the last four frames are stored in screen_0
        tmp = np.append(self.screen_0[:,:,1:], screen_1, axis = 2)
        # add the renewed replay
        self.repmem.append((self.screen_0, action, reward, tmp, done))
        # maintain the size of the replay memory
        if len(self.repmem) > self.REPLAYMEM:
            self.repmem.popleft()
        # having enough observes
        if self.epoch > self.observe:
            self.train()
        # renew screen_0
        self.screen_0 = tmp
        self.epoch += 1
        return self.epoch, np.max(self.qval)

    def get_action(self):
    	# calculate the Q value
        Q_value = self.output.eval(feed_dict={self.input : [self.screen_0]})[0]
        self.qval = Q_value
        action = np.zeros(self.actions)
        idx = 0
        # make action
        if random.random() <= self.epsilon:
            idx = random.randrange(self.actions)
            action[idx] = 1
        else:
            idx = np.argmax(Q_value)
            action[idx] = 1
        if self.epsilon > self.final_epsilon and self.epoch > self.observe:
            self.epsilon -= (1 - self.final_epsilon) / 500000

        return action

    def init_state(self, state):
        self.screen_0 = np.stack((state, state, state, state), axis=2)

class agent:
    def screen_handle(self, screen):
    	# process the current frame
        procs_screen = cv2.cvtColor(cv2.resize(screen, (84, 84)), cv2.COLOR_BGR2GRAY)
        dummy, bin_screen = cv2.threshold(procs_screen, 1, 255, cv2.THRESH_BINARY)
        bin_screen = np.reshape(bin_screen, (84, 84, 1))
        cv2.imshow('image', bin_screen)
        return bin_screen
        
    def run(self):
    	# initialize
        dqn_agent = DQN(0.99, 0, 1, 0.001, 50000, 32, 4)
        g = game.gameState()
        action_0 = np.array([1, 0, 0, 0])
        screen_0, reward_0, is_dead_0 = g.frameStep(action_0)
        screen_0 = cv2.cvtColor(cv2.resize(screen_0, (84, 84)), cv2.COLOR_BGR2GRAY)
        _, screen_0 = cv2.threshold(screen_0, 1, 255, cv2.THRESH_BINARY)
        dqn_agent.init_state(screen_0)
        while True:
        	# get action and update the game status
            action = dqn_agent.get_action()
            screen_1, r, done = g.frameStep(action)
            screen_1 = self.screen_handle(screen_1)
            _, q_val = dqn_agent.add_replay(screen_1, action, r, done)
            if done == True:
                score, episode = g.ret_score()
                print(score, episode)

def main():
    run_agent = agent()
    run_agent.run()

if __name__ == '__main__':
    main()