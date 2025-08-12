# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging


def migrate(cr, version):
    if not version:
        return
    logger = logging.getLogger(__name__)
    logger.info("Updating hr_employee...")
    cr.execute(
        """
    UPDATE
        hr_employee dest
    SET
        manual_company_id = src.company_id,
        manual_parent_id = src.parent_id,
        manual_job_id = src.job_id,
        manual_department_id = src.department_id,
        manual_employment_status_id = src.employment_status_id,
        manual_date_join = src.date_join,
        manual_date_termination = src.date_termination,
        manual_date_permanent = src.date_permanent,
        manual_date_contract_start = src.date_contract_start,
        manual_date_contract_end = src.date_contract_end
    FROM hr_employee src
    WHERE
        dest.id = src.id;
    """
    )
    logger.info("Successfully updated hr_employee tables")
