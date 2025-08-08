from .fonction import fonction


class CMD:
    clear= fonction.clear
    title= fonction.title

class system:
    iswin32= fonction.iswin32
    islinux= fonction.islinux
    isdarwin= fonction.isdarwin
    isadmin= fonction.isadmin
    runasadmin= fonction.runasadmin

class monitor:
    cpu_usage= fonction.cpu_usage
    ram_usage= fonction.ram_usage