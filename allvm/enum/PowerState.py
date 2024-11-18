import enum
# Using enum class create enumerations
class PowerState(enum.Enum):
    poweredOff = 0	#The virtual machine is currently powered off.
    poweredOn = 1	#The virtual machine is currently powered on.
    suspended = 2	#The virtual machine is currently suspended.

    @classmethod
    def fromName(cls, name):
        for state in PowerState:
            if state.name == name:
                return state
        raise ValueError('{} is not a valid state name'.format(name))
