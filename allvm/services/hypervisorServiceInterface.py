from allvm.dto.hypervisorDto import HypervisorConnection
from allvm.dto.hypervisorDto import HypervisorData
from abc import abstractmethod
from abc import ABCMeta

class HypervisorServiceInterface(metaclass=ABCMeta):
    """Formal interface to a hypervisor service.

    Raises:
        NotImplementedError: error raided when a method is not implemented in the concrete class.

    """
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'getHypervisorData') and 
                callable(subclass.getHypervisorData) or 
                NotImplemented)
    
    @abstractmethod
    def getHypervisorData(self, hypervisorConn: HypervisorConnection) -> HypervisorData:
        """Gather hypervisor data"""
        raise NotImplementedError