"""Tests for the GAHTO module"""
# Stdlib imports
from random import choices as random_choices

# Package imports
from pytest import raises

# Local imports
from gahto.gahto import AccountType  # pylint: disable=E0401


def test_account_type_constructor():
    """Test that the AccountType constructor behaves properly"""
    assert isinstance(AccountType("AccountsPayable"), AccountType)
    assert isinstance(AccountType("AccountsReceivable"), AccountType)
    assert isinstance(AccountType("Asset"), AccountType)
    assert isinstance(AccountType("Bank"), AccountType)
    assert isinstance(AccountType("Cash"), AccountType)
    assert isinstance(AccountType("CreditCard"), AccountType)
    assert isinstance(AccountType("Equity"), AccountType)
    assert isinstance(AccountType("Expense"), AccountType)
    assert isinstance(AccountType("Income"), AccountType)
    assert isinstance(AccountType("Liability"), AccountType)
    assert isinstance(AccountType("MutualFund"), AccountType)
    assert isinstance(AccountType("Stock"), AccountType)
    assert isinstance(AccountType("Trading"), AccountType)
    with raises(TypeError) as e_info:
        AccountType()
    assert e_info.type is TypeError
    assert e_info.value.args[0] == "AccountType.__init__() missing 1 required"\
        " positional argument: 'typename'"
    for _t in ["", "nope",
               "".join(random_choices([chr(x) for x in range(32, 127)], k=8))]:
        with raises(ValueError) as e_info:
            AccountType(_t)
        assert e_info.type is ValueError
        assert e_info.value.args[0] \
            == f"AccountType cannot take the value '{_t}'."


