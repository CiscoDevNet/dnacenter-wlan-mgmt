"""Sample usage
from dnacsdk.api import Api
from dnacsdk.wlan import Wlan

dnacp = Api(ip=DNAC_IP, username=DNAC_USERNAME, password=DNAC_PASSWORD)

wlans = Wlan.get_all(dnacp)
"""
import sys

class Wlan(object):

    @classmethod
    def get_all(cls, dnacp):
        wlans = \
        dnacp.get("/api/v1/commonsetting/wlan/-1")
        wlans = wlans["response"]
        validwlans=[]
        for wlan in wlans:
            if wlan["instanceType"] == "wlan":
                validwlans.append(Wlan(dnacp, wlan = wlan))

        return validwlans

    def __init__(self, dnacp, wlan = None):
        try:
            self.info = wlan
            self.ssid = self.info["value"][0]["ssid"]
            self.key = self.info["key"]
        except Exception as e:
            print("Parameters invalid")
            sys.exit()

    @classmethod
    def create(self, dnacp, create_params = None):
        body =[
        {
            "instanceType":"wlan",
            "namespace":"wlan",
            "type":"wlan.setting",
            "key":"wlan.info." + create_params["ssid"],
            "value":
                [
                    {
                        "ssid":create_params["ssid"],
                        "profileName":"",
                        "wlanType":"Enterprise",
                        "authType":"wpa2_enterprise",
                        "authServer":"auth_ise",
                        "authSecServer":"",
                        "redirectUrl":"",
                        "peerIp":"",
                        "isEnabled":True,
                        "isEmailReqd":False,
                        "isFabric":True,
                        "fabricId":None,
                        "isFastLaneEnabled":False,
                        "isMacFilteringEnabled":False,
                        "trafficType":"voicedata",
                        "radioPolicy":0,
                        "wlanBandSelectEnable":False,
                        "scalableGroupTag":"",
                        "passphrase":"",
                        "portalType":"",
                        "portalName":"",
                        "redirectUrlType":"",
                        "externalAuthIpAddress":"",
                        "isBroadcastSSID":True,
                        "fastTransition":"ADAPTIVE"
                    }
                ],
                "groupUuid":"-1"
            }
        ]

        creation=""
        try:
            creation = \
            dnacp.post("/api/v1/commonsetting/wlan/-1", \
            body)
        except Exception as e:
            creation = e
            print(e)

        return creation

    @classmethod
    def delete(self, dnacp, delete_params = None):

        try:
            deletion = \
            dnacp.delete("/api/v1/commonsetting/wlan/-1/" + delete_params["key"])
        except Exception as e:
            deletion = e
            print(e)


        return deletion

    @classmethod
    def task_status(cls, dnacp, taskId):
        api = "/api/v1/task{}".format(
            taskId
        )
        return dnacp.get(api)


        return creation
