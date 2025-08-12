# LabelPrint
### Automated barcode label generation and printing in Python

*Note: This package only works on Windows at the moment. With some minor rework, it could work on Linux too, that's just not a priority for my purposes at the moment.*

# Creating Labels

*(More help coming soon)*

# Testing Labels

There are two ways to test your label layouts. You can write a simple Python script to generate a label, or you can add some code to your HTML file to import the script and create a preview when opened in your browser.

*(More help coming soon)*
<!--
## Python Method

TBD

## HTML Method

TBD
-->

# Printing Labels

Printing your label with labelprint is easy! Simply call `label.printPDF`.

*(More help coming soon)*
<!--
Here's a full example:
```
TBD
```
-->

# Classes & Methods

## label.py
- `make(htmlFile: str[, outFile: str|BinaryIO], data: dict) -> None|bytes`\
	If `outFile` is a BinaryIO object, the PDF is written into it.\
	If `outFile` is None, raw PDF bytes are returned.
- `getPrinters() -> list[PrinterInfo]`
- `printPDF(fileName: str, ptrName: str[, printOpts: dict]) -> None`

### Printer Info
- `pPrinterName: str` Device name (give this to printPDF)
- `Offline: bool` Whether the printer is offline
- [See MSDN for PRINTER_INFO_2 structure](https://learn.microsoft.com/en-us/windows/win32/printdocs/printer-info-2)

### Print Options
| Name        | Type | Description               | Default        |
| ----------- | ---- | ------------------------- | -------------- |
| width       | int  | Width of page in inches   | HTML page size |
| length      | int  | Length of page in inches  | HTML page size |
| size        | int  | Standard paper size code  | Set by printer |
| orientation | str  | 'portrait' or 'landscape' | Set by printer |
| dpi         | int  | Print quality in DPI      | Set by printer |
| dpiX        | int  | DPI for X axis only       | Set by printer |
| dpiY        | int  | DPI for Y axis only       | Set by printer |
| color       | bool | Enable color printing     | True           |
| scale       | int  | Scale factor in percent   | 100            |
| copies      | int  | Number of copies          | 1              |

## web.py
- `Options: dict`
- `startDriver() -> ChromiumDriver` Start webdriver or return current instance.
- `stopDriver(force=False)` Shutdown webdriver in background after `Options.timeout`, or immediately if `force` is True.
- `getDriver() -> ChromiumDriver|None` Get global webdriver instance.
- `get(uri: str, timeout: float)` Get `uri` or raise TimeoutError if it can't be retrieved after `timeout` secs.

### Global Options
| Name     | Type        | Description               | Default |
| -------- | ----------- | ------------------------- | ------- |
| timeout  | float       | Secs to run in background | 120     |
| engine   | str         | Name of browser to use    | Edge    |
| opts     | BaseOptions | Custom webdriver options  | None    |
| headless | bool        | Run browser as headless   | True    |
| silent   | bool        | Don't print any debug     | False   |