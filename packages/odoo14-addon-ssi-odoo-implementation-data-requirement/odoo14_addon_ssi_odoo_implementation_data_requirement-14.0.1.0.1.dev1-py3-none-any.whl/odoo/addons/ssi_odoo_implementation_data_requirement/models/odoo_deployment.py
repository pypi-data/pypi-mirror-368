# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import models


class OdooDeployment(models.Model):
    _name = "odoo_deployment"
    _inherit = [
        "odoo_deployment",
        "mixin.data_requirement",
    ]

    _data_requirement_create_page = True
    _data_requirement_configurator_field_name = "type_id"
    _data_requirement_partner_field_name = "commercial_partner_id"
    _data_requirement_contact_field_name = "partner_id"
