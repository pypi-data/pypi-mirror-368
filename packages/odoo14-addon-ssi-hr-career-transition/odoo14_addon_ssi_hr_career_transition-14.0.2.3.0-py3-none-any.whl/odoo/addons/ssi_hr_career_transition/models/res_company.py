# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Company(models.Model):
    _name = "res.company"
    _inherit = ["res.company"]

    join_transition_type_id = fields.Many2one(
        string="Join Transition Type",
        comodel_name="employee_career_transition_type",
    )
    terminate_transition_type_id = fields.Many2one(
        comodel_name="employee_career_transition_type",
        string="Terminate Transition Type",
    )
    permanent_transition_type_id = fields.Many2one(
        comodel_name="employee_career_transition_type",
        string="Permanent Transition Type",
    )
    contract_transition_type_id = fields.Many2one(
        comodel_name="employee_career_transition_type",
        string="Contract Transition Type",
    )
