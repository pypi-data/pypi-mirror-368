from django.utils.translation import gettext as _
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
                    link_text=_("CVE List"),
                    permissions=["netbox_cvexplorer.view_cve"],
                    buttons=(
                        PluginMenuButton(
                            link="plugins:netbox_cvexplorer:cve_add",
                            title=_("Add CVE Entry"),
                            icon_class="mdi mdi-plus-thick",
                            color=ButtonColorChoices.GREEN,
                            permissions=["netbox_cvexplorer.add_cve"],
                        ),
                    ),
                ),
            ),
        ),
    ),
)