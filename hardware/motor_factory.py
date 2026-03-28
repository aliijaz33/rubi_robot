from .visual_simulator import VisualMotorSimulator

class MotorFactory:
    @staticmethod
    def create_motor_controller(mode='simulation', debug_window=None):
        """Create appropriate motor controller"""
        if mode == 'simulation':
            return VisualMotorSimulator(debug_window)
        else:
            raise NotImplementedError("Real motor controller not available in simulation mode")