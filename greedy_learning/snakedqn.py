import cv2

# for tensor
import numpy as np
import tensorflow as tf
import random
from collections import deque

# Based on NIPS 2013
class DQN:
    def __init__(self, DISCFT, FLAG, INIT_EPSILON, FIN_EPSILON, REPLAY_MEMORY, BATCH_SIZE, ACTIONS):
        # Initialize Variables
        # epoch - frame
        # episode - one round
        self.epoch = 0
        self.episode = 0
        self.observe = 10000
        # discount factor
        self.discft = DISCFT
        # FLAG
        # 0 - train
        # 1 - play
        self.flag = FLAG
        self.epsilon = INIT_EPSILON
        self.finep = FIN_EPSILON
        self.REPLAYMEM = REPLAY_MEMORY
        self.batchsize = BATCH_SIZE
        self.actions = ACTIONS
        self.repmem = deque()
        # Init weight and bias
        self.w1 = tf.Variable(tf.truncated_normal([8, 8, 4, 32], stddev = 0.01))
        self.b1 = tf.Variable(tf.constant(0.01, shape = [32]))

        self.w2 = tf.Variable(tf.truncated_normal([4, 4, 32, 64], stddev=0.01))
        self.b2 = tf.Variable(tf.constant(0.01, shape = [64]))

        self.w3 = tf.Variable(tf.truncated_normal([3, 3, 64, 64], stddev = 0.01))
        self.b3 = tf.Variable(tf.constant(0.01, shape = [64]))

        self.wfc = tf.Variable(tf.truncated_normal([2304, 512], stddev = 0.01))
        self.bfc = tf.Variable(tf.constant(0.01, shape = [512]))

        self.wto = tf.Variable(tf.truncated_normal([512, self.actions], stddev = 0.01))
        self.bto = tf.Variable(tf.constant(0.01, shape = [self.actions]))

        self.initConvNet()
        self.initNN()
    
    def initConvNet(self):
        # input layer
        self.input = tf.placeholder("float", [None, 84, 84, 4])

        # Convolutional Neural Network
        # zero-padding
        # 84 x 84 x 4
        # 8 x 8 x 4 with 32 Filters
        # Stride 4 -> Output 21 x 21 x 32 -> max_pool 11 x 11 x 32
        tf.nn.conv2d(self.input, self.w1, strides = [1, 4, 4, 1], padding = "SAME")
        conv1 = tf.nn.relu(tf.nn.conv2d(self.input, self.w1, strides = [1, 4, 4, 1], padding = "SAME") + self.b1)
        pool = tf.nn.max_pool(conv1, ksize = [1, 2, 2, 1], strides = [1, 2, 2, 1], padding = "SAME")

        # 11 x 11 x 32
        # 4 x 4 x 32 with 64 Filters
        # Stride 2 -> Output 6 x 6 x 64
        conv2 = tf.nn.relu(tf.nn.conv2d(pool, self.w2, strides = [1, 2, 2, 1], padding = "SAME") + self.b2)

        # 6 x 6 x 64
        # 3 x 3 x 64 with 64 Filters
        # Stride 1 -> Output 6 x 6 x 64
        conv3 = tf.nn.relu(tf.nn.conv2d(conv2, self.w3, strides = [1, 1, 1, 1], padding = "SAME") + self.b3)

        # 6 x 6 x 64 = 2304
        conv3_to_reshaped = tf.reshape(conv3, [-1, 2304])

        # Matrix (1, 2304) * (2304, 512)
        fullyconnected = tf.nn.relu(tf.matmul(conv3_to_reshaped, self.wfc) + self.bfc)

        # output(Q) layer
        # Matrix (1, 512) * (512, ACTIONS) -> (1, ACTIONS)
        self.output = tf.matmul(fullyconnected, self.wto) + self.bto

    def initNN(self):
        self.a = tf.placeholder("float", [None, self.actions])
        self.y = tf.placeholder("float", [None]) 
        out_action = tf.reduce_sum(tf.multiply(self.output, self.a), reduction_indices = 1)
        self.cost = tf.reduce_mean(tf.square(self.y - out_action))
        self.optimize = tf.train.AdamOptimizer(1e-6).minimize(self.cost)
        #print("cost : ",self.cost)
        #print("optimize : ",self.optimize)
        self.saver = tf.train.Saver()
        self.session = tf.InteractiveSession()
        self.session.run(tf.initialize_all_variables())
        checkpoint = tf.train.get_checkpoint_state("saved")
        # For fresh start, comment below 2 lines
        if checkpoint and checkpoint.model_checkpoint_path:
            self.saver.restore(self.session, checkpoint.model_checkpoint_path)
    
    def train(self):
        # DQN
        minibatch = random.sample(self.repmem, self.batchsize)
        s_batch = [data[0] for data in minibatch]
        a_batch = [data[1] for data in minibatch]
        r_batch = [data[2] for data in minibatch]
        s_t1_batch = [data[3] for data in minibatch]

        y_batch = []
        Q_batch = self.output.eval(feed_dict={self.input : s_t1_batch})
        for i in range(0,self.batchsize):
            done = minibatch[i][4]
            if done:
                y_batch.append(r_batch[i])
            else:
                y_batch.append(r_batch[i] + self.discft * np.max(Q_batch[i]))

        feed_dict = {self.y : y_batch, self.a : a_batch, self.input : s_batch}
        print(len(y_batch), len(a_batch), len(s_batch))
        self.optimize.run(feed_dict)
        if self.epoch % 30000 == 0:
            self.saver.save(self.session, 'saved/' + 'snake.ckpt', global_step = self.epoch)

    def addReplay(self, s_t1, action, reward, done):
        tmp = np.append(self.s_t[:,:,1:], s_t1, axis = 2)
        acts = np.zeros(self.actions)
        acts[action] = 1
        self.repmem.append((self.s_t, acts, reward, tmp, done))
        if len(self.repmem) > self.REPLAYMEM:
            self.repmem.popleft()
        if self.epoch > self.observe and self.flag == 0:
            self.train()

        self.s_t = tmp
        self.epoch += 1
        
        return self.epoch, np.max(self.qv)
        
    def getAction(self):
        #print("s_t", self.s_t)
        Q_val = self.output.eval(feed_dict={self.input : [self.s_t]})[0]
        print("Q_value : " + str(Q_val) + " @epoch : " + str(self.episode) + "\n")
        # for print
        self.qv = Q_val
        direction = 0
        idx = 0

        # epsilon greedily
        if random.random() <= self.epsilon:
            idx = random.randrange(self.actions)
            direction = idx
        else:
            idx = int(np.argmax(Q_val))
            print(np.argmax(Q_val))
            direction = idx

        # change episilon
        if self.flag == 0 and self.epsilon > self.finep and self.epoch > self.observe:
            self.epsilon -= (1 - self.finep) / 500000

        return direction

    def initState(self, state):
        self.s_t = np.stack((state, state, state, state), axis=2)
        #print("state: ", len(state))
        #print("stack: ", len(self.s_t))


    

