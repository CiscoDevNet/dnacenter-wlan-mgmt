"""Sample usage
from dnacsdk.api import Api
from dnacsdk.profile import Profile

dnacp = Api(ip=DNAC_IP, username=DNAC_USERNAME, password=DNAC_PASSWORD)

profiles = Profile.get_all(dnacp)
"""
import sys

class Profile(object):

    @classmethod
    def get_all(cls, dnacp):
        profiles = \
        dnacp.get("/api/v1/siteprofile")
        profiles = profiles["response"]
        profiles = [Profile(dnacp, profile = \
        profile) for profile in profiles]
        return profiles

    def __init__(self, dnacp, profile = None):
        try:
            self.info = profile
            self.name = self.info["name"]
            self.id = self.info["siteProfileUuid"]
            self.namespace = self.info["namespace"]
            self.sites = ""
            sites = dnacp.get("/api/v1/siteprofile/" + self.id + \
            "?includeSites=true")
            sites = sites["response"]
            if "sites" in sites.keys():
                sites = sites["sites"]
                for site in sites:
                    self.sites += "name: " + site["name"] + "\n" + \
                    "siteid: " + site["uuid"] + "\n\n"

        except Exception as e:
            print(e)
            print("Parameters invalid")
            sys.exit()

    @classmethod
    def create(self, dnacp, create_params = None):
        body ={
            "attributesList":[],
            "groupTypeList":[],
            "id":"",
            "interfaceList":[],
            "lastUpdatedBy":"",
            "lastUpdatedDatetime":0,
            "name":create_params["name"],
            "namespace":"wlan",
            "namingPrefix":"",
            "primaryDeviceType":"",
            "secondaryDeviceType":"",
            "profileAttributes":
            [
                {
                    "key":"wireless.ssid",
                    "value":create_params["name"],
                    "attribs":
                    [
                        {
                            "key":"wireless.fabric",
                            "value":False
                        },
                        {
                            "key":"wireless.flexConnect",
                            "value":False
                        },
                        {
                            "key":"wireless.authMode",
                            "value":"central"
                        },
                        {
                            "key":"wireless.trafficSwitchingMode",
                            "value":"fabric"
                        },
                        {
                            "key":"wireless.interfaceName",
                            "value":create_params["interfaceName"]
                        },
                        {
                            "key":"wireless.vlanId",
                            "value":create_params["vlanId"]
                        }
                    ]
                }
            ],
            "siteAssociationId":"",
            "siteProfileType":"",
            "siteProfileUuid":"",
            "status":"",
            "version":0
        }

        creation=""
        try:
            creation = \
            dnacp.post("/api/v1/siteprofile", \
            body)
        except Exception as e:
            creation = e
            print(e)

        return creation

    @classmethod
    def delete(self, dnacp, delete_params = None):

        try:
            deletion = \
            dnacp.delete("/api/v1/siteprofile/" + delete_params["id"])
        except Exception as e:
            deletion = e
            print(e)


        return deletion

    @classmethod
    def assign(self, dnacp, assign_params = None):
        try:
            assignment= \
            dnacp.post("/api/v1/siteprofile/" + assign_params["profileid"] + \
            "/site/" + assign_params["siteid"])
        except Exception as e:
            assignment = e
            print(e)


        return assignment

    @classmethod
    def unassign(self, dnacp, unassign_params = None):
        try:
            unassignment= \
            dnacp.delete("/api/v1/siteprofile/" + unassign_params["profileid"] + \
            "/site/" + unassign_params["siteid"])
        except Exception as e:
            unassignment = e
            print(e)


        return unassignment

    @classmethod
    def task_status(cls, dnacp, taskId):
        api = "/api/v1/task{}".format(
            taskId
        )
        return dnacp.get(api)


        return creation
