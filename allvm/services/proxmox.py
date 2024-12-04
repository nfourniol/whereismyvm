from allvm.services.hypervisorServiceInterface import HypervisorServiceInterface
from allvm.dto.hypervisorDto import HypervisorData, VirtualMachineData, HostData, HypervisorConnection
from allvm.enum.PowerState import PowerState
from allvm.enum.ProxmoxOS import ProxmoxOS
from proxmoxer import ProxmoxAPI # https://proxmoxer.github.io/docs/2.0/
from abc import ABCMeta



# Service Layer
class ProxmoxService(HypervisorServiceInterface):

    class ProxmoxConnectionDto:
        """Class to hold proxmox connection data"""
        def __init__(self, proxmox, nodeName):
            self.proxmox = proxmox
            self.nodeName = nodeName

    @staticmethod
    def connectToProxmox(hypervisorConn: HypervisorConnection):
        """Establish connection to Proxmox API"""
        try:
            proxmox = ProxmoxAPI(hypervisorConn.hostName, user=hypervisorConn.login, password=hypervisorConn.passwd, verify_ssl=False)
            
            if hypervisorConn.nodeName is None:
                # if nodeName is not provided we take the first node name found
                nodeName = proxmox.nodes.get()[0]["node"]
            else:
                nodeName = hypervisorConn.nodeName

            return ProxmoxService.ProxmoxConnectionDto(proxmox, nodeName)
        except Exception as e:
            print(f"Connection to Proxmox failed: {e}")
            return None

    @staticmethod
    def disconnectFromProxmox(proxmoxConnectionDto: ProxmoxConnectionDto):
        """Disconnect from Proxmox (no specific disconnect method in proxmoxer)"""
        # proxmoxer does not require explicit disconnection, so this is a placeholder
        pass

    @staticmethod
    def getHostData(proxmoxConnectionDto: ProxmoxConnectionDto) -> HostData:
        """Retrieve host data for Proxmox node"""
        nodeInfo = proxmoxConnectionDto.proxmox.nodes(proxmoxConnectionDto.nodeName).status.get()
        networkInfo = proxmoxConnectionDto.proxmox.nodes(proxmoxConnectionDto.nodeName).network.get()

        # Récupérer l'IP de la carte réseau principale (souvent `vmbr0`)
        mainIp = None
        for interface in networkInfo:
            if interface.get("iface") == "vmbr0" and "address" in interface:
                mainIp = interface["address"]
                break

        hostData = HostData(
            hardMemorySizeMb=nodeInfo["memory"]["total"] / 1024 / 1024,
            hardCpuCapabilityMhz=float(nodeInfo.get("cpuinfo", {}).get("mhz")),
            diskCapacity=nodeInfo["rootfs"]["total"],
            ipAddress=mainIp,
            overallMemoryUsageMb=nodeInfo["memory"]["used"] / 1024 / 1024,
            overallCpuUsageMhz=nodeInfo.get("cpu", 0) * float(nodeInfo.get("cpuinfo", {}).get("mhz")),
            uptimeMin=int(nodeInfo["uptime"] / 60),
            version=proxmoxConnectionDto.proxmox.version.get()["version"]
        )
        
        return hostData

    @staticmethod
    def getVmData(proxmoxConnectionDto: ProxmoxConnectionDto, vm_id: str) -> VirtualMachineData:
        """Retrieve VM data for a specific VM in Proxmox"""
        vm_info = proxmoxConnectionDto.proxmox.nodes(proxmoxConnectionDto.nodeName).qemu(vm_id).status.current.get()
        vm_config = proxmoxConnectionDto.proxmox.nodes(proxmoxConnectionDto.nodeName).qemu(vm_id).config.get()

        qemuAgent = False
        try:
            # Get network information via guest agent
            network_info = proxmoxConnectionDto.proxmox.nodes(proxmoxConnectionDto.nodeName).qemu(vm_id).agent("network-get-interfaces").get()
            qemuAgent = True # if network-get-interfaces is available then we know that Quemu agent is active and well configured

             # Array to store all ip address
            all_ips = []

            # Browse interfaces to find IP addresses
            for interface in network_info.get("result", []):
                if interface.get("name") != "virbr0" and interface.get("name") != "lo":
                    for ip in interface.get("ip-addresses", []):
                        if ip["ip-address-type"] == "ipv4":
                            all_ips.append(ip["ip-address"])

            # Convert all IPs to a character string
            all_ips_str = ", ".join(all_ips)

        except Exception as e:
            # Error handling if the Guest Agent is not available or if the API returns an error
            main_ip = "No IP (verify Qemu agent installed)"
            all_ips = []
            all_ips_str = "No IPs"
            print(f"Error retrieving IP addresses: {e}")



        committedDiskSpace = 0
        # Iteration on each defined disk inside the vm configuration
        for key, value in vm_config.items():
            if key.startswith(("scsi", "ide", "sata", "virtio")):
                # Recovers storage and volume from disk configuration
                disk_details = value.split(",")
                disk_path = disk_details[0]  # Disk path (par ex., "local:vm-100-disk-0")
                storage, volume = disk_path.split(":") if ":" in disk_path else (None, None)

                # Checks whether a storage device has been defined
                if storage and volume:
                    # Queries the API to obtain the size of the disk on this storage device
                    storage_info = proxmoxConnectionDto.proxmox.nodes(proxmoxConnectionDto.nodeName).storage(storage).content.get()
                    
                    # Find the corresponding volume and extract its size
                    for item in storage_info:
                        if item["volid"] == disk_path:
                            disk_size = item.get("size", 0)
                            committedDiskSpace += disk_size
  



        vmData = VirtualMachineData(
            name=vm_config["name"],
            powerState=PowerState.poweredOn if vm_info["status"] == "running" else PowerState.poweredOff,
            overallStatus="green" if vm_info["status"] == "running" else "red",
            guestFullName=ProxmoxOS.fromKey(vm_config.get("ostype", "Unknown OS")).osName,
            memorySizeMb=int(vm_config["memory"]),
            numCpu=int(vm_config["cores"]),
            ipAddress=all_ips_str,
            toolsVersion="Active" if qemuAgent else "Inactive or bad configuration",
            committedDiskSpace=committedDiskSpace,
            uncommittedDiskSpace=0  # Proxmox does not always track uncommitted space
        )

        return vmData

    def getHypervisorData(self, hypervisorConn: HypervisorConnection) -> HypervisorData:
        """Retrieve data for the hypervisor and its VMs in Proxmox"""
        proxmoxConnectionDto = ProxmoxService.connectToProxmox(hypervisorConn)
        vmDataList = []
        hostData = None
        countVMPowOn = 0
        countVMPowOff = 0
        allocatedRAMGb = 0
        allocatedDiskSpaceGb = 0
        
        if proxmoxConnectionDto:
            # Collect host data
            hostData = ProxmoxService.getHostData(proxmoxConnectionDto)

            # Collect VM data
            vms = proxmoxConnectionDto.proxmox.nodes(proxmoxConnectionDto.nodeName).qemu.get()
            for vm in vms:
                vmData = ProxmoxService.getVmData(proxmoxConnectionDto, vm["vmid"])
                vmDataList.append(vmData)
                allocatedDiskSpaceGb += vmData.committedDiskSpace / (1024 ** 3)  # Convert to GB

                if vmData.powerState == PowerState.poweredOn:
                    countVMPowOn += 1
                    allocatedRAMGb += vmData.memorySizeMb / 1024  # Convert to GB
                elif vmData.powerState == PowerState.poweredOff:
                    countVMPowOff += 1
        else:
            print(f"Impossible to connect to {hypervisorConn.hostName}")

        ProxmoxService.disconnectFromProxmox(proxmoxConnectionDto)

        return HypervisorData(
            hostType=hypervisorConn.type.lower, 
            hostName=hypervisorConn.hostName,
            nodeName=hypervisorConn.nodeName,
            hostData=hostData,
            vmDataList=vmDataList,
            countVMPoweredOn=countVMPowOn,
            countVMPoweredOff=countVMPowOff,
            allocatedRAMGb=allocatedRAMGb,
            allocatedDiskSpaceGb=allocatedDiskSpaceGb
        )
