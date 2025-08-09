# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SlideChannel(models.Model):
    _inherit = "slide.channel"

    related_content_ids = fields.Many2many(
        comodel_name="slide.slide",
        domain=[("channel_id.channel_type", "=", "documentation")],
        string="Related Contents",
    )
    commercial_partner_id = fields.Many2one(
        string="Commercial Partner",
        comodel_name="res.partner",
    )
