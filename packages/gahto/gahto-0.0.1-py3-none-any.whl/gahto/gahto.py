"""GNUCash Account Hierarchy Template Object"""

# NOTE
#
# This file has been validated by pylint, flake8, and mypy. The code within is
# therefore modified to accommodate the idiosyncrasies of those tools.
# Such modifications include the length of lines (< 80 characters), which is
# actually desirable (it brings the text past the middle of the screen on
# monitors with resolutions of 1366x768 or lower-and if you think this is
# "preposterous", check your privileges...).

# TODO  # pylint: disable=W0511
#
# - Properly implement all supported slot types (not just string)
# - Implement XML namespaces properly (and not via string output)
# - Implement parsing XML (gnucash-xea) files

# Stdlib imports
from typing import Any
from uuid import uuid4
from xml.etree import ElementTree as ET

# Package imports
from iso_4217 import Currency  # type: ignore [import] # pylint: disable=E0401

# The default currency for this package
DEFAULT_CURRENCY = Currency.EUR

# For now, only the string type is implemented. I am not sure how to implement
# the rest, but for further information, see here:
# https://code.gnucash.org/docs/STABLE/structKvpValueImpl.html#af35395e9846fc97d6daf29343fb3b978
XML_TYPES_NAMES: dict[type, str] = {
    str: "string",
}


class MetaAccountType(type):
    """Meta class for AccountType - Only for having getattr and setattr work on
    class variables."""
    def __getattr__(cls: "MetaAccountType", name: str) -> Any:
        return cls.__getattr__(cls, name)  # type: ignore[call-arg,arg-type]

    def __setattr__(cls: "MetaAccountType", name: str, val: Any) -> None:
        type.__setattr__(cls, name, val)


class AccountType(metaclass=MetaAccountType):
    """GATO Account Type

    The account types are from
    https://gnucash.org/docs/v5/C/gnucash-manual//acct-types.html

    The page (as of Thu 07 Aug 2025) is outdated, and so, the "Currency" type
    has been gone for a while, while the "Trading" type is now available (but
    isn't documented yet). The information contained in this class has
    therefore been obtained empirically.
    """
    __names = {
        "PAYABLE": "AccountsPayable",
        "RECEIVABLE": "AccountsReceivable",
        "ASSET": "Asset",
        "BANK": "Bank",
        "CASH": "Cash",
        "CREDIT": "CreditCard",
        "EQUITY": "Equity",
        "EXPENSE": "Expense",
        "INCOME": "Income",
        "LIABILITY": "Liability",
        "MUTUAL": "MutualFund",
        "STOCK": "Stock",
        "TRADING": "Trading",
    }
    __labels = {
        "PAYABLE": "Accounts Payable",
        "RECEIVABLE": "Accounts Receivable",
        "ASSET": "Asset",
        "BANK": "Bank",
        "CASH": "Cash",
        "CREDIT": "Credit Card",
        "EQUITY": "Equity",
        "EXPENSE": "Expense",
        "INCOME": "Income",
        "LIABILITY": "Liability",
        "MUTUAL": "Mutual Fund",
        "STOCK": "Stock",
        "TRADING": "Trading",
    }
    __default_allowed_list = ["PAYABLE", "RECEIVABLE", "ASSET", "BANK", "CASH",
                              "CREDIT", "LIABILITY", "MUTUAL", "STOCK"]
    __allowed_child_account_types = {
        "PAYABLE":    __default_allowed_list,
        "RECEIVABLE": __default_allowed_list,
        "ASSET":      __default_allowed_list,
        "BANK":       __default_allowed_list,
        "CASH":       __default_allowed_list,
        "CREDIT":     __default_allowed_list,
        "EQUITY":     ["EQUITY"],
        "EXPENSE":    ["EXPENSE", "INCOME"],
        "INCOME":     ["EXPENSE", "INCOME"],
        "LIABILITY":  __default_allowed_list,
        "MUTUAL":     __default_allowed_list,
        "STOCK":      __default_allowed_list,
        "TRADING":    ["TRADING"],
    }
    # NOTE possibly merge all the data above, in one big dict or list of dict,
    #      etc. Use what makes sense.

    def __init__(self: "AccountType", typename: str) -> None:
        kname, vname = next((x for x in self.__names.items() if typename in x),
                            ("", ""))
        if kname == vname == "":
            raise ValueError(f"{self.__class__.__name__} cannot take the value"
                             f" '{typename}'.")
        self.__value = kname
        self.__label = self.__labels[kname]
        self.__name = vname

    def __getattr__(self: "AccountType", name: str) -> Any:
        kname, vname = next((x for x in self.__names.items() if name in x),
                            ("", ""))
        if kname == vname == "":
            values_list = ", ".join(x for y in self.__names.items() for x in y)
            raise ValueError(f"Account type '{name}' not in: {values_list}.")
        obj = AccountType(name)
        setattr(self, kname, obj)
        setattr(self, vname, obj)
        return getattr(self, name)

    def __repr__(self: "AccountType") -> str:
        return f"<{self.__module__}.{self.__class__.__qualname__}" \
               f"({self.__name}) object at {hex(id(self))}>"

    def label(self: "AccountType") -> str:
        """Gets the human readable label of the type"""
        return self.__label

    def value(self: "AccountType") -> str:
        """Gets the value (for the XML file) of the type"""
        return self.__value

    def type_name(self: "AccountType") -> str:
        """Gets the type name"""
        return self.__name

    def is_valid_child_of(self: "AccountType", parent: "AccountType") -> bool:
        """Checks if an account type is a valid child of another"""
        return self.value() \
            in self.__allowed_child_account_types[parent.value()]

    def is_valid_parent_of(self: "AccountType", child: "AccountType") -> bool:
        """Checks if an account type is a valid parent of another"""
        return child.value() \
            in self.__allowed_child_account_types[self.value()]


