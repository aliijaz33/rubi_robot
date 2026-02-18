from .visual_simulator import VisualMotorSimulator

class MotorFactory:
    @staticmethod
    def create_motor_controller(mode='simulation'):
        """Create appropriate motor controller"""
        if mode == 'simulation':
            return VisualMotorSimulator()
        else:
            raise NotImplementedError("Real motor controller not available in simulation mode")