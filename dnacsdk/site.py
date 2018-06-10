"""Sample usage
from dnacsdk.api import Api
from dnacsdk.site import Site

dnacp = Api(ip=DNAC_IP, username=DNAC_USERNAME, password=DNAC_PASSWORD)

sites = Site.get_all(dnacp)
"""
import sys

class Site(object):

    @classmethod
    def get_all(cls, dnacp):
        sites = \
        dnacp.get("/api/v1/group/?groupType=SITE")
        sites = sites["response"]
        sites = [Site(dnacp, site = \
        site) for site in sites]
        return sites

    def __init__(self, dnacp, site = None):
        try:
            self.info = site
            self.groupNameHierarchy = self.info["groupNameHierarchy"]
            self.name = self.info["name"]
            self.id = self.info["id"]
        except Exception as e:
            print("Parameters invalid")
            sys.exit()