class GATO:
    """GNUCash Account Template Object main class"""

    def __init__(self: "GATO", name: str, acct_type: AccountType,
                 code: str | None = None,
                 currency: Currency = DEFAULT_CURRENCY) -> None:
        self.set_name(name)
        self.set_type(acct_type)
        self.__code: str | None
        if code is not None:
            self.set_code(code)
        else:
            self.__code = None
        self.set_currency(currency)
        self.__description: str | None = None
        # Generate a (GNUCash compatible) GUID for the account
        self.__uuid = uuid4().hex
        self.__slots: dict[str, Any] = {}
        self.__subaccounts: list[GATO] = []

    def get_name(self: "GATO") -> str:
        """Gets the name of the GATO object"""
        return self.__name

    def set_name(self: "GATO", name: str):
        """Sets the name of the GATO object"""
        if not isinstance(name, str):
            raise TypeError(f"{name} isn't a string")
        self.__name = name

    def get_type(self: "GATO") -> AccountType:
        """Gets the type of the GATO object"""
        return self.__type

    def set_type(self: "GATO", acct_type: AccountType) -> None:
        """Sets the type of the GATO object"""
        if not isinstance(acct_type, AccountType):
            raise TypeError(f"Account type {acct_type} isn't of the type "
                            f"{AccountType.__name__}")
        self.__type = acct_type

    def get_code(self: "GATO") -> str | None:
        """Gets the code of a GATO object"""
        return self.__code

    def set_code(self: "GATO", code: str):
        """Sets the code of the GATO object"""
        if not isinstance(code, str):
            raise TypeError(f"{code} isn't a string")
        self.__code = code

    def get_currency(self: "GATO") -> Currency:
        """Gets the currency for the GATO object"""
        return self.__currency

    def set_currency(self: "GATO", currency: Currency) -> None:
        """Sets the currency for the GATO object"""
        if not isinstance(currency, Currency):
            raise TypeError(f"{currency} isn't of type {type(Currency)}")
        self.__currency = currency

    def get_description(self: "GATO") -> str | None:
        """Gets the description of the GATO object"""
        return self.__description

    def set_description(self: "GATO", description: str):
        """Sets the description of the GATO object"""
        if not isinstance(description, str):
            raise TypeError(f"{description} isn't a string")
        self.__description = description

    def get_slot(self: "GATO", key: str) -> Any:
        """Gets a slot from the GATO object"""
        if not isinstance(key, str):
            raise TypeError(f"key {key} isn't a string")
        return self.__slots.get(key, None)

    def set_slot(self: "GATO", key: str, value: Any) -> None:
        """Sets a slot to the GATO object"""
        if not isinstance(key, str):
            raise TypeError(f"key {key} isn't a string")
        # Blacklisted values are set elsewhere (or not at all)
        blacklisted = ['tax-related', 'hidden', 'color', 'equity-type',
                       'placeholder', 'notes']
        if key in blacklisted:
            raise AttributeError(f"Slot '{key}' is set via a dedicated method")
        self.__slots[key] = value

    def get_notes(self: "GATO") -> str:
        """Gets the notes from the GATO object"""
        return self.__slots.get("notes", "")

    def set_notes(self: "GATO", notes: str) -> None:
        """Adds notes to the GATO object"""
        self.__slots["notes"] = notes

    def get_tax_related(self: "GATO") -> bool:
        """Gets the tax-related status from the GATO object"""
        return self.__slots.get("tax-related", "").lower().strip() == "true"

    def get_hidden(self: "GATO") -> bool:
        """Gets the hidden status of the GATO object"""
        return self.__slots.get("hidden", "").lower().strip() == "true"

    def get_placeholder(self: "GATO") -> bool:
        """Gets the state of the "placeholder" value"""
        return self.__slots.get("placeholder", "").lower().strip() == "true"

    def set_placeholder(self: "GATO", state: bool = True) -> None:
        """Sets the state of the "placeholder" value"""
        self.__slots["placeholder"] = "true" if state else "false"

    def is_opening_balance(self: "GATO") -> bool:
        """Gets if the account has an opening balance"""
        return self.__slots.get("equity-type", "").lower().strip() \
            == "opening-balance"

    def get_account_color(self: "GATO") -> tuple[int, int, int] | None:
        """Gets the color of the GATO object"""
        rgbcolor = self.__slots.get("color", None)
        if rgbcolor is None:
            return None
        if rgbcolor[0:4].lower() != "rgb(" or rgbcolor[-1] != ")":
            raise ValueError(f"RGB color {rgbcolor} not in the form "
                             "rgb(..., ..., ...)")
        try:
            _r, _g, _b = (x.strip() for x in rgbcolor[4:-1].split(","))
        except ValueError as ex:
            raise ValueError(f"RGB color {rgbcolor} not in the form "
                             "rgb(..., ..., ...)") from ex
        return (int(_r), int(_g), int(_b))

    def set_account_color(self: "GATO", _r: int, _g: int, _b: int) -> None:
        """Sets the color of the GATO object"""
        if not isinstance(_r, int):
            raise TypeError(f"Value {_r} for the color red has to be an int")
        if not isinstance(_g, int):
            raise TypeError(f"Value {_g} for the color green has to be an int")
        if not isinstance(_b, int):
            raise TypeError(f"Value {_b} for the color blue has to be an int")
        if _r < 0 or _r > 255:
            raise ValueError(f"Value {_r} for the color red isn't valid.")
        if _g < 0 or _g > 255:
            raise ValueError(f"Value {_g} for the color green isn't valid.")
        if _b < 0 or _b > 255:
            raise ValueError(f"Value {_b} for the color blue isn't valid.")
        self.__slots["color"] = f"rgb({_r},{_g},{_b})"

    def add_subaccount(self: "GATO", child: "GATO") -> None:
        """Add a GATO as a child to this GATO"""
        if self.__type.is_valid_parent_of(child.get_type()):
            self.__subaccounts.append(child)

    def add_subelements_to(self: "GATO", parent: ET.Element, parent_guid: str,
                           for_template: bool) -> None:
        """Add ElementTree SubElement(s) of this account to the parent
        element"""
        acct = ET.SubElement(parent, "gnc:account", attrib={
                "version": "2.0.0"
            })
        ET.SubElement(acct, "act:name").text = self.__name
        if self.__code is not None:
            ET.SubElement(acct, "act:code").text = self.__code
        ET.SubElement(acct, "act:id", attrib={
                "type": "new" if for_template else "guid"
            }).text = self.__uuid
        ET.SubElement(acct, "act:type").text = self.__type.value()
        commodity_node = ET.SubElement(acct, "act:commodity")
        ET.SubElement(commodity_node, "cmdty:space").text = "CURRENCY"
        ET.SubElement(commodity_node, "cmdty:id").text = self.__currency.name
        ET.SubElement(acct, "act:commodity-scu").text = str(int(
            self.__currency.subunit.from_(self.__currency.unit).magnitude))
        if self.__description is not None:
            ET.SubElement(acct, "act:description").text = self.__description
        if self.__slots:
            slots_node = ET.SubElement(acct, "act:slots")
            for key, value in self.__slots.items():
                slot_node = ET.SubElement(slots_node, "slot")
                ET.SubElement(slot_node, "slot:key").text = key
                ET.SubElement(slot_node, "slot:value", attrib={
                        "type": XML_TYPES_NAMES[type(value)]
                    }).text = value
        ET.SubElement(acct, "act:parent", attrib={
                "type": "new" if for_template else "guid"
            }).text = parent_guid

        for account in self.__subaccounts:
            account.add_subelements_to(parent, self.__uuid, for_template)


