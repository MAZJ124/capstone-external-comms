from pynq import Overlay, allocate, DefaultIP
import numpy as np
import pandas as pd
from typing import List

class Driver(DefaultIP):
    def __init__(self, description):
        super().__init__(description=description)

        self.input = allocate(shape=(30,6), dtype=np.float32)
        self.register_map.input_data = self.input.physical_address

        self.output = allocate(shape=(7,), dtype=np.float32)
        self.register_map.output_prediction = self.output.physical_address

        self.action_types = ('BOMB', 'CPT', 'HULK', 'IRON_MAN', 'RELOAD', 'SHANG_CHI', 'SHIELD')

    bindto = ["xilinx.com:hls:myCNN:1.0"]

    def get_prediction(self, input_data: List[List[np.float32]]):
        input_data = pd.DataFrame(np.array(input_data)).apply(lambda col: (col-col.mean())/col.std(), axis=0).values
        self.input[:] = [x[:] for x in input_data]
        self.register_map.CTRL.AP_START=1
        while(self.register_map.CTRL.AP_DONE == 0):
            pass

        return self.output    

    def clear_buffer(self):
        self.register_map.CTRL.AP_START=1
        while(self.register_map.CTRL.AP_DONE == 0):
            pass
    
    def get_action(self, index: int):
        return self.action_types[index]
    
    def __del__(self):
        del self.input
        del self.output

def Model(path):
	return Overlay(path).myCNN_0



#Sample Code below on how to use the model

#Initialize the model
# model = Model(r'/home/xilinx/fpga_deployment/week8.bit')

# test_case = [
#         [ 1.45194718e+00, -6.15968296e-01,  8.72134691e-01,
#             7.34305300e-01, -7.67589348e-01, -8.96998862e-01],
#         [ 1.45194718e+00, -1.42716447e+00,  7.59236996e-01,
#             1.15187070e+00,  7.23870512e-01, -1.37709656e+00],
#         [ 1.25160589e+00, -1.05401423e+00,  1.52411888e-01,
#             1.06918449e+00,  9.96873762e-01, -1.37709656e+00],
#         [ 2.70987964e-01, -3.72609444e-01, -3.13291103e-01,
#             9.41020847e-01,  1.03193313e+00, -1.37709656e+00],
#         [-3.93301598e-01,  2.92571421e-01, -6.94320822e-01,
#             5.35858375e-01,  9.07788491e-01, -1.37709656e+00],
#         [-7.93984190e-01,  1.62780033e-01, -1.00478948e+00,
#             2.10281390e-01,  1.30321215e+00, -1.37709656e+00],
#         [-1.26847673e+00, -5.67296526e-01, -1.25880930e+00,
#             1.05373250e-01,  8.14105271e-01, -1.37709656e+00],
#         [-2.75522004e+00, -8.75551073e-01, -1.16002381e+00,
#             -1.58705861e-01,  4.22245027e-02, -1.11605218e+00],
#         [-1.91167774e+00, -7.78207532e-01, -7.22545246e-01,
#             6.16994227e-01,  1.30723535e+00,  1.03144021e+00],
#         [-1.62698221e+00, -4.86176908e-01, -1.59750238e+00,
#             4.92964900e-01, -4.99758792e-01,  1.40865983e+00],
#         [-9.94325487e-01,  7.79289126e-01, -1.68217565e+00,
#             3.63250894e-01, -1.06128337e+00,  1.40865983e+00],
#         [-6.04187173e-01,  1.63915707e+00, -1.79507334e+00,
#             -4.01596628e-01, -8.61847313e-01,  1.17071054e+00],
#         [ 3.86975030e-01,  1.49314176e+00, -1.42815584e+00,
#             -1.94472818e+00, -1.50326126e+00,  7.42051879e-01],
#         [ 7.87657623e-01,  9.09080515e-01,  1.38299676e-01,
#             -2.21862628e+00, -2.21421920e+00, -1.11766184e-01],
#         [ 1.13561882e+00,  5.35930274e-01,  1.98699943e+00,
#             -1.90596902e+00, -1.81707132e+00, -7.14687710e-01],
#         [ 1.86633734e-01,  5.40797451e-04,  1.46484759e+00,
#             -1.50339049e+00, -6.15857016e-01, -8.64455796e-01],
#         [-3.40580204e-01,  2.60123574e-01,  1.09793008e+00,
#             -7.51979479e-01, -3.24461968e-01, -2.20942920e-01],
#         [ 5.55683491e-01,  5.68378121e-01,  7.31012573e-01,
#             6.88311091e-01,  9.22157083e-01,  5.27897512e-01],
#         [ 1.55000898e-01, -1.13513385e+00,  9.85032386e-01,
#             1.15083713e+00,  8.99167336e-01,  1.40865983e+00],
#         [ 1.55000898e-01, -2.20591280e+00,  7.45124784e-01,
#             1.35031763e+00,  1.16929687e+00,  1.40865983e+00],
#         [ 5.76772048e-01, -2.38437596e+00,  7.59236996e-01,
#             1.24437591e+00, -1.82500278e-01,  1.40865983e+00],
#         [ 1.45194718e+00, -5.99744373e-01, -7.50769669e-01,
#             1.44488999e+00, -2.19180420e+00,  1.40865983e+00],
#         [ 1.01963176e+00,  9.73976209e-01, -7.50769669e-01,
#             2.08731023e-01,  2.84766337e-01,  1.60125879e-01],
#         [ 4.18607867e-01,  1.10376760e+00,  1.80636311e-01,
#             -2.95654910e-01,  1.91657861e-01, -3.58323646e-02],
#         [ 1.97178013e-01,  1.10376760e+00,  5.33441607e-01,
#             -1.53021183e-01, -2.06064769e-01, -1.10716408e-01],
#         [ 1.02279504e-01,  8.76632668e-01,  5.61666031e-01,
#             -2.43459235e-01,  5.37653558e-01, -6.66258029e-02],
#         [-2.66770253e-01,  7.14393432e-01,  5.75778243e-01,
#             -3.77307551e-01,  4.18106872e-01,  8.24424326e-02],
#         [-4.53403987e-02,  4.06138885e-01,  6.04002666e-01,
#             -5.30277056e-01, -1.38245014e-01,  1.25833187e-01],
#         [-2.35137416e-01,  3.08795344e-01,  6.32227090e-01,
#             -6.88414449e-01,  4.88225602e-01, -1.76362420e-02],
#         [-3.19491646e-01,  3.73691038e-01,  3.78207277e-01,
#             -1.13543682e+00,  3.45689168e-01,  1.25833187e-01]]

# print(f'Shape of input = {np.array(test_case).shape}')

# predictions = model.get_prediction(input_data=test_case)
# predictions = np.array(predictions)

# print(f'Shape of output = {np.array(predictions).shape}')
# print()
# print(f'Output = {predictions}')
# print()
# print(f'Highest Confidence = {np.max(predictions)}')
# print()
# print(f'Action Predicted = {model.get_action(np.argmax(predictions))}')

# model.clear_buffer()
