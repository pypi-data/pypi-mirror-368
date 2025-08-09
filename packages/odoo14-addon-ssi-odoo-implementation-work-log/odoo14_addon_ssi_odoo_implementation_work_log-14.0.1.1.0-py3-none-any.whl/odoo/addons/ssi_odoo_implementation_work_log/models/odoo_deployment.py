# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import models


class OdooDeployment(models.Model):
    _name = "odoo_deployment"
    _inherit = [
        "odoo_deployment",
        "mixin.work_object",
    ]

    _work_log_create_page = True