class GAHTO:
    """GNUCash Hierarchy Account Template Object main class"""
    def __init__(self: "GAHTO", title: str | None = None,
                 currency: Currency = DEFAULT_CURRENCY) -> None:
        self.__top_level_accounts: list[GATO] = []
        self.__title = title
        self.__short_description: str | None = None
        self.__long_description: str | None = None
        self.__currency = currency
        self.__exclude_from_select_all: bool = True
        # Generate a (GNUCash compatible) GUID for the Root Account
        self.__root_acct_guid = uuid4().hex

    def set_title(self: "GAHTO", title: str) -> None:
        """Sets the title of the GAHTO object"""
        self.__title = title

    def set_description(self: "GAHTO", short: str | None,
                        long: str | None = None) -> None:
        """Sets the description(s) of the GAHTO object"""
        if short is not None:
            self.__short_description = short
        if long is not None:
            self.__long_description = long

    def set_currency(self: "GAHTO", currency: Currency) -> None:
        """Sets the currency of the GAHTO object"""
        if not isinstance(currency, Currency):
            raise TypeError(f"Currency {currency} is of type {type(currency)}."
                            f" Expected type is {type(Currency)}.")
        self.__currency = currency

    def exclude_from_select_all(self: "GAHTO") -> None:
        """Sets the "exclude_from_select_all" value to false"""
        self.__exclude_from_select_all = True

    def include_in_select_all(self: "GAHTO") -> None:
        """Sets the "exclude_from_select_all" value to false"""
        self.__exclude_from_select_all = False

    def add_account(self: "GAHTO", account: GATO) -> None:
        """Adds a GATO account to the GAHTO object"""
        self.__top_level_accounts.append(account)

    def export(self: "GAHTO", path: str, to_template: bool = True) -> None:
        """Exports the GAHTO object to an XML file at path"""

        # Define the XML root element
        root_node = ET.Element("gnc-account-example")
        root_node.set("xmlns", "http://www.gnucash.org/XML/")
        root_node.set("xmlns:act", "http://www.gnucash.org/XML/act")
        root_node.set("xmlns:addr", "http://www.gnucash.org/XML/addr")
        root_node.set("xmlns:bgt", "http://www.gnucash.org/XML/bgt")
        root_node.set("xmlns:billterm", "http://www.gnucash.org/XML/billterm")
        root_node.set("xmlns:book", "http://www.gnucash.org/XML/book")
        root_node.set("xmlns:bt-days", "http://www.gnucash.org/XML/bt-days")
        root_node.set("xmlns:bt-prox", "http://www.gnucash.org/XML/bt-prox")
        root_node.set("xmlns:cd", "http://www.gnucash.org/XML/cd")
        root_node.set("xmlns:cmdty", "http://www.gnucash.org/XML/cmdty")
        root_node.set("xmlns:cust", "http://www.gnucash.org/XML/cust")
        root_node.set("xmlns:employee", "http://www.gnucash.org/XML/employee")
        root_node.set("xmlns:entry", "http://www.gnucash.org/XML/entry")
        root_node.set("xmlns:fs", "http://www.gnucash.org/XML/fs")
        root_node.set("xmlns:gnc", "http://www.gnucash.org/XML/gnc")
        root_node.set("xmlns:gnc-act", "http://www.gnucash.org/XML/gnc-act")
        root_node.set("xmlns:invoice", "http://www.gnucash.org/XML/invoice")
        root_node.set("xmlns:job", "http://www.gnucash.org/XML/job")
        root_node.set("xmlns:lot", "http://www.gnucash.org/XML/lot")
        root_node.set("xmlns:order", "http://www.gnucash.org/XML/order")
        root_node.set("xmlns:owner", "http://www.gnucash.org/XML/owner")
        root_node.set("xmlns:price", "http://www.gnucash.org/XML/price")
        root_node.set("xmlns:recurrence",
                      "http://www.gnucash.org/XML/recurrence")
        root_node.set("xmlns:slot", "http://www.gnucash.org/XML/slot")
        root_node.set("xmlns:split", "http://www.gnucash.org/XML/split")
        root_node.set("xmlns:sx", "http://www.gnucash.org/XML/sx")
        root_node.set("xmlns:taxtable", "http://www.gnucash.org/XML/taxtable")
        root_node.set("xmlns:trn", "http://www.gnucash.org/XML/trn")
        root_node.set("xmlns:ts", "http://www.gnucash.org/XML/ts")
        root_node.set("xmlns:tte", "http://www.gnucash.org/XML/tte")
        root_node.set("xmlns:vendor", "http://www.gnucash.org/XML/vendor")

        # Define all the root element direct children
        ET.SubElement(root_node, "gnc-act:title").text = \
            self.__title if self.__title is not None else "<No title>"

        ET.SubElement(root_node, "gnc-act:short-description").text = \
            self.__short_description if self.__short_description is not None \
            else "<No description>"

        ET.SubElement(root_node, "gnc-act:long-description").text = \
            self.__long_description if self.__long_description is not None \
            else \
            """<No description was provided during the creation of this Account
            Hierarchy Template. Please report the issue to whoever created it>
            """

        ET.SubElement(root_node, "gnc-act:exclude-from-select-all").text = \
            str(int(self.__exclude_from_select_all))

        # Define the Root Account (GNUCash concept)
        root_acct = ET.SubElement(root_node, "gnc:account", attrib={
                "version": "2.0.0"
            })

        # Define all the Root Account children
        ET.SubElement(root_acct, "act:name").text = "Root Account"

        ET.SubElement(root_acct, "act:id", attrib={
                "type": "new" if to_template else "guid"
            }).text = self.__root_acct_guid

        ET.SubElement(root_acct, "act:type").text = "ROOT"

        commodity_node = ET.SubElement(root_acct, "act:commodity")
        ET.SubElement(commodity_node, "cmdty:space").text = "CURRENCY"
        ET.SubElement(commodity_node, "cmdty:id").text = self.__currency.name

        ET.SubElement(root_acct, "act:commodity-scu").text = str(int(
            self.__currency.subunit.from_(self.__currency.unit).magnitude))

        for account in self.__top_level_accounts:
            account.add_subelements_to(root_node, self.__root_acct_guid,
                                       to_template)

        tree = ET.ElementTree(root_node)
        ET.indent(tree)
        tree.write(path, xml_declaration=True, encoding="Unicode")
