from typing import List, Any

from .enums import ExpenseStateEnum, SourceAccountTypeEnum, FundSourceEnum
from .constants import REIMBURSABLE_IMPORT_STATE, CCC_IMPORT_STATE
from .models import ExpenseGroupSettingsAdapter


def get_expense_import_states(expense_group_settings: Any, integration_type: str = 'default') -> List[str]:
    """
    Get expense import state
    :param expense_group_settings: expense group settings model instance
    :param integration_type: Type of integration (e.g. 'default', 'xero')
    :return: expense import state
    """
    expense_group_settings = ExpenseGroupSettingsAdapter(expense_group_settings, integration_type)
    expense_import_state = set()

    if expense_group_settings.ccc_expense_state == ExpenseStateEnum.APPROVED:
        expense_import_state = {ExpenseStateEnum.APPROVED, ExpenseStateEnum.PAYMENT_PROCESSING, ExpenseStateEnum.PAID}

    if expense_group_settings.expense_state == ExpenseStateEnum.PAYMENT_PROCESSING:
        expense_import_state.add(ExpenseStateEnum.PAYMENT_PROCESSING)
        expense_import_state.add(ExpenseStateEnum.PAID)

    if expense_group_settings.expense_state == ExpenseStateEnum.PAID or expense_group_settings.ccc_expense_state == ExpenseStateEnum.PAID:
        expense_import_state.add(ExpenseStateEnum.PAID)

    return list(expense_import_state)


def filter_expenses_based_on_state(expenses: List[Any], expense_group_settings: Any, integration_type: str = 'default'):
    """
    Filter expenses based on the expense state
    :param expenses: list of expenses
    :param expense_group_settings: expense group settings model instance
    :param integration_type: Type of integration (e.g. 'default', 'xero')
    :return: list of filtered expenses
    """
    expense_group_settings = ExpenseGroupSettingsAdapter(expense_group_settings, integration_type)

    allowed_reimbursable_import_state = REIMBURSABLE_IMPORT_STATE.get(expense_group_settings.expense_state)
    reimbursable_expenses = list(filter(lambda expense: expense['source_account_type'] == SourceAccountTypeEnum.PERSONAL_CASH_ACCOUNT and expense['state'] in allowed_reimbursable_import_state, expenses))

    allowed_ccc_import_state = CCC_IMPORT_STATE.get(expense_group_settings.ccc_expense_state)
    ccc_expenses = list(filter(lambda expense: expense['source_account_type'] == SourceAccountTypeEnum.PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT and expense['state'] in allowed_ccc_import_state, expenses))

    return reimbursable_expenses + ccc_expenses


def get_source_account_types_based_on_export_modules(reimbursable_export_module: str, ccc_export_module: str) -> List[str]:
    """
    Get source account types based on the export modules
    :param reimbursable_export_module: reimbursable export module
    :param ccc_export_module: ccc export module
    :return: list of source account types
    """
    source_account_types = []
    if reimbursable_export_module:
        source_account_types.append(SourceAccountTypeEnum.PERSONAL_CASH_ACCOUNT)
    if ccc_export_module:
        source_account_types.append(SourceAccountTypeEnum.PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT)

    return source_account_types


def get_fund_source_based_on_export_modules(reimbursable_export_module: str, ccc_export_module: str) -> List[str]:
    """
    Get fund source based on the export modules
    :param reimbursable_export_module: reimbursable export module
    :param ccc_export_module: ccc export module
    :return: list of fund source
    """
    fund_source = []
    if reimbursable_export_module:
        fund_source.append(FundSourceEnum.PERSONAL)
    if ccc_export_module:
        fund_source.append(FundSourceEnum.CCC)

    return fund_source
