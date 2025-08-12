# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.ssi_decorator import ssi_decorator


class HrCareerTransition(models.Model):
    _name = "employee_career_transition"
    _description = "Career Transition"
    _inherit = [
        "mixin.transaction_confirm",
        "mixin.transaction_done",
        "mixin.transaction_cancel",
        "mixin.employee_document",
    ]

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True

    # Attributes related to add element on form view automatically
    _automatically_insert_multiple_approval_page = True
    _statusbar_visible_label = "draft,confirm,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]

    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "action_done",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    _order = "effective_date desc, employee_id, id"

    # Sequence attribute
    _create_sequence_state = "done"

    type_id = fields.Many2one(
        comodel_name="employee_career_transition_type",
        string="Career Transition Type",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    reason_id = fields.Many2one(
        comodel_name="employee_career_transition_type.reason",
        string="Reason",
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    allowed_reason_ids = fields.Many2many(
        comodel_name="employee_career_transition_type.reason",
        string="Allowed Reasons",
        compute="_compute_allowed_reason_ids",
        compute_sudo=True,
        store=False,
    )
    require_reason = fields.Boolean(
        related="type_id.require_reason",
        string="Require Reason",
        store=False,
    )
    effective_date = fields.Date(
        string="Effective Date",
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    @api.depends(
        "type_id",
    )
    def _compute_contract(self):
        company = self.env.company
        contract_type_id = company.contract_transition_type_id.id
        for document in self:
            document.contract = False
            if contract_type_id:
                if document.type_id.id == contract_type_id:
                    document.contract = True

    contract = fields.Boolean(
        string="Contract",
        compute="_compute_contract",
        store=False,
    )

    @api.depends(
        "type_id",
    )
    def _compute_join(self):
        company = self.env.company
        join_type_id = company.join_transition_type_id.id
        for document in self:
            document.join = False
            if join_type_id:
                if document.type_id.id == join_type_id:
                    document.join = True

    join = fields.Boolean(
        string="Join",
        compute="_compute_join",
        store=False,
    )

    @api.depends(
        "type_id",
    )
    def _compute_permanent(self):
        company = self.env.company
        permanent_type_id = company.permanent_transition_type_id.id
        for document in self:
            document.permanent = False
            if permanent_type_id:
                if document.type_id.id == permanent_type_id:
                    document.permanent = True

    permanent = fields.Boolean(
        string="Permanent",
        compute="_compute_permanent",
        store=False,
    )

    @api.depends(
        "type_id",
    )
    def _compute_terminate(self):
        company = self.env.company
        terminate_type_id = company.permanent_transition_type_id.id
        for document in self:
            document.terminate = False
            if terminate_type_id:
                if document.type_id.id == terminate_type_id:
                    document.terminate = True

    terminate = fields.Boolean(
        string="Terminate",
        compute="_compute_terminate",
        store=False,
    )

    @api.depends(
        "reason_id",
        "type_id",
    )
    def _compute_limit(self):
        for document in self:
            document.limit = 0
            if document.reason_id:
                document.limit = document.reason_id.limit
            else:
                document.limit = document.type_id.limit

    limit = fields.Integer(
        string="Limit",
        compute="_compute_limit",
        store=False,
    )

    date_contract_start = fields.Date(
        string="Contract Start Date",
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date_contract_end = fields.Date(
        string="Contract End Date",
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    change_company = fields.Boolean(
        string="Change Company",
        related="type_id.change_company",
    )
    require_company = fields.Boolean(
        string="Require Company",
        related="type_id.require_company",
    )
    change_parent = fields.Boolean(
        string="Change Manager",
        related="type_id.change_parent",
    )
    require_parent = fields.Boolean(
        string="Require Manager",
        related="type_id.require_parent",
    )
    change_job = fields.Boolean(
        string="Change Job Position",
        related="type_id.change_job",
    )
    require_job = fields.Boolean(
        string="Require Job Position",
        related="type_id.require_job",
    )
    change_department = fields.Boolean(
        string="Change Department",
        related="type_id.change_department",
    )
    require_department = fields.Boolean(
        string="Require Department",
        related="type_id.require_department",
    )
    change_employment_status = fields.Boolean(
        string="Change Employee Status",
        related="type_id.change_employment_status",
    )
    require_employment_status = fields.Boolean(
        string="Require Employee Status",
        related="type_id.require_employment_status",
    )
    archieve = fields.Boolean(
        string="Archieve",
        default=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    previous_company_id = fields.Many2one(
        string="Previous Company",
        comodel_name="res.company",
        readonly=True,
    )
    previous_department_id = fields.Many2one(
        string="Previous Department",
        comodel_name="hr.department",
        readonly=True,
    )
    previous_job_id = fields.Many2one(
        string="Previous Job Position",
        comodel_name="hr.job",
        readonly=True,
    )
    previous_parent_id = fields.Many2one(
        string="Previous Manager",
        comodel_name="hr.employee",
        readonly=True,
    )
    previous_employment_status_id = fields.Many2one(
        string="Previous Employment Status",
        comodel_name="hr.employment_status",
        readonly=True,
    )
    new_company_id = fields.Many2one(
        comodel_name="res.company",
        string="New Company",
        ondelete="restrict",
    )
    new_department_id = fields.Many2one(
        comodel_name="hr.department",
        string="New Department",
        ondelete="restrict",
    )
    new_job_id = fields.Many2one(
        comodel_name="hr.job",
        string="New Job Position",
        ondelete="restrict",
    )
    new_parent_id = fields.Many2one(
        comodel_name="hr.employee",
        string="New Manager",
        ondelete="restrict",
    )

    @api.depends("type_id", "archieve")
    def _compute_allowed_employment_status_ids(self):
        obj_hr_employment_status = self.env["hr.employment_status"]
        for record in self:
            result = []
            criteria = [("id", "in", record.type_id.allowed_employment_status_ids.ids)]
            employment_status_ids = obj_hr_employment_status.search(criteria)
            if employment_status_ids:
                result = employment_status_ids.ids

            record.allowed_employment_status_ids = result

    allowed_employment_status_ids = fields.Many2many(
        comodel_name="hr.employment_status",
        string="Allowed Employment Status",
        compute="_compute_allowed_employment_status_ids",
        compute_sudo=True,
        store=False,
    )

    new_employment_status_id = fields.Many2one(
        comodel_name="hr.employment_status",
        string="New Employment Status",
        ondelete="restrict",
        readonly=True,
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
            ("reject", "Rejected"),
        ],
        default="draft",
        copy=False,
    )

    @api.model
    def _get_policy_field(self):
        res = super(HrCareerTransition, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "reject_ok",
            "restart_approval_ok",
            "cancel_ok",
            "restart_ok",
            "done_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @api.depends("type_id")
    def _compute_allowed_reason_ids(self):
        for record in self:
            result = []
            if record.type_id:
                reasons = self.env["employee_career_transition_type.reason"].search(
                    [("type_id", "=", record.type_id.id)]
                )
                result = reasons.ids

            record.allowed_reason_ids = result

    @api.onchange(
        "employee_id",
    )
    def onchange_previous_company_id(self):
        self.previous_company_id = False
        if self.employee_id:
            self.previous_company_id = self.employee_id.company_id

    @api.onchange(
        "previous_company_id",
        "archieve",
    )
    def onchange_new_company_id(self):
        self.new_company_id = False
        if self.previous_company_id and not self.archieve:
            self.new_company_id = self.previous_company_id

    @api.onchange(
        "employee_id",
    )
    def onchange_previous_department_id(self):
        self.previous_department_id = False
        if self.employee_id:
            self.previous_department_id = self.employee_id.department_id

    @api.onchange(
        "previous_department_id",
        "archieve",
    )
    def onchange_new_department_id(self):
        self.new_department_id = False
        if self.previous_department_id and not self.archieve:
            self.new_department_id = self.previous_department_id

    @api.onchange(
        "employee_id",
    )
    def onchange_previous_parent_id(self):
        self.previous_parent_id = False
        if self.employee_id:
            self.previous_parent_id = self.employee_id.parent_id

    @api.onchange(
        "previous_parent_id",
        "archieve",
    )
    def onchange_new_parent_id(self):
        self.new_parent_id = False
        if self.previous_parent_id and not self.archieve:
            self.new_parent_id = self.previous_parent_id

    @api.onchange(
        "employee_id",
    )
    def onchange_previous_job_id(self):
        self.previous_job_id = False
        if self.employee_id:
            self.previous_job_id = self.employee_id.job_id

    @api.onchange(
        "previous_job_id",
        "archieve",
    )
    def onchange_new_job_id(self):
        self.new_job_id = False
        if self.previous_job_id and not self.archieve:
            self.new_job_id = self.previous_job_id

    @api.onchange(
        "employee_id",
    )
    def onchange_previous_employment_status_id(self):
        self.previous_employment_status_id = False
        if self.employee_id:
            self.previous_employment_status_id = self.employee_id.employment_status_id

    @api.onchange(
        "previous_employment_status_id",
        "archieve",
        "type_id",
    )
    def onchange_new_employment_status_id(self):
        self.new_employment_status_id = False
        if self.previous_employment_status_id and not self.archieve:
            self.new_employment_status_id = self.previous_employment_status_id
        else:
            self.new_employment_status_id = self.type_id.default_employment_status_id

    @api.onchange(
        "date_contract_start",
    )
    def onchange_effective_date(self):
        self.effective_date = False
        if self.date_contract_start:
            self.effective_date = self.date_contract_start

    @ssi_decorator.post_cancel_check
    def _01_check_latest_history_when_cancel(self):
        if self.id != self.employee_id.latest_career_transition_id.id:
            if not self.archieve:
                if self.state == "done":
                    error_message = _(
                        """
                    Context: Cancel employee career transition
                    Database ID: %s
                    Problem: Employee career transition is not latest transition
                    Solution: Find and cancel latest transition first
                    """
                        % (self.id)
                    )
                    raise ValidationError(error_message)

    @ssi_decorator.pre_confirm_check()
    def _01_check_limit_before_confirm(self):
        self._check_limit_transaction()

    @api.constrains(
        "date_contract_start",
        "date_contract_end",
    )
    def _check_date_contract_start_end(self):
        for record in self.sudo():
            if record.date_contract_start and record.date_contract_end:
                strWarning = _(
                    "Contract Date end must be greater than Contract Date Start"
                )
                if record.date_contract_end < record.date_contract_start:
                    raise ValidationError(strWarning)

    @api.constrains(
        "employee_id",
        "type_id",
        "reason_id",
    )
    def _check_limit_transaction(self):
        for record in self.sudo():
            if record.limit > 0:
                if record.employee_id and record.reason_id:
                    transition_ids = record.employee_id.career_transition_ids.filtered(
                        lambda x: x.reason_id.id == record.reason_id.id
                    )
                    if len(transition_ids.ids) > record.limit:
                        error_message = _(
                            """
                        Context: Validation Error
                        Database ID: %s
                        Problem: This transaction has exceeded the limit %s
                        Solution: Change the limit or please contact HR
                        """
                            % (record.id, record.limit)
                        )
                        raise ValidationError(error_message)
                elif record.employee_id and record.type_id:
                    transition_ids = record.employee_id.career_transition_ids.filtered(
                        lambda x: x.type_id.id == record.type_id.id
                    )
                    if len(transition_ids.ids) > record.limit:
                        error_message = _(
                            """
                        Context: Validation Error
                        Database ID: %s
                        Problem: This transaction has exceeded the limit %s
                        Solution: Change the limit or please contact HR
                        """
                            % (record.id, record.limit)
                        )
                        raise ValidationError(error_message)

    @api.constrains(
        "effective_date",
        "archieve",
        "employee_id",
    )
    def _check_effective_date(self):
        for record in self.sudo():
            latest_effective_date = (
                record.employee_id.latest_career_transition_id
                and record.employee_id.latest_career_transition_id.effective_date
                or False
            )
            if latest_effective_date:
                if record.archieve:
                    if record.effective_date > latest_effective_date:
                        error_message = _(
                            """
                        Context: Validation Error
                        Database ID: %s
                        Problem: Effective date on archieve data cannot be greater than %s
                        Solution: Change the effective date or please contact HR
                        """
                            % (record.id, latest_effective_date)
                        )
                        raise ValidationError(error_message)
                else:
                    if record.effective_date < latest_effective_date:
                        error_message = _(
                            """
                        Context: Validation Error
                        Database ID: %s
                        Problem: Effective date on non-archieve data must be greater than %s
                        Solution: Change the effective date or please contact HR
                        """
                            % (record.id, latest_effective_date)
                        )
                        raise ValidationError(error_message)
