from pros_car_py.env import SERIAL_DEV_DEFAULT
from pros_car_py.car_models import TwoWheelAndServoState
import rclpy
from rclpy.node import Node
import orjson
from std_msgs.msg import String
from serial import Serial
from rclpy.duration import Duration

class CarAStatePublisher(Node):
    def __init__(self):
        super().__init__('car_a_state_publisher')

        serial_port = self.declare_parameter('serial_port', SERIAL_DEV_DEFAULT).value
        self._serial = Serial(serial_port, 115200, timeout=0)

        self.publisher = self.create_publisher(
            String,
            'carA_state',
            10
        )

        # Create a timer to read from the serial port and publish state every 100 ms
        self.timer = self.create_timer(0.01, self.timer_callback)
        self.log_interval = Duration(seconds=1)  # Log every 1 seconds


    def timer_callback(self):
        if self._serial.in_waiting:
            incoming_data = self._serial.readline()
            self.get_logger().info(f'Receive from car esp32: {incoming_data}')

            try:
                # Assuming the incoming data is already in the required JSON format
                
                state_msg = String()
                # validation should be customized
                state_data =TwoWheelAndServoState(**orjson.loads(incoming_data))
                state_msg.data = orjson.dumps({"type":"CarA_State","data":incoming_data.decode()}).decode()
                self.publisher.publish(state_msg)
            except orjson.JSONDecodeError as e:
                self.get_logger().error(f'JSON decode error: {e}')

def main(args=None):
    rclpy.init(args=args)
    car_a_state_publisher = CarAStatePublisher()
    rclpy.spin(car_a_state_publisher)
    car_a_state_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
