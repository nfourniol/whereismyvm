from dataclasses import dataclass
from dataclasses import field
import enum
import string
from typing import List

@dataclass
class HypervisorConnection:
    """Detail of a hypervisor connection, attributes are read from the configuration file.
    """
     
    # parameterized constructor
    def __init__(self, hostName: str, type: str, login: str, passwd: str):
        self.hostName = hostName
        self.type = type
        self.login = login
        self.passwd = passwd


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



        


    
@dataclass
class VirtualMachineData:
    """All data about a virtual machine.
    """

    # parameterized constructor
    def __init__(self, name, powerState, overallStatus, guestFullName, memorySizeMb, numCpu, 
     ipAddress, toolsVersion, committedDiskSpace, uncommittedDiskSpace):
        self.name = name
        self.powerState = powerState
        self.overallStatus = overallStatus
        self.guestFullName = guestFullName
        self.memorySizeMb = memorySizeMb
        self.numCpu = numCpu
        self.ipAddress = ipAddress
        self.toolsVersion = toolsVersion
        self.committedDiskSpace = committedDiskSpace
        self.uncommittedDiskSpace = uncommittedDiskSpace

    def getMemorySizeGb(self) -> int:
        if self.memorySizeMb is not None:
            return int(self.memorySizeMb / 1024)
        else:
            return 0

    def getAllocatedDiskSpaceGb(self) -> int:
        return int((self.committedDiskSpace + self.uncommittedDiskSpace) / 1024 / 1024 / 1024)

    def getAllocatedDiskSpaceGbCorrectedBUG(self) -> int:
        return int((self.committedDiskSpace + self.uncommittedDiskSpace) / 1024 / 1024 / 1024) - self.getMemorySizeGb()


