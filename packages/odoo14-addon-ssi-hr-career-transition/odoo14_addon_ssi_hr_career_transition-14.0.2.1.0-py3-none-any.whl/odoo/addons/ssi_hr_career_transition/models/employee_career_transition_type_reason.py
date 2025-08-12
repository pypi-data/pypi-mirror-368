# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrCareerTransitionTypeReason(models.Model):
    _name = "employee_career_transition_type.reason"
    _description = "Employee Career Transition Type Reason"

    name = fields.Char(
        string="Reason",
        required=True,
    )
    type_id = fields.Many2one(
        comodel_name="employee_career_transition_type",
        string="Career Transition Type",
        required=True,
        ondelete="restrict",
    )
    limit = fields.Integer(
        string="Limit",
        required=True,
        default=0,
    )
    note = fields.Text(
        string="Description",
    )
