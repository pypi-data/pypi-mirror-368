# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrCareerTransitionType(models.Model):
    _name = "employee_career_transition_type"
    _description = "Employee Career Transition Type"
    _inherit = ["mixin.master_data"]

    name = fields.Char(
        string="Career Transition Type",
    )
    require_reason = fields.Boolean(
        string="Require Reason",
    )
    reason_ids = fields.One2many(
        comodel_name="employee_career_transition_type.reason",
        inverse_name="type_id",
        string="Reasons",
    )
    limit = fields.Integer(
        string="Transition Limit",
        default=0,
    )
    change_company = fields.Boolean(
        string="Change Company",
    )
    require_company = fields.Boolean(
        string="Require Company",
    )
    change_parent = fields.Boolean(
        string="Change Manager",
    )
    require_parent = fields.Boolean(
        string="Require Manager",
    )
    change_job = fields.Boolean(
        string="Change Job Position",
    )
    require_job = fields.Boolean(
        string="Require Job Position",
    )
    change_department = fields.Boolean(
        string="Change Department",
    )
    require_department = fields.Boolean(
        string="Require Department",
    )
    change_employment_status = fields.Boolean(
        string="Change Employee Status",
    )
    require_employment_status = fields.Boolean(
        string="Require Employee Status",
    )

    allowed_employment_status_ids = fields.Many2many(
        string="Allowed Employment Status",
        comodel_name="hr.employment_status",
        relation="rel_transition_type_2_employment_status",
        column1="type_id",
        column2="employment_status_id",
    )
    default_employment_status_id = fields.Many2one(
        string="Default Employment Status",
        comodel_name="hr.employment_status",
    )
