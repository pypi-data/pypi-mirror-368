"""Tests for the GAHTO module"""

# Stdlib imports
from random import choices as random_choices
from uuid import uuid4
from xml.etree import ElementTree

# Package imports
from iso_4217 import Currency
from pytest import raises

# Local imports
from gahto.gahto import GATO  # pylint: disable=E0401
from gahto.gahto import AccountType  # pylint: disable=E0401


def test_constructor():
    """Test the GATO constructor"""
    acct = GATO("Account name", AccountType.Income)
    assert isinstance(acct, GATO)


def test_get_name():
    """Test the GATO get_name method"""
    acct_name = "Account Name "
    acct_name += "".join(random_choices([chr(x) for x in range(32, 127)], k=8))
    acct = GATO(acct_name, AccountType.Income)
    assert acct.get_name() == acct_name


def test_set_name():
    """Test the GATO get_name method"""
    acct_name = "Account Name "
    acct_name += "".join(random_choices([chr(x) for x in range(32, 127)], k=8))
    acct = GATO("Wrong name", AccountType.Income)
    acct.set_name(acct_name)
    assert acct.get_name() == acct_name
    with raises(TypeError):
        acct.set_name(True)


def test_get_type():
    """Test the GATO get_type method"""
    acct = GATO("Account name", AccountType.Expense)
    assert acct.get_type() is AccountType.Expense


def test_set_type():
    """Test the GATO set_type method"""
    acct = GATO("Account name", AccountType.Expense)
    acct.set_type(AccountType.Income)
    assert acct.get_type() is AccountType.Income
    with raises(TypeError):
        acct.set_type(True)


def test_add_subelements_to():
    """Test the GATO add_subelements_to method"""
    # NOTE
    # This test could be handled a lot better: it currently hardcodes the
    # position of the elements in the XML (because it uses a string) where it
    # could rather create a similar XML document, canonicalize the two and
    # compare the canon forms.
    # Also, this test does not even try to handle namespaces. Instead, it
    # bypasses them by declaring to the parser that we are searching in *all
    # namespaces* (with `{*}`) before we use the namespace notation `act:...`.
    acct_name = "Account name"
    acct_type = AccountType.Expense
    acct = GATO(acct_name, acct_type)
    root_node = ElementTree.Element("root")
    root_guid = uuid4().hex
    acct.add_subelements_to(root_node, root_guid, False)

    acct_guid = root_node.find(".//{*}act:id").text
    valid_output = bytes("<root>"
                         '<gnc:account version="2.0.0">'
                         f"<act:name>{acct_name}</act:name>"
                         f'<act:id type="guid">{acct_guid}</act:id>'
                         f"<act:type>{acct_type.value()}</act:type>"
                         "<act:commodity>"
                         "<cmdty:space>CURRENCY</cmdty:space>"
                         "<cmdty:id>EUR</cmdty:id>"
                         "</act:commodity>"
                         "<act:commodity-scu>100</act:commodity-scu>"
                         f'<act:parent type="guid">{root_guid}</act:parent>'
                         "</gnc:account>"
                         "</root>", encoding="UTF-8")
    assert ElementTree.tostring(root_node) == valid_output


def test_set_slot():
    """Test the GATO set_slot method"""
    # NOTE
    # See test above.
    acct_name = "Account name"
    acct_type = AccountType.Expense
    acct = GATO(acct_name, acct_type)
    slot_name = "slot name"
    slot_value = "slot value"
    acct.set_slot(slot_name, slot_value)
    root_node = ElementTree.Element("root")
    root_guid = uuid4().hex
    acct.add_subelements_to(root_node, root_guid, False)

    acct_guid = root_node.find(".//{*}act:id").text
    valid_output = bytes("<root>"
                         '<gnc:account version="2.0.0">'
                         f"<act:name>{acct_name}</act:name>"
                         f'<act:id type="guid">{acct_guid}</act:id>'
                         f"<act:type>{acct_type.value()}</act:type>"
                         "<act:commodity>"
                         "<cmdty:space>CURRENCY</cmdty:space>"
                         "<cmdty:id>EUR</cmdty:id>"
                         "</act:commodity>"
                         "<act:commodity-scu>100</act:commodity-scu>"
                         "<act:slots>"
                         "<slot>"
                         f"<slot:key>{slot_name}</slot:key>"
                         f'<slot:value type="string">{slot_value}</slot:value>'
                         "</slot>"
                         "</act:slots>"
                         f'<act:parent type="guid">{root_guid}</act:parent>'
                         "</gnc:account>"
                         "</root>", encoding="UTF-8")
    assert ElementTree.tostring(root_node) == valid_output

    with raises(TypeError):
        acct.set_slot(True, None)

    with raises(AttributeError):
        acct.set_slot("hidden", "true")


