# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import models


class SlideChannel(models.Model):
    _name = "slide.channel"
    _inherit = [
        "slide.channel",
        "mixin.work_object",
    ]

    _work_log_create_page = True
