"""Sample usage
from dnacsdk.api import Api
from dnacsdk.wireless_vlan import Wireless_VLAN

wireless_vlanId = 87
interfaceName = "Wireless API Test"

dnacp = Api(ip=DNAC_IP, username=DNAC_USERNAME, password=DNAC_PASSWORD)

wireless_vlans = Wireless_VLAN.get_all(dnacp)

create_params = {
                    "interfaceName": interfaceName
                    "vlanId" : wireless_vlanId
                }

creation = Wireless_VLAN.create(dnacp, create_params)
"""
import sys

class Wireless_VLAN(object):

    @classmethod
    def get_all(cls, dnacp):
        wireless_vlans = \
        dnacp.get("/api/v1/commonsetting/global/-1?key=interface.info")
        wireless_vlans = wireless_vlans["response"][0]["value"]
        wireless_vlans = [Wireless_VLAN(dnacp, wireless_vlan = \
        wireless_vlan) for wireless_vlan in wireless_vlans]
        return wireless_vlans

    def __init__(self, dnacp, wireless_vlan = None):
        try:
            self.info = wireless_vlan
            self.vlanId = self.info["vlanId"]
            self.interfaceName = self.info["interfaceName"]
        except Exception as e:
            print("Parameters invalid")
            sys.exit()


    @classmethod
    def create(self, dnacp, create_params = None):
        new_vlan = Wireless_VLAN(dnacp, wireless_vlan = create_params)

        wireless_vlans = self.get_all(dnacp)
        wireless_vlans.append(new_vlan)
        value = []

        for wireless_vlan in wireless_vlans:
            value.append({"interfaceName":wireless_vlan.interfaceName, \
            "vlanId":wireless_vlan.vlanId})


        body = [
                    {
                        "instanceType":"interface",
                        "namespace":"global",
                        "type":"interface.setting",
                        "key":"interface.info",
                        "value":value,
                        "groupUuid":"-1",
                        "inheritedGroupUuid":"",
                        "inheritedGroupName":""
                    }
                ]

        creation = ""
        try:
            creation = \
            dnacp.post("/api/v1/commonsetting/global/-1?key=interface.info", \
            body)
        except Exception as e:
            creation = e
            print(e)


        return creation

    @classmethod
    def delete(self, dnacp, delete_params = None):
        wireless_vlans = self.get_all(dnacp)
        value = []

        for wireless_vlan in wireless_vlans:
            if str(wireless_vlan.vlanId) != delete_params["vlanId"]:
                value.append({"interfaceName":wireless_vlan.interfaceName, \
                "vlanId":wireless_vlan.vlanId})


        body = [
                    {
                        "instanceType":"interface",
                        "namespace":"global",
                        "type":"interface.setting",
                        "key":"interface.info",
                        "value":value,
                        "groupUuid":"-1",
                        "inheritedGroupUuid":"",
                        "inheritedGroupName":""
                    }
                ]

        try:
            deletion = \
            dnacp.post("/api/v1/commonsetting/global/-1?key=interface.info", \
            body)
        except Exception as e:
            print(e)


        return deletion

    @classmethod
    def task_status(cls, dnacp, taskId):
        api = "/api/v1/task{}".format(
            taskId
        )
        return dnacp.get(api)