def test_get_slot():
    """Test the GATO get_slot method"""
    acct = GATO("Account name", AccountType.Income)
    slot_name = "slot name"
    slot_value = "slot value"
    acct.set_slot(slot_name, slot_value)
    assert acct.get_slot(slot_name) == slot_value
    with raises(TypeError):
        acct.get_slot(True)


def test_set_notes():
    """Test the GATO set_notes method"""
    acct_name = "Account name"
    acct_type = AccountType.Expense
    acct_notes = "notes"
    acct = GATO(acct_name, acct_type)
    acct.set_notes(acct_notes)
    root_node = ElementTree.Element("root")
    root_guid = uuid4().hex
    acct.add_subelements_to(root_node, root_guid, False)

    acct_guid = root_node.find(".//{*}act:id").text
    valid_output = bytes("<root>"
                         '<gnc:account version="2.0.0">'
                         f"<act:name>{acct_name}</act:name>"
                         f'<act:id type="guid">{acct_guid}</act:id>'
                         f"<act:type>{acct_type.value()}</act:type>"
                         "<act:commodity>"
                         "<cmdty:space>CURRENCY</cmdty:space>"
                         "<cmdty:id>EUR</cmdty:id>"
                         "</act:commodity>"
                         "<act:commodity-scu>100</act:commodity-scu>"
                         "<act:slots>"
                         "<slot>"
                         f"<slot:key>notes</slot:key>"
                         f'<slot:value type="string">{acct_notes}</slot:value>'
                         "</slot>"
                         "</act:slots>"
                         f'<act:parent type="guid">{root_guid}</act:parent>'
                         "</gnc:account>"
                         "</root>", encoding="UTF-8")
    assert ElementTree.tostring(root_node) == valid_output


def test_get_notes():
    """Test the GATO get_notes method"""
    notes = "".join(random_choices([chr(x) for x in range(32, 127)], k=8))
    acct = GATO("Test account", AccountType.Income)
    acct.set_notes(notes)
    assert acct.get_notes() == notes


def test_get_tax_related():
    """Test the GATO get_tax_related method"""
    acct = GATO("Test account", AccountType.Income)
    assert acct.get_tax_related() is False


def test_get_hidden():
    """Test the GATO get_hidden method"""
    acct = GATO("Test account", AccountType.Income)
    assert acct.get_hidden() is False


def test_is_opening_balance():
    """Test the GATO is_opening_balance method"""
    acct = GATO("Test account", AccountType.Income)
    assert acct.is_opening_balance() is False


