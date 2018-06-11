#! /usr/bin/env python
"""Command Line Interface Tool for Deploying Templates to DNA Center.


Copyright (c) 2018 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

import os
from dnacsdk.api import Api
import urllib3
import click
import tabulate

__author__ = "Hank Preston <hapresto@cisco.com>"
__extended__ = "Matthew DeNapoli <mdenapol@cisco.com>"
__copyright__ = "Copyright (c) 2018 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DNAC_IP = os.environ.get("DNAC_IP")
DNAC_USERNAME = os.environ.get("DNAC_USERNAME")
DNAC_PASSWORD = os.environ.get("DNAC_PASSWORD")

if DNAC_IP is None or DNAC_USERNAME is None or DNAC_PASSWORD is None:
    print("DNA Center details must be set via environment variables before running.")
    print("   export DNAC_IP=192.168.100.1")
    print("   export DNAC_USERNAME=admin")
    print("   export DNAC_PASSWORD=password")
    print("")
    exit("1")

dnacp = Api(ip=DNAC_IP, username=DNAC_USERNAME, password=DNAC_PASSWORD)

@click.group()
def cli():
    """Command line tool for deploying templates to DNA Center.
    """
    pass

@click.command()
def device_list():
    """Retrieve and return network devices list.

        Returns the hostname, management IP, and family of each device.

        Example command:

            ./wlanmgmt.py device_list

    """
    click.secho("Retrieving the devices.")

    from dnacsdk.networkDevice import NetworkDevice
    devices = NetworkDevice.get_all(dnacp)

    headers = ["Hostname", "Management IP", "Family","ID"]
    table = list()

    for device in devices:
        tr = [device.hostname, device.managementIpAddress, device.family, device.id]
        table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))

@click.command()
@click.argument("device")
def interface_list(device):
    """Retrieve the list of interfaces on a device.

        Returns the port name, status, description, and vlan information.

        Example command:

            ./wlanmgmt.py inteface_list switch1

    """
    click.secho("Retrieving the interfaces for {}.".format(device))

    from dnacsdk.networkDevice import NetworkDevice
    device = NetworkDevice(dnacp, hostname = device)

    headers = ["Port Name", "Status", "Description", "VLAN", "Voice VLAN"]
    table = list()

    for interface in device.interfaces.values():
        tr = [
                interface["portName"],
                "{}/{}".format(interface["adminStatus"], interface["status"]),
                interface["description"],
                interface["vlanId"],
                interface["voiceVlan"]
            ]
        table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))



@click.command()
def template_list():
    """Retrieve the deployment templates that are available.

        Returns the template name, parameters, content, and device types.

        Example command:

            ./wlanmgmt.py template_list
    """
    click.secho("Retrieving the templates available")

    from dnacsdk.templateProgrammer import Template
    templates = Template.get_all(dnacp)

    headers = ["Template Name", "Parameters", "Deploy Command", "Content", "Device Types"]
    table = list()

    for template in templates:
        tr = []
        tr.append(template.name)
        tr.append("\n".join(
                ["{}".format(param["parameterName"])
                    for param in template.info["templateParams"]
                ]
            )
        )
        cmd = "./wlanmgmt.py deploy \\\n --template {} \\\n --target {} ".format(
                template.name,
                "DEVICE"
            )
        params_cmd = " ".join(
            [
                '\\\n "{}=VALUE"'.format(param["parameterName"])
                for param in template.info["templateParams"]
            ]
        )
        cmd = cmd + params_cmd
        tr.append(cmd)
        tr.append(template.info["templateContent"])
        tr.append("\n".join(
            [type["productFamily"] for type in template.info["deviceTypes"]]
            )
        )
        table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))


@click.command()
@click.option("--template", help="Name of the template to deploy")
@click.option("--target", help="Hostname of target network device.")
@click.argument("parameters", nargs=-1)
def deploy(template, target, parameters):
    """Deploy a template with DNA Center.

        Provide all template parameters and their values as arguements in the format of: "PARAMTER=VALUE"

        You can find the list of parameters using:
          ./wlanmgmt.py template_list

        Example command:

          ./wlanmgmt.py deploy --template VLANSetup --target switch1 \\\n"VLANID=3001" "VLANNAME=Data"
    """
    click.secho("Attempting deployment.")

    from dnacsdk.networkDevice import NetworkDevice
    from dnacsdk.templateProgrammer import Template


    device = NetworkDevice(dnacp, hostname = target)
    template = Template(dnacp, name = template)

    deploy_params = dict([param.split("=", maxsplit=1) for param in parameters])

    # Deploy Template
    deployment = template.deploy(
                                    dnacp,
                                    target_device_ip = device.managementIpAddress,
                                    params = deploy_params
                                )

    print("Deployment Status: {}".format(
        Template.deployment_status(dnacp, deployment)["devices"][0]["status"])
    )


@click.command()
def wireless_vlan_list():
    """Retrieve and return wireless vlans list.

        Returns the interfaceName and vlanId of all configured VLANS.

        Example command:

            ./wlanmgmt.py wireless_vlan_list

    """
    click.secho("Retrieving the wireless vlans.")

    from dnacsdk.wireless_vlan import Wireless_VLAN
    wireless_vlans= Wireless_VLAN.get_all(dnacp)

    headers = ["Interface Name", "VLAN ID"]
    table = list()

    for wireless_vlan in wireless_vlans:
        tr = [wireless_vlan.interfaceName, wireless_vlan.vlanId]
        table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))

@click.command()
@click.argument("parameters", nargs=-1)
def create_wireless_vlan(parameters):
    """create a Wireless VLAN

        Provide all parameters and their values as arguements in the format of: "PARAMTER=VALUE"

        You can find the list of parameters using:
          ./wlanmgmt.py wireless_vlan_list

        Example command:

          ./wlanmgmt.py create_wireless_vlan "vlanId=87" "interfaceName=Wireless Test"
    """
    click.secho("Attempting wireless vlan creation.")

    from dnacsdk.wireless_vlan import Wireless_VLAN

    create_params = dict([param.split("=", maxsplit=1) for param in parameters])

    # Create VLAN
    creation = Wireless_VLAN.create(dnacp, create_params = create_params)

    print("Create Status: {}".format(creation))


@click.command()
@click.argument("parameters", nargs=-1)
def delete_wireless_vlan(parameters):
    """delete a Wireless VLAN

        Provide all parameters and their values as arguements in the format of: "PARAMTER=VALUE"

        You can find the list of parameters using:
          ./wlanmgmt.py wireless_vlan_list

        Example command:

          ./wlanmgmt.py delete_wireless_vlan "vlanId=87"
    """
    click.secho("Attempting wireless vlan deletion.")

    from dnacsdk.wireless_vlan import Wireless_VLAN

    delete_params = dict([param.split("=", maxsplit=1) for param in parameters])

    # Create VLAN
    deletion = Wireless_VLAN.delete(dnacp, delete_params = delete_params)

    print("Delete Status: {}".format(deletion))


@click.command()
def site_list():
    """Retrieve and return sites list.

        Returns the groupNameHierarchy, name, and id of all configured sites.

        Example command:

            ./wlanmgmt.py site_list

    """
    click.secho("Retrieving the sites.")

    from dnacsdk.site import Site
    sites= Site.get_all(dnacp)

    headers = ["groupNameHierarchy", "name", "id"]
    table = list()

    for site in sites:
        tr = [site.groupNameHierarchy, site.name, site.id]
        table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))


@click.command()
def profile_list():
    """Retrieve and return profiles list.

        Returns the interfaceName and vlanId of all configured VLANS.

        Example command:

            ./wlanmgmt.py profile_list

    """
    click.secho("Retrieving the profiles.")

    from dnacsdk.profile import Profile
    profiles= Profile.get_all(dnacp)

    headers = ["Name", "Namespace", "ID", "Assigned Sites"]
    table = list()

    for profile in profiles:
        tr = [profile.name, profile.namespace, profile.id, profile.sites]
        table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))

@click.command()
@click.argument("parameters", nargs=-1)
def create_profile(parameters):
    """create a Profile

        Provide all parameters and their values as arguements in the format of: "PARAMTER=VALUE"

        You can find the list of parameters using:
          ./wlanmgmt.py profile_list

        Example command:

          ./wlanmgmt.py create_profile "name=matt" vlanId=87" "interfaceName=Wireless Test"
    """
    click.secho("Attempting profile creation.")

    from dnacsdk.profile import Profile

    create_params = dict([param.split("=", maxsplit=1) for param in parameters])

    # Create VLAN
    creation = Profile.create(dnacp, create_params = create_params)

    print("Create Status: {}".format(creation))


@click.command()
@click.argument("parameters", nargs=-1)
def delete_profile(parameters):
    """delete a Profile

        Provide all parameters and their values as arguements in the format of: "PARAMTER=VALUE"

        You can find the list of parameters using:
          ./wlanmgmt.py profile_list

        Example command:

          ./wlanmgmt.py delete_profile "id=<profile id>"
    """
    click.secho("Attempting profile deletion.")

    from dnacsdk.profile import Profile

    delete_params = dict([param.split("=", maxsplit=1) for param in parameters])

    # Create VLAN
    deletion = Profile.delete(dnacp, delete_params = delete_params)

    print("Delete Status: {}".format(deletion))

@click.command()
@click.argument("parameters", nargs=-1)
def assign_profile_site(parameters):
    """Assign a site to a profile

        Provide all parameters and their values as arguements in the format of: "PARAMTER=VALUE"

        You can find the list of parameters using:
          ./wlanmgmt.py profile_list

        Example command:

          ./wlanmgmt.py assign_profile_site "profileid=<profileid>" "siteid=<siteid>"
    """
    click.secho("Attempting profile/site assignment.")

    from dnacsdk.profile import Profile

    assign_params = dict([param.split("=", maxsplit=1) for param in parameters])

    # Create VLAN
    assignment = Profile.assign(dnacp, assign_params = assign_params)

    print("Assignment Status: {}".format(assignment))

@click.command()
@click.argument("parameters", nargs=-1)
def unassign_profile_site(parameters):
    """Unassign a site to a profile

        Provide all parameters and their values as arguements in the format of: "PARAMTER=VALUE"

        You can find the list of parameters using:
          ./wlanmgmt.py profile_list

        Example command:

          ./wlanmgmt.py unassign_profile_site "profileid=<profileid>" "siteid=<siteid>"
    """
    click.secho("Attempting profile/site unassignment.")

    from dnacsdk.profile import Profile

    unassign_params = dict([param.split("=", maxsplit=1) for param in parameters])

    # Create VLAN
    unassignment = Profile.unassign(dnacp, unassign_params = unassign_params)

    print("Unassignment Status: {}".format(unassignment))

@click.command()
def wlan_list():
    """Retrieve and return wlans list.

        Returns the interfaceName and vlanId of all configured VLANS.

        Example command:

            ./wlanmgmt.py wlan_list

    """
    click.secho("Retrieving the wlans.")

    from dnacsdk.wlan import Wlan
    wlans= Wlan.get_all(dnacp)

    headers = ["SSID", "Key"]
    table = list()

    for wlan in wlans:
        tr = [wlan.ssid, wlan.key]
        table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))

@click.command()
@click.argument("parameters", nargs=-1)
def create_wlan(parameters):
    """create a wlan

        Provide all parameters and their values as arguements in the format of: "PARAMTER=VALUE"

        You can find the list of parameters using:
          ./wlanmgmt.py wlan_list

        Example command:

          ./wlanmgmt.py create_wlan "name=matt" vlanId=87" "interfaceName=Wireless Test"
    """
    click.secho("Attempting wlan creation.")

    from dnacsdk.wlan import Wlan


    create_params = dict([param.split("=", maxsplit=1) for param in parameters])

    # Create VLAN
    creation = Wlan.create(dnacp, create_params = create_params)

    print("Create Status: {}".format(creation))


@click.command()
@click.argument("parameters", nargs=-1)
def delete_wlan(parameters):
    """delete a wlan

        Provide all parameters and their values as arguements in the format of: "PARAMTER=VALUE"

        You can find the list of parameters using:
          ./wlanmgmt.py wlan_list

        Example command:

          ./wlanmgmt.py delete_wlan "id=<wlan id>"
    """
    click.secho("Attempting wlan deletion.")

    from dnacsdk.wlan import Wlan

    delete_params = dict([param.split("=", maxsplit=1) for param in parameters])

    # Create VLAN
    deletion = Wlan.delete(dnacp, delete_params = delete_params)

    print("Delete Status: {}".format(deletion))

@click.command()
@click.argument("parameters", nargs=-1)
def assign_device_site(parameters):
    """Assign a site to a device

        Provide all parameters and their values as arguements in the format of: "PARAMTER=VALUE"

        You can find the list of parameters using:
          ./wlanmgmt.py device_list

        Example command:

          ./wlanmgmt.py assign_device_site "deviceid=<deviceid>" "siteid=<siteid>"
    """
    click.secho("Attempting device/site assignment.")

    from dnacsdk.networkDevice import NetworkDevice

    assign_params = dict([param.split("=", maxsplit=1) for param in parameters])

    # Create VLAN
    assignment = NetworkDevice.assign(dnacp, assign_params = assign_params)

    print("Assignment Status: {}".format(assignment))

@click.command()
@click.argument("parameters", nargs=-1)
def unassign_device_site(parameters):
    """Unassign a site to a device

        Provide all parameters and their values as arguements in the format of: "PARAMTER=VALUE"

        You can find the list of parameters using:
          ./wlanmgmt.py device_list

        Example command:

          ./wlanmgmt.py unassign_device_site "deviceid=<deviceid>" "siteid=<siteid>"
    """
    click.secho("Attempting device/site unassignment.")

    from dnacsdk.networkDevice import NetworkDevice

    unassign_params = dict([param.split("=", maxsplit=1) for param in parameters])

    # Create VLAN
    unassignment = NetworkDevice.unassign(dnacp, unassign_params = unassign_params)

    print("Unassignment Status: {}".format(unassignment))

cli.add_command(deploy)
cli.add_command(device_list)
cli.add_command(interface_list)
cli.add_command(template_list)
cli.add_command(wireless_vlan_list)
cli.add_command(create_wireless_vlan)
cli.add_command(delete_wireless_vlan)
cli.add_command(site_list)
cli.add_command(profile_list)
cli.add_command(create_profile)
cli.add_command(delete_profile)
cli.add_command(wlan_list)
cli.add_command(create_wlan)
cli.add_command(delete_wlan)
cli.add_command(assign_profile_site)
cli.add_command(unassign_profile_site)
cli.add_command(assign_device_site)
cli.add_command(unassign_device_site)

if __name__ == '__main__':
    cli()
