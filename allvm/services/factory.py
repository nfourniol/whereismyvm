#from allvm.services.esxi import ESXiService

# TODO: delete this file

class HypervisorServiceFactory:

    @staticmethod
    def getHypervisorService(type: str):
        
        if type.lower() == "esxi":
            #return ESXiService()
            f"TODO return ESXiService"
        elif type.lower() == "proxmox":
            f"TODO implement proxmox service"
        else:
            raise NotImplementedError
        