def test_set_account_color():
    """Test the GATO set_account_color method"""
    acct_name = "Test account"
    acct_type = AccountType.Income
    acct = GATO(acct_name, acct_type)
    acct.set_account_color(10, 20, 30)
    root_node = ElementTree.Element("root")
    root_guid = uuid4().hex
    acct.add_subelements_to(root_node, root_guid, False)

    acct_guid = root_node.find(".//{*}act:id").text
    valid_output = bytes("<root>"
                         '<gnc:account version="2.0.0">'
                         f"<act:name>{acct_name}</act:name>"
                         f'<act:id type="guid">{acct_guid}</act:id>'
                         f"<act:type>{acct_type.value()}</act:type>"
                         "<act:commodity>"
                         "<cmdty:space>CURRENCY</cmdty:space>"
                         "<cmdty:id>EUR</cmdty:id>"
                         "</act:commodity>"
                         "<act:commodity-scu>100</act:commodity-scu>"
                         "<act:slots>"
                         "<slot>"
                         f"<slot:key>color</slot:key>"
                         '<slot:value type="string">rgb(10,20,30)</slot:value>'
                         "</slot>"
                         "</act:slots>"
                         f'<act:parent type="guid">{root_guid}</act:parent>'
                         "</gnc:account>"
                         "</root>", encoding="UTF-8")
    assert ElementTree.tostring(root_node) == valid_output

    with raises(TypeError):
        acct.set_account_color('a', 0, 0)

    with raises(TypeError):
        acct.set_account_color(0, 'a', 0)

    with raises(TypeError):
        acct.set_account_color(0, 0, 'a')

    with raises(ValueError):
        acct.set_account_color(9513, 0, 0)

    with raises(ValueError):
        acct.set_account_color(0, 56478, 0)

    with raises(ValueError):
        acct.set_account_color(0, 0, 548694)


def test_get_account_color():
    """Test the GATO get_account_color method"""
    acct = GATO("Test account", AccountType.Income)
    assert acct.get_account_color() is None
    acct.set_account_color(10, 20, 30)
    assert acct.get_account_color() == (10, 20, 30)


def test_get_code():
    """Test the GATO get_code method"""
    acct_code = "code"
    acct_code += "".join(random_choices([chr(x) for x in range(32, 127)], k=8))
    acct = GATO("Account name", AccountType.Expense, acct_code)
    assert acct.get_code() is acct_code


def test_set_code():
    """Test the GATO set_code method"""
    # NOTE
    # See test above.
    acct_name = "Account name"
    acct_type = AccountType.Expense
    acct_code = "42"
    acct = GATO(acct_name, acct_type, acct_code)
    root_node = ElementTree.Element("root")
    root_guid = uuid4().hex
    acct.add_subelements_to(root_node, root_guid, False)

    acct_guid = root_node.find(".//{*}act:id").text
    valid_output = bytes("<root>"
                         '<gnc:account version="2.0.0">'
                         f"<act:name>{acct_name}</act:name>"
                         f"<act:code>{acct_code}</act:code>"
                         f'<act:id type="guid">{acct_guid}</act:id>'
                         f"<act:type>{acct_type.value()}</act:type>"
                         "<act:commodity>"
                         "<cmdty:space>CURRENCY</cmdty:space>"
                         "<cmdty:id>EUR</cmdty:id>"
                         "</act:commodity>"
                         "<act:commodity-scu>100</act:commodity-scu>"
                         f'<act:parent type="guid">{root_guid}</act:parent>'
                         "</gnc:account>"
                         "</root>", encoding="UTF-8")
    assert ElementTree.tostring(root_node) == valid_output

    acct_name = "Account name"
    acct_type = AccountType.Expense
    acct_code = "42"
    acct = GATO(acct_name, acct_type)
    acct.set_code(acct_code)
    root_node = ElementTree.Element("root")
    root_guid = uuid4().hex
    acct.add_subelements_to(root_node, root_guid, False)

    acct_guid = root_node.find(".//{*}act:id").text
    valid_output = bytes("<root>"
                         '<gnc:account version="2.0.0">'
                         f"<act:name>{acct_name}</act:name>"
                         f"<act:code>{acct_code}</act:code>"
                         f'<act:id type="guid">{acct_guid}</act:id>'
                         f"<act:type>{acct_type.value()}</act:type>"
                         "<act:commodity>"
                         "<cmdty:space>CURRENCY</cmdty:space>"
                         "<cmdty:id>EUR</cmdty:id>"
                         "</act:commodity>"
                         "<act:commodity-scu>100</act:commodity-scu>"
                         f'<act:parent type="guid">{root_guid}</act:parent>'
                         "</gnc:account>"
                         "</root>", encoding="UTF-8")
    assert ElementTree.tostring(root_node) == valid_output

    with raises(TypeError):
        acct.set_code(True)


