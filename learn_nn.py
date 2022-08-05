from nn.movement_nn import MovementNN
from nn.position_nn import PositionNN
from utils.read_robot_data import read_robot_data
from utils.read_movement_nn_learning_data import read_movement_nn_learning_data
from utils.read_position_nn_learning_data import read_position_nn_learning_data


robots_filename = 'D:\\Uloziste\\Skola\\DP\\Algorithm\\_test_inputs\\robots_01.txt'
movements_filename = 'D:\\Uloziste\\Skola\\DP\\Algorithm\\_test_inputs\\movements_01.txt'
positions_filename = 'D:\\Uloziste\\Skola\\DP\\Algorithm\\_test_inputs\\positions_01.txt'
movement_nn_filename = 'D:\\Uloziste\\Skola\\DP\\Algorithm\\_test_inputs\\movement_nn_01.txt'
position_nn_filename = 'D:\\Uloziste\\Skola\\DP\\Algorithm\\_test_inputs\\position_nn_01.txt'

# reads data
robots = read_robot_data(robots_filename)
movements_data = read_movement_nn_learning_data(movements_filename, robots)
positions_data = read_position_nn_learning_data(positions_filename, robots)

# print('Robots:')
# print(robots)
# print('Movements data:')
# print(movements_data)
# print('Positions data:')
# print(positions_data)

# learns and saves Movement NN
movement_nn = MovementNN()
movement_nn.learn(movements_data)
movement_nn_file = open(movement_nn_filename, "w")
movement_nn_file.write(movement_nn.get_nn())

# learns and saves Position NN
position_nn = PositionNN()
position_nn.learn(positions_data)
position_nn_file = open(position_nn_filename, "w")
position_nn_file.write(position_nn.get_nn())
