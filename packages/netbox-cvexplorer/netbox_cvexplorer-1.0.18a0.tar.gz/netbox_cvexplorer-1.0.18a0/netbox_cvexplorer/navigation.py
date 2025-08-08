from netbox.choices import ButtonColorChoices
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

menu = PluginMenu(
    label="CVExplorer",
    icon_class="mdi mdi-security",
    groups=(
        (
            "",
            (
                PluginMenuItem(
                    link="plugins:netbox_cvexplorer:cve_list",
                    link_text="CVE Liste",
                    permissions=["netbox_cvexplorer.view_cve"],
                    buttons=(
                        PluginMenuButton(
                            link="plugins:netbox_cvexplorer:cve_add",
                            title="Neues CVE",
                            icon_class="mdi mdi-plus-thick",
                            color="success",
                            permissions=["netbox_cvexplorer.add_cve"],
                        ),
                    ),
                ),
            ),
        ),
    ),
)