def test_get_currency():
    """Test the GATO get_currency method"""
    currency = Currency.USD
    acct = GATO("Test account", AccountType.Income, "", currency)
    assert acct.get_currency() == currency


def test_set_currency():
    """Test the GATO set_currency method"""
    currency = Currency.USD
    acct = GATO("Test account", AccountType.Income, "", Currency.BSD)
    acct.set_currency(currency)
    assert acct.get_currency() == currency
    with raises(TypeError):
        acct.set_currency(True)


def test_set_description():
    """Test the GATO set_description method"""
    # NOTE
    # See test above.
    acct_name = "Account name"
    acct_type = AccountType.Expense
    acct_desc = "Account description"
    acct = GATO(acct_name, acct_type)
    acct.set_description(acct_desc)
    root_node = ElementTree.Element("root")
    root_guid = uuid4().hex
    acct.add_subelements_to(root_node, root_guid, False)

    acct_guid = root_node.find(".//{*}act:id").text
    valid_output = bytes("<root>"
                         '<gnc:account version="2.0.0">'
                         f"<act:name>{acct_name}</act:name>"
                         f'<act:id type="guid">{acct_guid}</act:id>'
                         f"<act:type>{acct_type.value()}</act:type>"
                         "<act:commodity>"
                         "<cmdty:space>CURRENCY</cmdty:space>"
                         "<cmdty:id>EUR</cmdty:id>"
                         "</act:commodity>"
                         "<act:commodity-scu>100</act:commodity-scu>"
                         f"<act:description>{acct_desc}</act:description>"
                         f'<act:parent type="guid">{root_guid}</act:parent>'
                         "</gnc:account>"
                         "</root>", encoding="UTF-8")
    assert ElementTree.tostring(root_node) == valid_output

    with raises(TypeError):
        acct.set_description(True)


def test_get_description():
    """Test the GATO get_description method"""
    description = "Test description"
    acct = GATO("Test account", AccountType.Income)
    assert acct.get_description() is None
    acct.set_description(description)
    assert acct.get_description() == description


def test_set_placeholder():
    """Test the GATO set_placeholder method"""
    # NOTE
    # See test above.
    acct_name = "Account name"
    acct_type = AccountType.Expense
    acct = GATO(acct_name, acct_type)
    acct.set_placeholder()
    root_node = ElementTree.Element("root")
    root_guid = uuid4().hex
    acct.add_subelements_to(root_node, root_guid, False)

    acct_guid = root_node.find(".//{*}act:id").text
    valid_output = bytes("<root>"
                         '<gnc:account version="2.0.0">'
                         f"<act:name>{acct_name}</act:name>"
                         f'<act:id type="guid">{acct_guid}</act:id>'
                         f"<act:type>{acct_type.value()}</act:type>"
                         "<act:commodity>"
                         "<cmdty:space>CURRENCY</cmdty:space>"
                         "<cmdty:id>EUR</cmdty:id>"
                         "</act:commodity>"
                         "<act:commodity-scu>100</act:commodity-scu>"
                         "<act:slots>"
                         "<slot>"
                         f"<slot:key>placeholder</slot:key>"
                         f'<slot:value type="string">true</slot:value>'
                         "</slot>"
                         "</act:slots>"
                         f'<act:parent type="guid">{root_guid}</act:parent>'
                         "</gnc:account>"
                         "</root>", encoding="UTF-8")
    assert ElementTree.tostring(root_node) == valid_output

    acct = GATO(acct_name, acct_type)
    acct.set_placeholder(True)
    root_node = ElementTree.Element("root")
    root_guid = uuid4().hex
    acct.add_subelements_to(root_node, root_guid, False)

    acct_guid = root_node.find(".//{*}act:id").text
    valid_output = bytes("<root>"
                         '<gnc:account version="2.0.0">'
                         f"<act:name>{acct_name}</act:name>"
                         f'<act:id type="guid">{acct_guid}</act:id>'
                         f"<act:type>{acct_type.value()}</act:type>"
                         "<act:commodity>"
                         "<cmdty:space>CURRENCY</cmdty:space>"
                         "<cmdty:id>EUR</cmdty:id>"
                         "</act:commodity>"
                         "<act:commodity-scu>100</act:commodity-scu>"
                         "<act:slots>"
                         "<slot>"
                         f"<slot:key>placeholder</slot:key>"
                         f'<slot:value type="string">true</slot:value>'
                         "</slot>"
                         "</act:slots>"
                         f'<act:parent type="guid">{root_guid}</act:parent>'
                         "</gnc:account>"
                         "</root>", encoding="UTF-8")
    assert ElementTree.tostring(root_node) == valid_output

    acct = GATO(acct_name, acct_type)
    acct.set_placeholder(False)
    root_node = ElementTree.Element("root")
    root_guid = uuid4().hex
    acct.add_subelements_to(root_node, root_guid, False)

    acct_guid = root_node.find(".//{*}act:id").text
    valid_output = bytes("<root>"
                         '<gnc:account version="2.0.0">'
                         f"<act:name>{acct_name}</act:name>"
                         f'<act:id type="guid">{acct_guid}</act:id>'
                         f"<act:type>{acct_type.value()}</act:type>"
                         "<act:commodity>"
                         "<cmdty:space>CURRENCY</cmdty:space>"
                         "<cmdty:id>EUR</cmdty:id>"
                         "</act:commodity>"
                         "<act:commodity-scu>100</act:commodity-scu>"
                         "<act:slots>"
                         "<slot>"
                         f"<slot:key>placeholder</slot:key>"
                         f'<slot:value type="string">false</slot:value>'
                         "</slot>"
                         "</act:slots>"
                         f'<act:parent type="guid">{root_guid}</act:parent>'
                         "</gnc:account>"
                         "</root>", encoding="UTF-8")
    assert ElementTree.tostring(root_node) == valid_output


