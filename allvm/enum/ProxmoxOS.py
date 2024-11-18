from enum import Enum

class ProxmoxOS(Enum):
    L26 = ("l26", "Linux (generic)", "Used for generic Linux distributions (Ubuntu, Debian, CentOS, etc.)")
    WIN7 = ("win7", "Windows 7", "Windows 7 (specific edition unspecified)")
    WIN8 = ("win8", "Windows 8", "Windows 8 (specific edition unspecified)")
    WIN10 = ("win10", "Windows 10", "Windows 10 (specific edition unspecified)")
    WIN11 = ("win11", "Windows 11", "Windows 11 (specific edition unspecified)")
    WIN2K = ("win2k", "Windows 2000", "Windows 2000")
    WIN2K3 = ("win2k3", "Windows Server 2003", "Windows Server 2003")
    WIN2K8 = ("win2k8", "Windows Server 2008", "Windows Server 2008")
    WIN2K8R2 = ("win2k8r2", "Windows Server 2008 R2", "Windows Server 2008 R2")
    WIN2012 = ("win2012", "Windows Server 2012", "Windows Server 2012")
    WIN2016 = ("win2016", "Windows Server 2016", "Windows Server 2016")
    WIN2019 = ("win2019", "Windows Server 2019", "Windows Server 2019")
    WIN2022 = ("win2022", "Windows Server 2022", "Windows Server 2022")
    OTHER = ("other", "Other", "For unspecified or unknown OS types")
    SOLARIS = ("solaris", "Solaris", "Used for Solaris OS")
    DARWIN = ("darwin", "macOS (generic)", "Used for macOS systems")
    FREEBSD = ("freebsd", "FreeBSD", "Used for FreeBSD")
    NETBSD = ("netbsd", "NetBSD", "Used for NetBSD")
    OPENBSD = ("openbsd", "OpenBSD", "Used for OpenBSD")

    def __init__(self, osKey, osName, description):
        self.osKey = osKey
        self.osName = osName
        self.description = description

    @classmethod
    def fromKey(cls, key):
        """Return the OS corresponding to the given key, or None if not found."""
        for osType in cls:
            if osType.osKey == key:
                return osType
        return None

    def __str__(self):
        return f"{self.name} - {self.description}"
