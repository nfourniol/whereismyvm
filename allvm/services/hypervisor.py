from allvm.dto.hypervisorDto import HypervisorConnection
from allvm.dto.hypervisorDto import HypervisorDataList
from allvm.services.esxi import ESXiService
from allvm.services.proxmox import ProxmoxService
from allvm.services.hypervisorServiceInterface import HypervisorServiceInterface

import yaml
import os



class HypervisorService:

    BASE_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../..")
    )
    
    @staticmethod
    def getHypervisorConnections()  -> list[HypervisorConnection]:
        hypervisorConns = []
        with open(os.path.join(HypervisorService.BASE_DIR, "hypervisor.yaml"), 'r') as file:
            document = yaml.full_load(file)

            for item, connections in document.items():
                for connect in connections:
                    hypervisorConns.append(HypervisorConnection(hostName=connect.get('host'), type=connect.get('type'), login=connect.get('login'), passwd=connect.get('passwd')))
        
        return hypervisorConns

    @staticmethod
    def getHypervisorDataList() -> HypervisorDataList:
        hypervisorConns = HypervisorService.getHypervisorConnections()
        hypervisorDataList = []
        for hypervisorConn in hypervisorConns:
            hypervisorService: HypervisorServiceInterface = HypervisorServiceFactory.getHypervisorService(hypervisorConn.type)
            hypervisorDataList.append(hypervisorService.getHypervisorData(hypervisorConn))

        return HypervisorDataList(hypervisorDataList=hypervisorDataList)


class HypervisorServiceFactory:

    @staticmethod
    def getHypervisorService(type: str) -> HypervisorServiceInterface:
        
        if type.lower() == "esxi":
            return ESXiService()
        elif type.lower() == "proxmox":
            return ProxmoxService()
        else:
            raise NotImplementedError
        

