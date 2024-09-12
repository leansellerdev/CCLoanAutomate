from openvpn_api.vpn import VPN
from openvpn_api.util.errors import ConnectError


class VPNConnect:
    def __init__(self) -> None:
        self.host = '185.97.113.229'
        self.port = 1194

        self.vpn = VPN(host=self.host, port=self.port)

    def connect(self) -> bool:
        try:
            status = self.vpn.connect()
        except ConnectError:
            raise ConnectError
        else:
            return status
