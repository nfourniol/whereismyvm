from allvm.services.hypervisorServiceInterface import HypervisorServiceInterface
from allvm.dto.hypervisorDto import HypervisorData
from allvm.dto.hypervisorDto import VirtualMachineData
from allvm.dto.hypervisorDto import HostData
from allvm.dto.hypervisorDto import HypervisorConnection
from allvm.enum.PowerState import PowerState


from abc import ABCMeta
import ssl
import atexit
from pyVim import connect
from pyVmomi import vmodl, vim




# Service Layer
class ESXiService(HypervisorServiceInterface):

    #
    # TODO : https://github.com/rg3915/django-boilerplate
    #

    MAX_DEPTH=10

    class ESXiConnectionDto:
        """Just a class to transport esxi connection data
        """
        # parameterized constructor
        def __init__(self, hostContainerView, containerView, listVmView, version):
            self.hostContainerView = hostContainerView
            self.containerView = containerView
            self.hostView = hostContainerView.view[0]
            self.listVmView = listVmView
            self.version = version

    def print_vminfo(vm, depth=1):
        """
        Print information for a particular virtual machine or recurse into a folder
        with depth protection
        """

        # if this is a group it will have children. if it does, recurse into them
        # and then return
        if hasattr(vm, 'childEntity'):
            if depth > ESXiService.MAX_DEPTH:
                return
            vmlist = vm.childEntity
            for child in vmlist:
                ESXiService.print_vminfo(child, depth+1)
            return

        summary = vm.summary
        print(summary.config.name)



    # Method 2
    def print_vm_info(virtual_machine):
        """
        Print information for a particular virtual machine or recurse into a
        folder with depth protection
        """
        summary = virtual_machine.summary
        print("Name       : ", summary.config.name)
        print("Template   : ", summary.config.template)
        print("Path       : ", summary.config.vmPathName)
        print("Guest      : ", summary.config.guestFullName)
        print("Instance UUID : ", summary.config.instanceUuid)
        print("Bios UUID     : ", summary.config.uuid)
        annotation = summary.config.annotation
        if annotation:
            print("Annotation : ", annotation)
        print("State      : ", summary.runtime.powerState)
        if summary.guest is not None:
            ip_address = summary.guest.ipAddress
            tools_version = summary.guest.toolsStatus
            if tools_version is not None:
                print("VMware-tools: ", tools_version)
            else:
                print("Vmware-tools: None")
            if ip_address:
                print("IP         : ", ip_address)
            else:
                print("IP         : None")
        if summary.runtime.question is not None:
            print("Question  : ", summary.runtime.question.text)
        print("")


    def getHostData(hostView) -> HostData:

        summary = hostView.summary

        # Evaluation de la capacité disque totale de l'host esx
        diskCapacity = 0
        host_file_sys_vol_mount_info = hostView.configManager.storageSystem.fileSystemVolumeInfo.mountInfo
        for volMountInfo in host_file_sys_vol_mount_info:
            if volMountInfo.mountInfo.accessMode == 'readWrite':
                # Remarque : si accessMode = 'readOnly' cela signifie que le disque n'est pas inscriptible directement il fait partie d'un RAID
                # => c'est pour cela qu'on ne comptabilise que les disques 'readWrite'
                diskCapacity = diskCapacity + volMountInfo.volume.capacity

        hostData = HostData(
            hardMemorySizeMb=summary.hardware.memorySize / 1024 / 1024, 
            hardCpuCapabilityMhz=summary.hardware.numCpuCores * summary.hardware.cpuMhz, 
            diskCapacity=diskCapacity,
            ipAddress=summary.managementServerIp,
            overallMemoryUsageMb=summary.quickStats.overallMemoryUsage, # en Mb
            overallCpuUsageMhz=summary.quickStats.overallCpuUsage, 
            uptimeMin=int((summary.quickStats.uptime if summary.quickStats.uptime is not None else 0) / 60)) # uptime en minutes 


        return hostData


    def getVmData(virtualMachine) -> VirtualMachineData:

        summary = virtualMachine.summary
        vmData = VirtualMachineData(name=summary.config.name, powerState=PowerState.fromName(summary.runtime.powerState), overallStatus=summary.overallStatus,
        guestFullName=summary.config.guestFullName, memorySizeMb=summary.config.memorySizeMB, numCpu=summary.config.numCpu,
        ipAddress=summary.guest.ipAddress, toolsVersion=summary.guest.toolsStatus, 
        committedDiskSpace=summary.storage.committed, uncommittedDiskSpace=summary.storage.uncommitted)

        return vmData


    def connectToESXi(hypervisorConn: HypervisorConnection):
        # magic to disable SSL cert checking
        sslCtx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        sslCtx.verify_mode = ssl.CERT_NONE

        # another equivalent:
        #sslCtx = ssl._create_unverified_context()

        # let's get a connection
        try:
            svc_inst = connect.SmartConnect(host=hypervisorConn.hostName,
                                                    user=hypervisorConn.login,
                                                    pwd=hypervisorConn.passwd,
                                                    port=int(443),
                                                    sslContext=sslCtx)
            # incantation to close if the application is exited (process exited)
            atexit.register(connect.Disconnect, svc_inst)
            # verify that the connection has worked.
            sid = svc_inst.content.sessionManager.currentSession.key
            assert sid is not None, "Connection to ESX failed"
        except vim.fault.InvalidLogin:
            return None
        except Exception as e:
            return None

        content = svc_inst.RetrieveContent()

        container = content.rootFolder  # starting point to look into
        viewType = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively
        containerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)

        viewType = [vim.HostSystem]
        recursive = True  # whether we should look into it recursively
        hostContainerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)

        listVmView = containerView.view

        esxiConnectionDto = ESXiService.ESXiConnectionDto(hostContainerView, containerView, listVmView, svc_inst.content.about.version)

        return esxiConnectionDto
    

    def disconnectFromESXi(esxiConnectionDto: ESXiConnectionDto):
        # Disconnect from ESXi
        connect.Disconnect
        # Clean view
        #esxiConnectionDto.containerView.Destroy()
        #esxiConnectionDto.hostContainerView.Destroy()


    def getHypervisorData(self, hypervisorConn: HypervisorConnection)  -> HypervisorData:
        esxiConnectionDto = ESXiService.connectToESXi(hypervisorConn)
        vmDataList: list[VirtualMachineData] = []
        hostData: HostData = None
        countVMPowOn = 0
        countVMPowOff = 0
        allocatedRAMGb = 0 # RAM already allocated
        allocatedDiskSpaceGb = 0
        
        if esxiConnectionDto is not None:
            # # Firstly get data from host view
            hostData = ESXiService.getHostData(esxiConnectionDto.hostView)
            hostData.version = esxiConnectionDto.version

            # Secondly get data from each vm view
            # listVmView is None when there was a connection error (for instance bad identifiers)
            for vmView in esxiConnectionDto.listVmView:
                vmData: VirtualMachineData = ESXiService.getVmData(vmView)
                vmDataList.append(vmData)
                allocatedDiskSpaceGb = allocatedDiskSpaceGb + vmData.getAllocatedDiskSpaceGb()
                if vmData.powerState.name == PowerState.poweredOn.name:
                    countVMPowOn = countVMPowOn + 1
                    allocatedRAMGb = allocatedRAMGb + vmData.getMemorySizeGb()
                elif vmData.powerState.name == PowerState.poweredOff.name:
                    countVMPowOff = countVMPowOff + 1
                    
        else:
            f"Impossible to connect to {hypervisorConn.hostName}"

        ESXiService.disconnectFromESXi(esxiConnectionDto)
        
        return HypervisorData(hostName=hypervisorConn.hostName, hostData=hostData, vmDataList=vmDataList, countVMPoweredOn=countVMPowOn, 
                        countVMPoweredOff=countVMPowOff, allocatedRAMGb=allocatedRAMGb, allocatedDiskSpaceGb=allocatedDiskSpaceGb)


