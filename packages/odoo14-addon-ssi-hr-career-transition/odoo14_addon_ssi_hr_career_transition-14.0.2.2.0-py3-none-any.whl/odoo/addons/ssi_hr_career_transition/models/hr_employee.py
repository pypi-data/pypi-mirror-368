# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _name = "hr.employee"
    _inherit = ["hr.employee"]

    career_transition_ids = fields.One2many(
        comodel_name="employee_career_transition",
        inverse_name="employee_id",
        string="Career Transitions",
    )
    latest_career_transition_id = fields.Many2one(
        comodel_name="employee_career_transition",
        compute="_compute_career_transition",
        string="Latest Career Transition",
        store=True,
        readonly=True,
    )
    join_career_transition_id = fields.Many2one(
        comodel_name="employee_career_transition",
        compute="_compute_career_transition",
        string="Join Career Transition",
        store=True,
        readonly=True,
    )
    terminate_career_transition_id = fields.Many2one(
        comodel_name="employee_career_transition",
        compute="_compute_career_transition",
        string="Terminate Career Transition",
        store=True,
        readonly=True,
    )
    permanent_career_transition_id = fields.Many2one(
        comodel_name="employee_career_transition",
        compute="_compute_career_transition",
        string="Permanent Career Transition",
        store=True,
        readonly=True,
    )
    contract_career_transition_id = fields.Many2one(
        comodel_name="employee_career_transition",
        compute="_compute_career_transition",
        string="Contract Career Transition",
        store=True,
        readonly=True,
    )
    work_information_method = fields.Selection(
        string="Work Information Method",
        selection=[
            ("manual", "Manual"),
            ("career_transition", "From Career Transition"),
        ],
    )
    manual_company_id = fields.Many2one(
        string="Manual Company",
        comodel_name="res.company",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        compute="_compute_company_id",
        store=True,
        related=False,
    )
    manual_parent_id = fields.Many2one(
        string="Manual Manager",
        comodel_name="hr.employee",
    )
    parent_id = fields.Many2one(
        string="Manager",
        comodel_name="hr.employee",
        compute="_compute_parent_id",
        store=True,
    )
    manual_job_id = fields.Many2one(
        string="Manual Job",
        comodel_name="hr.job",
    )
    job_id = fields.Many2one(
        string="Job",
        comodel_name="hr.job",
        compute="_compute_job_id",
        store=True,
    )
    manual_department_id = fields.Many2one(
        string="Manual Department",
        comodel_name="hr.department",
    )
    department_id = fields.Many2one(
        string="Department",
        comodel_name="hr.department",
        compute="_compute_department_id",
        store=True,
    )
    manual_employment_status_id = fields.Many2one(
        string="Manual Employee Status",
        comodel_name="hr.employment_status",
    )
    employment_status_id = fields.Many2one(
        string="Employee Status",
        comodel_name="hr.employment_status",
        compute="_compute_employment_status_id",
        store=True,
    )
    manual_date_join = fields.Date(
        string="Manual Join Date",
    )
    date_join = fields.Date(
        string="Join Date",
        compute="_compute_date_join",
        store=True,
    )
    manual_date_termination = fields.Date(
        string="Manual Termination Date",
    )
    date_termination = fields.Date(
        string="Termination Date",
        compute="_compute_date_termination",
        store=True,
    )
    manual_date_permanent = fields.Date(
        string="Manual Permanent Date",
    )
    date_permanent = fields.Date(
        string="Permanent Date",
        compute="_compute_date_permanent",
        store=True,
    )
    manual_date_contract_start = fields.Date(
        string="Manual Contract Start Date",
    )
    manual_date_contract_end = fields.Date(
        string="Manual Contract End Date",
    )
    date_contract_start = fields.Date(
        string="Contract Start Date",
        compute="_compute_date_contract_start",
        store=True,
    )
    date_contract_end = fields.Date(
        string="Contract End Date",
        compute="_compute_date_contract_end",
        store=True,
    )

    @api.depends(
        "career_transition_ids",
        "career_transition_ids.state",
        "career_transition_ids.type_id",
    )
    def _compute_career_transition(self):
        for record in self:
            record.latest_career_transition_id = False
            record.join_career_transition_id = False
            record.terminate_career_transition_id = False
            record.permanent_career_transition_id = False
            record.contract_career_transition_id = False
            latest = self.env["employee_career_transition"].search(
                [
                    ("state", "=", "done"),
                    ("employee_id", "=", record.id),
                ]
            )

            if len(latest) > 0:
                record.latest_career_transition_id = latest[0]

            joins = self.env["employee_career_transition"].search(
                [
                    ("state", "=", "done"),
                    ("type_id", "=", record.company_id.join_transition_type_id.id),
                    ("employee_id", "=", record.id),
                ]
            )

            if len(joins) > 0:
                record.join_career_transition_id = joins[0]

            terminates = self.env["employee_career_transition"].search(
                [
                    ("state", "=", "done"),
                    ("type_id", "=", record.company_id.terminate_transition_type_id.id),
                    ("employee_id", "=", record.id),
                ]
            )

            if len(terminates) > 0:
                record.terminate_career_transition_id = terminates[0]

            permanents = self.env["employee_career_transition"].search(
                [
                    ("state", "=", "done"),
                    ("type_id", "=", record.company_id.permanent_transition_type_id.id),
                    ("employee_id", "=", record.id),
                ]
            )

            if len(permanents) > 0:
                record.permanent_career_transition_id = permanents[0]

            contracts = self.env["employee_career_transition"].search(
                [
                    ("state", "=", "done"),
                    ("type_id", "=", record.company_id.contract_transition_type_id.id),
                    ("employee_id", "=", record.id),
                ]
            )

            if len(contracts) > 0:
                record.contract_career_transition_id = contracts[0]

    @api.depends(
        "work_information_method",
        "latest_career_transition_id",
        "manual_company_id",
    )
    def _compute_company_id(self):
        for record in self:
            record.company_id = self.env.company
            if record.work_information_method == "manual":
                if record.manual_company_id:
                    record.company_id = record.manual_company_id
            elif (
                record.work_information_method == "career_transition"
                and record.latest_career_transition_id
            ):
                if record.latest_career_transition_id.new_company_id:
                    record.company_id = (
                        record.latest_career_transition_id.new_company_id
                    )

    @api.depends(
        "work_information_method",
        "latest_career_transition_id",
        "manual_department_id",
    )
    def _compute_department_id(self):
        for record in self:
            record.department_id = record.manual_department_id
            if (
                record.work_information_method == "career_transition"
                and record.latest_career_transition_id
            ):
                record.department_id = (
                    record.latest_career_transition_id.new_department_id
                )

    @api.depends(
        "work_information_method",
        "latest_career_transition_id",
        "manual_job_id",
    )
    def _compute_job_id(self):
        for record in self:
            record.job_id = record.manual_job_id
            if (
                record.work_information_method == "career_transition"
                and record.latest_career_transition_id
            ):
                record.job_id = record.latest_career_transition_id.new_job_id

    @api.depends(
        "work_information_method",
        "latest_career_transition_id",
        "manual_parent_id",
    )
    def _compute_parent_id(self):
        for record in self:
            record.parent_id = record.manual_parent_id
            if (
                record.work_information_method == "career_transition"
                and record.latest_career_transition_id
            ):
                record.parent_id = record.latest_career_transition_id.new_parent_id

    @api.depends(
        "work_information_method",
        "latest_career_transition_id",
        "manual_employment_status_id",
    )
    def _compute_employment_status_id(self):
        for record in self:
            record.employment_status_id = record.manual_employment_status_id
            if (
                record.work_information_method == "career_transition"
                and record.latest_career_transition_id
            ):
                record.employment_status_id = (
                    record.latest_career_transition_id.new_employment_status_id
                )

    @api.depends(
        "work_information_method",
        "join_career_transition_id",
        "manual_date_join",
    )
    def _compute_date_join(self):
        for record in self:
            record.date_join = record.manual_date_join
            if (
                record.work_information_method == "career_transition"
                and record.join_career_transition_id
            ):
                record.date_join = record.join_career_transition_id.effective_date

    @api.depends(
        "work_information_method",
        "terminate_career_transition_id",
        "manual_date_termination",
    )
    def _compute_date_termination(self):
        for record in self:
            record.date_termination = record.manual_date_termination
            if (
                record.work_information_method == "career_transition"
                and record.terminate_career_transition_id
            ):
                record.date_termination = (
                    record.terminate_career_transition_id.effective_date
                )

    @api.depends(
        "work_information_method",
        "permanent_career_transition_id",
        "manual_date_permanent",
    )
    def _compute_date_permanent(self):
        for record in self:
            record.date_permanent = record.manual_date_permanent
            if (
                record.work_information_method == "career_transition"
                and record.permanent_career_transition_id
            ):
                record.date_permanent = (
                    record.permanent_career_transition_id.effective_date
                )

    @api.depends(
        "work_information_method",
        "contract_career_transition_id",
        "manual_date_contract_start",
    )
    def _compute_date_contract_start(self):
        for record in self:
            record.date_contract_start = record.manual_date_contract_start
            if (
                record.work_information_method == "career_transition"
                and record.contract_career_transition_id
            ):
                record.date_contract_start = (
                    record.contract_career_transition_id.date_contract_start
                )

    @api.depends(
        "work_information_method",
        "contract_career_transition_id",
        "manual_date_contract_end",
    )
    def _compute_date_contract_end(self):
        for record in self:
            record.date_contract_end = record.manual_date_contract_end
            if (
                record.work_information_method == "career_transition"
                and record.contract_career_transition_id
            ):
                record.date_contract_end = (
                    record.contract_career_transition_id.date_contract_end
                )

    def action_set_method_2_career(self):
        for record in self:
            record.work_information_method = "career_transition"

    def action_set_method_2_manual(self):
        for record in self:
            record.work_information_method = "manual"
