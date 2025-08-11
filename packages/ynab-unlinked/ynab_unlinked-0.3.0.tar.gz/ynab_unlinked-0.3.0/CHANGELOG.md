# Release notes

Welcome to the official ledger for `ynab-unlinked`! Just like you meticulously track your transactions, we keep a detailed account of every change we make to the project. Here you'll find a transparent record of new features hitting the market, bugs we've written off, and all the behind-the-scenes investments in our codebase.

To help us keep our books in order, these release notes are automatically generated using the wonderful [Towncrier](https://github.com/twisted/towncrier).

<!-- towncrier release notes start -->

## ynab-unlinked 0.3.0 (2025-08-10)

### Bugs Squashed, Peace Restored
* Fix XLS files in Sabadell when pending transactions where present. Sabadell can also now identify file type automatically.

## ynab-unlinked 0.2.1 (2025-08-10)

### Bugs Squashed, Peace Restored
* Fix an issue by which Sabadell entity was not properly ignoring pending transactions in txt format
* Fix issue with Cobee entity causing transactions with 0 euros showing as transactions to import

## ynab-unlinked 0.2.0 (2025-07-26)

### Polished Until It Shines
* Improved how the reconcile command works. Now it launches a Textual app to more easily review all transactions to reconcile.

## ynab-unlinked 0.1.0 (2025-07-15)

### Fresh Out of the Feature Oven
* [[#14](https://github.com/AAraKKe/ynab-unlinked/issues/14)] Add option to the load command that prompts to select an account to import to
* [[#18](https://github.com/AAraKKe/ynab-unlinked/issues/18)] Add support for XLS parsing to Sabadell entity
* Add support for XLSX files to BBVA improving how to handle multiple files types
* [[#1](https://github.com/AAraKKe/ynab-unlinked/issues/1)] Yul Config can now be versioned and migrated from older to newer versions.

### Polished Until It Shines
* Bring match days threshold to the same value as YNAB has it
* [[#9](https://github.com/AAraKKe/ynab-unlinked/issues/9)] Improve amount formatting based on the settings in the used YNAB budget
* [[#1](https://github.com/AAraKKe/ynab-unlinked/issues/1)] Improve display handling by centralizing styles in the display module and moving complex display logic to utils
* Instead of avoid loading transactions from the last time the tool was run, we are now tryingto match transactions with YNAB transactions that are a number of days prior to the earliest transaction in the import file. This is configurable through the `--buffer` option in the load command.
* Make the menu to select accounts to reconcile interactive. This type of menu will be used whenever the user needs to selet an option

### Bugs Squashed, Peace Restored
* [[#11](https://github.com/AAraKKe/ynab-unlinked/issues/11)] Fix in Cobee entity that prevents it from importing accumulations lines
* [[#20](https://github.com/AAraKKe/ynab-unlinked/issues/20)] Sabadell import ignores cash withdrawals. These appear in the linked bank acccount

## ynab-unlinked 0.0.3 (2025-05-18)

### Fresh Out of the Feature Oven
* Add new reconcile command. Run `yul reconcile` and reconcile all your accounts in one go.

### Bugs Squashed, Peace Restored
* Fix reconcile command that would break when selecting all accounts

### For the Builders: Dev Experience Upgrades
* [[#4](https://github.com/AAraKKe/ynab-unlinked/issues/4)] Add towncrier support. This includes configuration, hatch environment and scripts.
* [[#5](https://github.com/AAraKKe/ynab-unlinked/issues/5)] Add GitHub workflow to validate PRs. This includes: format checkts, linter, type checker and towncrier validation
