from .visual_simulator import VisualMotorSimulator

class MotorFactory:
    @staticmethod
    def create_motor_controller(mode='simulation', debug_window=None, root=None):
        """Create appropriate motor controller"""
        if mode == 'simulation':
            # Pass standalone=False to integrate with existing Tkinter app
            return VisualMotorSimulator(debug_window, standalone=False, root=root)
        else:
            raise NotImplementedError("Real motor controller not available in simulation mode")