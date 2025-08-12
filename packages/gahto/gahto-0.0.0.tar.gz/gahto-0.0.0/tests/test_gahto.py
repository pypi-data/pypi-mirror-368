"""Tests for the GAHTO module"""

from xml.etree import ElementTree

from iso_4217 import Currency  # type: ignore [import] # pylint: disable=E0401
from pytest import raises

from gahto.gahto import GAHTO  # pylint: disable=E0401
from gahto.gahto import GATO  # pylint: disable=E0401
from gahto.gahto import AccountType  # pylint: disable=E0401


def test_constructor():
    """Test the GAHTO constructor"""
    _el = GAHTO()
    assert isinstance(_el, GAHTO)


def test_export(tmpdir):
    """Test the GAHTO export method"""
    # NOTE
    # This code isn't complete: ElementTree.parse() isn't parsing the
    # namespaces properly. This won't be implemented before the namespaces are
    # handled properly in the main code. For now, this test checks that the
    # generated XML is valid (for the parser), nothing more.
    # In addition, the xml version and encoding declaration isn't trivial to
    # assert, so this needs extra work too.
    _el = GAHTO()
    _fh = tmpdir.join("test.gnucash-xea")
    _el.export(_fh.strpath)
    xml = ElementTree.parse(_fh.strpath)
    assert isinstance(xml, ElementTree.ElementTree)


def test_add_account(tmpdir):
    """Test the GAHTO add_account method"""
    # NOTE
    # See above
    _el = GAHTO()
    acct_name = "Test account"
    acct_type = AccountType.Income
    _el.add_account(GATO(acct_name, acct_type))
    _fh = tmpdir.join("test.gnucash-xea")
    _el.export(_fh.strpath)
    xml = ElementTree.parse(_fh.strpath)
    acct_tag = ".//{http://www.gnucash.org/XML/gnc}account"
    _, el_acct, *_ = xml.findall(acct_tag)
    assert el_acct.find(".//{http://www.gnucash.org/XML/act}name").text \
        == acct_name
    assert el_acct.find(".//{http://www.gnucash.org/XML/act}type").text \
        == acct_type.value()
    assert isinstance(xml, ElementTree.ElementTree)


def test_set_title(tmpdir):
    """Test the GAHTO set_title method"""
    # NOTE
    # See above
    _el = GAHTO()
    ah_title = "Account Hierarchy Title"
    _el.set_title(ah_title)
    _fh = tmpdir.join("test.gnucash-xea")
    _el.export(_fh.strpath)
    xml = ElementTree.parse(_fh.strpath)
    assert xml.find(".//{http://www.gnucash.org/XML/gnc-act}title").text \
        == ah_title
    assert isinstance(xml, ElementTree.ElementTree)


def test_set_description(tmpdir):
    """Test the GAHTO set_description method"""
    # NOTE
    # See above
    _el = GAHTO()
    ah_sdesc = "short"
    ah_ldesc = "Longer description with more text"
    _el.set_description(ah_sdesc, ah_ldesc)
    _fh = tmpdir.join("test.gnucash-xea")
    _el.export(_fh.strpath)
    xml = ElementTree.parse(_fh.strpath)
    sdesc_tag = ".//{http://www.gnucash.org/XML/gnc-act}short-description"
    ldesc_tag = ".//{http://www.gnucash.org/XML/gnc-act}long-description"
    assert xml.find(sdesc_tag).text == ah_sdesc
    assert xml.find(ldesc_tag).text == ah_ldesc
    assert isinstance(xml, ElementTree.ElementTree)


def test_set_currency(tmpdir):
    """Test the GAHTO set_currency method"""
    # NOTE
    # See above
    _el = GAHTO()
    with raises(TypeError):
        _el.set_currency(None)
    currency = Currency.BSD
    _el.set_currency(currency)
    _fh = tmpdir.join("test.gnucash-xea")
    _el.export(_fh.strpath)
    xml = ElementTree.parse(_fh.strpath)
    currency_id_tag = ".//{http://www.gnucash.org/XML/cmdty}id"
    assert xml.find(currency_id_tag).text == currency.name
    assert isinstance(xml, ElementTree.ElementTree)


def test_exclude_from_select_all(tmpdir):
    """Test the GAHTO exclude_from_select_all method"""
    # NOTE
    # See above
    _el = GAHTO()
    _el.exclude_from_select_all()
    _fh = tmpdir.join("test.gnucash-xea")
    _el.export(_fh.strpath)
    xml = ElementTree.parse(_fh.strpath)
    efsa_tag = ".//{http://www.gnucash.org/XML/gnc-act}exclude-from-select-all"
    assert xml.find(efsa_tag).text == '1'
    assert isinstance(xml, ElementTree.ElementTree)


def test_include_in_select_all(tmpdir):
    """Test the GAHTO include_in_select_all method"""
    # NOTE
    # See above
    _el = GAHTO()
    _el.include_in_select_all()
    _fh = tmpdir.join("test.gnucash-xea")
    _el.export(_fh.strpath)
    xml = ElementTree.parse(_fh.strpath)
    efsa_tag = ".//{http://www.gnucash.org/XML/gnc-act}exclude-from-select-all"
    assert xml.find(efsa_tag).text == '0'
    assert isinstance(xml, ElementTree.ElementTree)