def test_get_placeholder():
    """Test the GATO get_placeholder method"""
    acct = GATO("Test account", AccountType.Income)
    assert acct.get_placeholder() is False


def test_subaccounts():
    """Test the GATO subaccounts"""
    # NOTE
    # See test above.
    acct_name = "Account name"
    acct_type = AccountType.Expense
    sub_accts = ["Sub1", "Sub2"]
    acct = GATO(acct_name, acct_type)
    for sub_acct in sub_accts:
        acct.add_subaccount(GATO(sub_acct, acct_type))
    root_node = ElementTree.Element("root")
    root_guid = uuid4().hex
    acct.add_subelements_to(root_node, root_guid, False)

    acct_guid, *sub_guids = [x.text for x in root_node.findall(".//{*}act:id")]
    valid_output = bytes("<root>"
                         '<gnc:account version="2.0.0">'
                         f"<act:name>{acct_name}</act:name>"
                         f'<act:id type="guid">{acct_guid}</act:id>'
                         f"<act:type>{acct_type.value()}</act:type>"
                         "<act:commodity>"
                         "<cmdty:space>CURRENCY</cmdty:space>"
                         "<cmdty:id>EUR</cmdty:id>"
                         "</act:commodity>"
                         "<act:commodity-scu>100</act:commodity-scu>"
                         f'<act:parent type="guid">{root_guid}</act:parent>'
                         "</gnc:account>", encoding="UTF-8")
    for idx, sub_acct in enumerate(sub_accts):
        valid_output += bytes('<gnc:account version="2.0.0">'
                              f"<act:name>{sub_acct}</act:name>"
                              f'<act:id type="guid">{sub_guids[idx]}</act:id>'
                              "<act:type>EXPENSE</act:type>"
                              "<act:commodity>"
                              "<cmdty:space>CURRENCY</cmdty:space>"
                              "<cmdty:id>EUR</cmdty:id>"
                              "</act:commodity>"
                              "<act:commodity-scu>100</act:commodity-scu>"
                              '<act:parent type="guid">'
                              f"{acct_guid}</act:parent>"
                              "</gnc:account>", encoding="UTF-8")
    valid_output += bytes("</root>", encoding="UTF-8")
    assert ElementTree.tostring(root_node) == valid_output