def test_account_type_equivalence():  # pylint: disable=R0915
    """Test that the different AccountType constants are properly set"""
    assert AccountType.AccountsPayable == AccountType.PAYABLE
    assert AccountType.AccountsReceivable == AccountType.RECEIVABLE
    assert AccountType.Asset == AccountType.ASSET
    assert AccountType.Bank == AccountType.BANK
    assert AccountType.Cash == AccountType.CASH
    assert AccountType.CreditCard == AccountType.CREDIT
    assert AccountType.Equity == AccountType.Equity
    assert AccountType.Expense == AccountType.EXPENSE
    assert AccountType.Income == AccountType.INCOME
    assert AccountType.Liability == AccountType.LIABILITY
    assert AccountType.MutualFund == AccountType.MUTUAL
    assert AccountType.Stock == AccountType.STOCK
    assert AccountType.Trading == AccountType.TRADING

    assert AccountType.AccountsPayable != AccountType.AccountsReceivable
    assert AccountType.AccountsPayable != AccountType.Asset
    assert AccountType.AccountsPayable != AccountType.Bank
    assert AccountType.AccountsPayable != AccountType.Cash
    assert AccountType.AccountsPayable != AccountType.CreditCard
    assert AccountType.AccountsPayable != AccountType.Equity
    assert AccountType.AccountsPayable != AccountType.Expense
    assert AccountType.AccountsPayable != AccountType.Income
    assert AccountType.AccountsPayable != AccountType.Liability
    assert AccountType.AccountsPayable != AccountType.MutualFund
    assert AccountType.AccountsPayable != AccountType.Stock
    assert AccountType.AccountsPayable != AccountType.Trading

    assert AccountType.AccountsReceivable != AccountType.Asset
    assert AccountType.AccountsReceivable != AccountType.Bank
    assert AccountType.AccountsReceivable != AccountType.Cash
    assert AccountType.AccountsReceivable != AccountType.CreditCard
    assert AccountType.AccountsReceivable != AccountType.Equity
    assert AccountType.AccountsReceivable != AccountType.Expense
    assert AccountType.AccountsReceivable != AccountType.Income
    assert AccountType.AccountsReceivable != AccountType.Liability
    assert AccountType.AccountsReceivable != AccountType.MutualFund
    assert AccountType.AccountsReceivable != AccountType.Stock
    assert AccountType.AccountsReceivable != AccountType.Trading

    assert AccountType.Asset != AccountType.Bank
    assert AccountType.Asset != AccountType.Cash
    assert AccountType.Asset != AccountType.CreditCard
    assert AccountType.Asset != AccountType.Equity
    assert AccountType.Asset != AccountType.Expense
    assert AccountType.Asset != AccountType.Income
    assert AccountType.Asset != AccountType.Liability
    assert AccountType.Asset != AccountType.MutualFund
    assert AccountType.Asset != AccountType.Stock
    assert AccountType.Asset != AccountType.Trading

    assert AccountType.Bank != AccountType.Cash
    assert AccountType.Bank != AccountType.CreditCard
    assert AccountType.Bank != AccountType.Equity
    assert AccountType.Bank != AccountType.Expense
    assert AccountType.Bank != AccountType.Income
    assert AccountType.Bank != AccountType.Liability
    assert AccountType.Bank != AccountType.MutualFund
    assert AccountType.Bank != AccountType.Stock
    assert AccountType.Bank != AccountType.Trading

    assert AccountType.Cash != AccountType.CreditCard
    assert AccountType.Cash != AccountType.Equity
    assert AccountType.Cash != AccountType.Expense
    assert AccountType.Cash != AccountType.Income
    assert AccountType.Cash != AccountType.Liability
    assert AccountType.Cash != AccountType.MutualFund
    assert AccountType.Cash != AccountType.Stock
    assert AccountType.Cash != AccountType.Trading

    assert AccountType.CreditCard != AccountType.Equity
    assert AccountType.CreditCard != AccountType.Expense
    assert AccountType.CreditCard != AccountType.Income
    assert AccountType.CreditCard != AccountType.Liability
    assert AccountType.CreditCard != AccountType.MutualFund
    assert AccountType.CreditCard != AccountType.Stock
    assert AccountType.CreditCard != AccountType.Trading

    assert AccountType.Equity != AccountType.Expense
    assert AccountType.Equity != AccountType.Income
    assert AccountType.Equity != AccountType.Liability
    assert AccountType.Equity != AccountType.MutualFund
    assert AccountType.Equity != AccountType.Stock
    assert AccountType.Equity != AccountType.Trading

    assert AccountType.Expense != AccountType.Income
    assert AccountType.Expense != AccountType.Liability
    assert AccountType.Expense != AccountType.MutualFund
    assert AccountType.Expense != AccountType.Stock
    assert AccountType.Expense != AccountType.Trading

    assert AccountType.Income != AccountType.Liability
    assert AccountType.Income != AccountType.MutualFund
    assert AccountType.Income != AccountType.Stock
    assert AccountType.Income != AccountType.Trading

    assert AccountType.Liability != AccountType.MutualFund
    assert AccountType.Liability != AccountType.Stock
    assert AccountType.Liability != AccountType.Trading

    assert AccountType.MutualFund != AccountType.Stock
    assert AccountType.MutualFund != AccountType.Trading

    assert AccountType.Stock != AccountType.Trading