@dataclass
class HostData:
    """
    contains information about the hypervisor only
    """
    # An Hypervisor Host (different from a VM which is virtualized inside an Hypervisor host)

    # parameterized constructor
    def __init__(self, hardMemorySizeMb, hardCpuCapabilityMhz, diskCapacity, ipAddress, overallMemoryUsageMb, overallCpuUsageMhz, uptimeMin):
        self.hardMemorySizeMb = hardMemorySizeMb
        self.hardCpuCapabilityMhz = hardCpuCapabilityMhz
        self.diskCapacity = diskCapacity
        self.ipAddress = ipAddress
        self.overallMemoryUsageMb = overallMemoryUsageMb
        self.overallCpuUsageMhz = overallCpuUsageMhz
        self.uptimeMin = uptimeMin

    def getDiskCapacityGb(self) -> int:
        return int(self.diskCapacity / 1024 / 1024 / 1024)

    def getRamPercentageUsage(self) -> int:
        return int((self.overallMemoryUsageMb * 100) / self.hardMemorySizeMb)

    def getCpuPercentageUsage(self) -> int:
        return int((self.overallCpuUsageMhz * 100) / self.hardCpuCapabilityMhz)
        
    def getHardMemorySizeGb(self) -> int:
        return int(self.hardMemorySizeMb / 1024)

    def getHardCpuCapabilityGhzString(self) -> string:
        return "{:.2f}".format(self.hardCpuCapabilityMhz / 1000)

    def getOverallMemoryUsageGb(self) -> int:
        return int(self.overallMemoryUsageMb / 1024)

    def getOverallCpuUsageGhz(self) -> float:
        return float(self.overallCpuUsageMhz / 1000)

    def getOverallCpuUsageGhzString(self) -> string:
        return "{:.2f}".format(self.overallCpuUsageMhz / 1000)

    def getUptimeString(self) -> string:
        return str(self.uptimeMin // 1440) + "d " + str((self.uptimeMin % 1440) // 60) + "h " + str(self.uptimeMin % 60) + "min"



@dataclass
class HypervisorData:
    """Contains information about the hypervisor and its VMs.
    """

    hostData: HostData = field(default_factory=[HostData])
    #vmDataList: List[VirtualMachineData]
    vmDataList: List = field(default_factory=[VirtualMachineData])

    # parameterized constructor
    def __init__(self, hostName, hostData: HostData, vmDataList: List[VirtualMachineData], 
                countVMPoweredOn: int, countVMPoweredOff: int, allocatedRAMGb: int, allocatedDiskSpaceGb: int):
        self.hostName = hostName
        self.hostData = hostData
        self.vmDataList = vmDataList
        self.__countVMPoweredOn = countVMPoweredOn
        self.__countVMPoweredOff = countVMPoweredOff
        self.__allocatedRAMGb = allocatedRAMGb
        self.__allocatedDiskSpaceGb = allocatedDiskSpaceGb

    def getAvailableDiskGb(self) -> int:
        if self.hostData is not None:  # hostData can be none if there was an error during the esxi connection (for examle if the esxi is powered off)
            return self.hostData.getDiskCapacityGb() - self.__allocatedDiskSpaceGb
        else:
            return 0

    def getDiskPercentageUsage(self) -> int:
        if self.hostData is not None: # hostData can be none if there was an error during the esxi connection (for examle if the esxi is powered off)
            return int((self.__allocatedDiskSpaceGb * 100) / self.hostData.getDiskCapacityGb())
        else:
            return 0

    def getFreeDiskSpaceGb(self) -> int:
        if self.hostData is not None:  # hostData can be none if there was an error during the esxi connection (for example if the esxi is powered off)
            return int(self.hostData.getDiskCapacityGb() - self.__allocatedDiskSpaceGb)
        else:
            return 0

    # return total free RAM on the host = RAM available for VMs on the host
    def getAvailableRAMGb(self) -> int:
        if self.hostData is not None:
            return self.hostData.getHardMemorySizeGb() - self.__allocatedRAMGb
        else:
            return 0


    # return the total number of VMs
    def countVMTotal(self) -> int:
        return len(self.vmDataList)

    @property
    def countVMPoweredOn(self) -> int:
        return self.__countVMPoweredOn
    
    @countVMPoweredOn.setter
    def countVMPoweredOn(self, countVMPoweredOn):
        self.__countVMPoweredOn = countVMPoweredOn

    @property
    def countVMPoweredOff(self) -> int:
        return self.__countVMPoweredOff # __ denotes as a private attribute

    @countVMPoweredOff.setter
    def countVMPoweredOff(self, countVMPoweredOff):
        self.__countVMPoweredOff = countVMPoweredOff

    @property
    def allocatedRAMGb(self) -> int:
        return self.__allocatedRAMGb # __ denotes as a private attribute

    @allocatedRAMGb.setter
    def allocatedRAMGb(self, allocatedRAMGb):
        self.__allocatedRAMGb = allocatedRAMGb

    #def countVMPowerState(self, state: PowerState) -> int:
    #    count: int = 0
    #    for vm in self.vmDataList:
    #        if vm.powerState.name == state.name:
    #            count += 1
    #    
    #    return count

    #def countVMPowerOn(self) -> int:
    #    return self.countVMPowerState(PowerState.poweredOn)

    #def countVMPowerOff(self) -> int:
    #    return self.countVMPowerState(PowerState.poweredOff)


@dataclass
class HypervisorDataList:
    """Contains a list of all hypervisorData.
    """

    hypervisorDataList: List = field(default_factory=[HypervisorData])

    def __init__(self, hypervisorDataList: List[HypervisorData]):
        self.hypervisorDataList = hypervisorDataList

    def countVMTotal(self) -> int:
        count: int = 0
        for hypervisorData in self.hypervisorDataList:
            count = count + hypervisorData.countVMTotal()

        return count

    def countVMPoweredOnTotal(self) -> int:
        count: int = 0
        for hypervisorData in self.hypervisorDataList:
            count = count + hypervisorData.countVMPoweredOn

        return count

    def countVMPoweredOffTotal(self) -> int:
        count: int = 0
        for hypervisorData in self.hypervisorDataList:
            count = count + hypervisorData.countVMPoweredOff

        return count
