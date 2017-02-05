import tensorflow as tf

x = tf.placeholder(tf.uint16, shape=[None, 1])

hidden_units = 3

def inference(x):
    with tf.name_scope('hidden'):
        weights = tf.Variable(tf.truncated_normal([1, hidden_units], stddev=1.0),
                              name='weights')
        biases = tf.Variable(tf.zeros([hidden_units]),
                             name='biases')
        hidden = tf.nn.relu(tf.matmul(x, weights) + biases)
    with tf.name_scope('linear_regression'):
        weights = tf.Variable(tf.truncated_normal([hidden_units, 1], stddev=1.0),
                              name='weights')
        biases = tf.Variable(tf.zeros([1]),
                             name='biases')
        regression = tf.matmul(hidden, weights) + biases

    return regression

def loss(regression, groundtruth):
    loss = tf.reduce_mean(tf.square(groundtruth - regression), name='cost')

    return loss

def training(loss, learning_rate):
    tf.summary.scalar('loss', loss)
    optimizer = tf.train.GradientDescentOptimizer(learning_rate)
    global_step = tf.Variable(0, name='global_step', trainable=False)
    train_op = optimizer.minimize(loss, global_step=global_step)

    return train_op