def test_filiation():
    """Test the filiation logic"""

    # NOTE The set of allowed children and parents is exactly symmetrical.
    # Therefore the contents of the corresponding dicts for "children" and
    # "parents" are equal, but there are two different sets of dicts in case
    # this ever changes.

    default_allowed_children = {
        AccountType.AccountsPayable: True,
        AccountType.AccountsReceivable: True,
        AccountType.Asset: True,
        AccountType.Bank: True,
        AccountType.Cash: True,
        AccountType.CreditCard: True,
        AccountType.Equity: False,
        AccountType.Expense: False,
        AccountType.Income: False,
        AccountType.Liability: True,
        AccountType.MutualFund: True,
        AccountType.Stock: True,
        AccountType.Trading: False,
    }
    default_allowed_parents = {
        AccountType.AccountsPayable: True,
        AccountType.AccountsReceivable: True,
        AccountType.Asset: True,
        AccountType.Bank: True,
        AccountType.Cash: True,
        AccountType.CreditCard: True,
        AccountType.Equity: False,
        AccountType.Expense: False,
        AccountType.Income: False,
        AccountType.Liability: True,
        AccountType.MutualFund: True,
        AccountType.Stock: True,
        AccountType.Trading: False,
    }
    allowed_children = {
            AccountType.AccountsPayable: default_allowed_children,
            AccountType.AccountsReceivable: default_allowed_children,
            AccountType.Asset: default_allowed_children,
            AccountType.Bank: default_allowed_children,
            AccountType.Cash: default_allowed_children,
            AccountType.CreditCard: default_allowed_children,
            AccountType.Equity: {
                AccountType.AccountsPayable: False,
                AccountType.AccountsReceivable: False,
                AccountType.Asset: False,
                AccountType.Bank: False,
                AccountType.Cash: False,
                AccountType.CreditCard: False,
                AccountType.Equity: True,
                AccountType.Expense: False,
                AccountType.Income: False,
                AccountType.Liability: False,
                AccountType.MutualFund: False,
                AccountType.Stock: False,
                AccountType.Trading: False,
            },
            AccountType.Expense: {
                AccountType.AccountsPayable: False,
                AccountType.AccountsReceivable: False,
                AccountType.Asset: False,
                AccountType.Bank: False,
                AccountType.Cash: False,
                AccountType.CreditCard: False,
                AccountType.Equity: False,
                AccountType.Expense: True,
                AccountType.Income: True,
                AccountType.Liability: False,
                AccountType.MutualFund: False,
                AccountType.Stock: False,
                AccountType.Trading: False,
            },
            AccountType.Income: {
                AccountType.AccountsPayable: False,
                AccountType.AccountsReceivable: False,
                AccountType.Asset: False,
                AccountType.Bank: False,
                AccountType.Cash: False,
                AccountType.CreditCard: False,
                AccountType.Equity: False,
                AccountType.Expense: True,
                AccountType.Income: True,
                AccountType.Liability: False,
                AccountType.MutualFund: False,
                AccountType.Stock: False,
                AccountType.Trading: False,
            },
            AccountType.Liability: default_allowed_children,
            AccountType.MutualFund: default_allowed_children,
            AccountType.Stock: default_allowed_children,
            AccountType.Trading: {
                AccountType.AccountsPayable: False,
                AccountType.AccountsReceivable: False,
                AccountType.Asset: False,
                AccountType.Bank: False,
                AccountType.Cash: False,
                AccountType.CreditCard: False,
                AccountType.Equity: False,
                AccountType.Expense: False,
                AccountType.Income: False,
                AccountType.Liability: False,
                AccountType.MutualFund: False,
                AccountType.Stock: False,
                AccountType.Trading: True,
            },
    }
    allowed_parents = {
            AccountType.AccountsPayable: default_allowed_parents,
            AccountType.AccountsReceivable: default_allowed_parents,
            AccountType.Asset: default_allowed_parents,
            AccountType.Bank: default_allowed_parents,
            AccountType.Cash: default_allowed_parents,
            AccountType.CreditCard: default_allowed_parents,
            AccountType.Equity: {
                AccountType.AccountsPayable: False,
                AccountType.AccountsReceivable: False,
                AccountType.Asset: False,
                AccountType.Bank: False,
                AccountType.Cash: False,
                AccountType.CreditCard: False,
                AccountType.Equity: True,
                AccountType.Expense: False,
                AccountType.Income: False,
                AccountType.Liability: False,
                AccountType.MutualFund: False,
                AccountType.Stock: False,
                AccountType.Trading: False,
            },
            AccountType.Expense: {
                AccountType.AccountsPayable: False,
                AccountType.AccountsReceivable: False,
                AccountType.Asset: False,
                AccountType.Bank: False,
                AccountType.Cash: False,
                AccountType.CreditCard: False,
                AccountType.Equity: False,
                AccountType.Expense: True,
                AccountType.Income: True,
                AccountType.Liability: False,
                AccountType.MutualFund: False,
                AccountType.Stock: False,
                AccountType.Trading: False,
            },
            AccountType.Income: {
                AccountType.AccountsPayable: False,
                AccountType.AccountsReceivable: False,
                AccountType.Asset: False,
                AccountType.Bank: False,
                AccountType.Cash: False,
                AccountType.CreditCard: False,
                AccountType.Equity: False,
                AccountType.Expense: True,
                AccountType.Income: True,
                AccountType.Liability: False,
                AccountType.MutualFund: False,
                AccountType.Stock: False,
                AccountType.Trading: False,
            },
            AccountType.Liability: default_allowed_parents,
            AccountType.MutualFund: default_allowed_parents,
            AccountType.Stock: default_allowed_parents,
            AccountType.Trading: {
                AccountType.AccountsPayable: False,
                AccountType.AccountsReceivable: False,
                AccountType.Asset: False,
                AccountType.Bank: False,
                AccountType.Cash: False,
                AccountType.CreditCard: False,
                AccountType.Equity: False,
                AccountType.Expense: False,
                AccountType.Income: False,
                AccountType.Liability: False,
                AccountType.MutualFund: False,
                AccountType.Stock: False,
                AccountType.Trading: True,
            },
    }

    for parent, children in allowed_children.items():
        for child, correct in children.items():
            assert child.is_valid_child_of(parent) is correct, \
                f"{child.value()}.is_valid_child_of({parent.value()}) " \
                f"!= {correct}"

    for child, parents in allowed_parents.items():
        for parent, correct in parents.items():
            assert parent.is_valid_parent_of(child) is correct, \
                f"{parent.value()}.is_valid_parent_of({child.value()}) " \
                f"!= {correct}"


