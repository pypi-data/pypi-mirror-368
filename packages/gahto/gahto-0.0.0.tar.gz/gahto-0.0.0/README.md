GNUCash Account Hierarchy Template Object
=========================================

GAHTO is a small Python module for creating GNUCash Account Hierarchy Template
Objects natively in python, and eventually exporting them in XML as
`.gnucash-xea` files.

Usage
-----

```python
from gahto.gahto import GAHTO
from gahto.gahto import GATO
from gahto.gahto import AccountType

EL = GAHTO("Title")
EL.set_description("Short description", "Longer description")

expenses_acct = GATO("Expenses", AccountType.Expense)
expenses_acct.set_description("Expenses")
expenses_acct.set_placeholder(True)
EL.add_account(expenses_acct)

childcare_acct = GATO("Childcare", AccountType.Expense)
childcare_acct.set_description("Childcare")
expenses_acct.add_subaccount(childcare_acct)

EL.export("example-account-hierarchy.gnucash-xea")
```

Run tests
---------

With [`python-coverage`](https://github.com/nedbat/coveragepy) and
[`pytest`](https://pytest.org/) installed, run:

```sh
$ python3-coverage run -m pytest
$ python3-coverage html
$ xdg-open htmlcov/index.html
```

Alternatively, you can replace the last two commands with:

```sh
$ python3-coverage report
```
