class Config:
    """Configuration settings"""
    MODE = 'simulation'  # Use simulation for Mac development
    
    @classmethod
    def get_mode(cls):
        return cls.MODE