def test_repr():
    """Test the __repr__ function"""
    obj = AccountType.AccountsPayable
    loc = hex(id(obj))
    assert repr(obj) == f"<gahto.gahto.AccountType({obj.type_name()}) object "\
        f"at {loc}>"


def test_type_name():
    """Test the type name"""
    assert AccountType.AccountsPayable.type_name() == "AccountsPayable"
    assert AccountType.AccountsReceivable.type_name() == "AccountsReceivable"
    assert AccountType.Asset.type_name() == "Asset"
    assert AccountType.Bank.type_name() == "Bank"
    assert AccountType.Cash.type_name() == "Cash"
    assert AccountType.CreditCard.type_name() == "CreditCard"
    assert AccountType.Equity.type_name() == "Equity"
    assert AccountType.Expense.type_name() == "Expense"
    assert AccountType.Income.type_name() == "Income"
    assert AccountType.Liability.type_name() == "Liability"
    assert AccountType.MutualFund.type_name() == "MutualFund"
    assert AccountType.Stock.type_name() == "Stock"
    assert AccountType.Trading.type_name() == "Trading"


def test_value():
    """Test the type name"""
    assert AccountType.AccountsPayable.value() == "PAYABLE"
    assert AccountType.AccountsReceivable.value() == "RECEIVABLE"
    assert AccountType.Asset.value() == "ASSET"
    assert AccountType.Bank.value() == "BANK"
    assert AccountType.Cash.value() == "CASH"
    assert AccountType.CreditCard.value() == "CREDIT"
    assert AccountType.Equity.value() == "EQUITY"
    assert AccountType.Expense.value() == "EXPENSE"
    assert AccountType.Income.value() == "INCOME"
    assert AccountType.Liability.value() == "LIABILITY"
    assert AccountType.MutualFund.value() == "MUTUAL"
    assert AccountType.Stock.value() == "STOCK"
    assert AccountType.Trading.value() == "TRADING"


def test_label():
    """Test the type name"""
    assert AccountType.AccountsPayable.label() == "Accounts Payable"
    assert AccountType.AccountsReceivable.label() == "Accounts Receivable"
    assert AccountType.Asset.label() == "Asset"
    assert AccountType.Bank.label() == "Bank"
    assert AccountType.Cash.label() == "Cash"
    assert AccountType.CreditCard.label() == "Credit Card"
    assert AccountType.Equity.label() == "Equity"
    assert AccountType.Expense.label() == "Expense"
    assert AccountType.Income.label() == "Income"
    assert AccountType.Liability.label() == "Liability"
    assert AccountType.MutualFund.label() == "Mutual Fund"
    assert AccountType.Stock.label() == "Stock"
    assert AccountType.Trading.label() == "Trading"
