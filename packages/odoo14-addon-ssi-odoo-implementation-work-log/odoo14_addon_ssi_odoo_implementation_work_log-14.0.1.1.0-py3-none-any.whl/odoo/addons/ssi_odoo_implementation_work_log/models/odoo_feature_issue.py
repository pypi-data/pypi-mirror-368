# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import models


class OdooFeatureIssue(models.Model):
    _name = "odoo_feature_issue"
    _inherit = [
        "odoo_feature_issue",
        "mixin.work_object",
    ]

    _work_log_create_page = True
