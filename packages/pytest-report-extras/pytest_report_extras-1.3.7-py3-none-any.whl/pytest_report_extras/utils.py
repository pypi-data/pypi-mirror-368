import base64
import html
import importlib.metadata
import os
import pathlib
import pytest
import shutil
import sys
import uuid
from typing import Literal, Optional
from .link import Link


error_screenshot = None


#
# Auxiliary functions
#
def check_options(htmlpath: Optional[str], allurepath: Optional[str]) -> None:
    """ Verifies if the --html or --alluredir option has been set. """
    if htmlpath is None and allurepath is None:
        message = ("\nIt appears you are using the pytest-report-extras plugin.\n"
                   "This requires either the pytest-html or allure-pytest plugin to generate reports.\n"
                   "Please ensure you provide the --html or --alluredir option when running pytest.\n")
        print(message, file=sys.stderr)


def check_lists_length(report, fx_extras) -> bool:
    """
    Verifies if the comment, multimedia, page source and attachment lists have the same length

    Args:
        report (pytest.TestReport): The pytest test report.
        fx_extras (Extras): The report extras.
    """
    message = ('"multimedia", "comments", "sources", and "attachments" lists don\'t have the same length.\n'
               "Steps won't be logged for this test in pytest-html report.\n")
    if not (len(fx_extras.multimedia) == len(fx_extras.comments) ==
            len(fx_extras.sources) == len(fx_extras.attachments)):
        log_error(report, message)
        return False
    else:
        return True


def create_assets(htmlpath: Optional[str], single_page: bool) -> None:
    """ Recreate report sub-folders. """
    global error_screenshot
    if htmlpath is None:
        return
    folder = f"{htmlpath}{os.sep}"
    try:
        # Create downloads folder
        shutil.rmtree(f"{folder}downloads", ignore_errors=True)
        pathlib.Path(f"{folder}downloads").mkdir(parents=True)
        # Get error image file
        resources_path = pathlib.Path(__file__).parent.joinpath("resources")
        error_img = pathlib.Path(resources_path, "error.png")
        if single_page:
            try:
                f = open(error_img, 'rb')
                data = f.read()
                f.close()
                error_screenshot = f"data:image/png;base64,{base64.b64encode(data).decode()}"
            except Exception:
                pass
            finally:
                return
        # Create other folders
        for subfolder in ("images", "sources", "videos", "audio"):
            shutil.rmtree(f"{folder}{subfolder}", ignore_errors=True)
            pathlib.Path(f"{folder}{subfolder}").mkdir(parents=True)
        # Copy error.png to images folder
        shutil.copy(str(error_img), f"{folder}images")
        error_screenshot = f"images{os.sep}error.png"
    except OSError as error:
        message = ("Cannot create report sub-folders.\n"
                   "pytest-report-extras won't work properly.\n")
        print(message, repr(error), file=sys.stderr)


def delete_empty_subfolders(htmlpath: Optional[str]) -> None:
    if htmlpath is None:
        return
    folder = f"{htmlpath}{os.sep}"
    try:
        for subfolder in ("sources", "videos", "audio", "downloads"):
            if (
                os.path.exists(f"{folder}{subfolder}") and
                os.path.isdir(f"{folder}{subfolder}") and
                len(os.listdir(f"{folder}{subfolder}")) == 0
            ):
                pathlib.Path(f"{folder}{subfolder}").rmdir()
        # check whether to delete 'images' subfolder
        if os.path.exists(f"{folder}images") and os.path.isdir(f"{folder}images"):
            files = os.listdir(f"{folder}images")
            if len(files) == 1 and files[0] == "error.png":
                shutil.rmtree(f"{folder}images", ignore_errors=True)
    except OSError:
        pass


def get_folder(filepath: Optional[str]) -> Optional[str]:
    """
    Returns the folder of a filepath.

    Args:
        filepath (str): The filepath.
    """
    folder = None
    if filepath is not None:
        folder = os.path.dirname(filepath)
    return folder if folder != '' else '.'


def escape_html(text: Optional[str], quote=False) -> Optional[str]:
    """ Escapes HTML characters in a text. """
    if text is None:
        return None
    return html.escape(str(text), quote)


def is_package_installed(pkg: str) -> bool:
    """ Whether a python package is installed """
    try:
        importlib.metadata.version(pkg)
        return True
    except importlib.metadata.PackageNotFoundError:
        return False


def get_scenario_steps(item) -> str:
    """ Return the steps of a pytest-bdd test scenario """
    result = ""
    try:
        for step in item.__scenario_report__.scenario.steps:
            result += f"{step.keyword} {step.name}\n"
    except Exception:
        pass
    return result


#
# Screenshot related functions
#
def check_screenshot_target_type(target):
    """
    Checks whether an object is an instance of WebDriver, WebElement, Page or Locator.

    Returns:
        bool: whether target is an instance of WebDriver, WebElement, Page or Locator.
        WebDriver | Page: target if it is an instance of WebDriver or Page.
        bool: whether target is in a valid state (applicable only to Page objects).
    """
    if is_package_installed("selenium"):
        from selenium.webdriver.remote.webdriver import WebDriver
        from selenium.webdriver.remote.webelement import WebElement
        if isinstance(target, WebDriver):
            return True, target, True
        if isinstance(target, WebElement):
            return True, None, True

    if is_package_installed("playwright"):
        from playwright.sync_api import Page
        from playwright.sync_api import Locator
        if isinstance(target, Page):
            if target.is_closed():
                return True, target, False
            else:
                return True, target, True
        if isinstance(target, Locator):
            return True, None, True
    return False, None, False


def get_screenshot(target, full_page=True, page_source=False) -> tuple[Optional[bytes], Optional[str]]:
    """
    Returns the screenshot in PNG format as bytes and the webpage source.

    Args:
        target (WebDriver | WebElement | Page | Locator): The target of the screenshot.
        full_page (bool): Whether to take a full-page screenshot if the target is an instance of WebDriver or Page.
        page_source (bool): Whether to gather the webpage source.

    Returns:
        The image as bytes and the webpage source if applicable.
    """
    image = None
    source = None

    if target is not None:
        if is_package_installed("selenium"):
            from selenium.webdriver.remote.webdriver import WebDriver
            from selenium.webdriver.remote.webelement import WebElement
            if isinstance(target, WebElement) or isinstance(target, WebDriver):
                image, source = _get_selenium_screenshot(target, full_page, page_source)

        if is_package_installed("playwright"):
            from playwright.sync_api import Page
            from playwright.sync_api import Locator
            if isinstance(target, Page) or isinstance(target, Locator):
                image, source = _get_playwright_screenshot(target, full_page, page_source)
    return image, source


def _get_selenium_screenshot(target, full_page=True, page_source=False) -> tuple[Optional[bytes], Optional[str]]:
    """
    Returns the screenshot in PNG format as bytes and the webpage source.

    Args:
        target (WebDriver | WebElement): The target of the screenshot.
        full_page (bool): Whether to take a full-page screenshot if the target is a WebDriver or WebElement instance.
        page_source (bool): Whether to gather the webpage source.

    Returns:
        The image as bytes and the webpage source if applicable.
    """
    from selenium.webdriver.chrome.webdriver import WebDriver as WebDriver_Chrome
    from selenium.webdriver.chromium.webdriver import ChromiumDriver as WebDriver_Chromium
    from selenium.webdriver.edge.webdriver import WebDriver as WebDriver_Edge
    from selenium.webdriver.remote.webelement import WebElement

    image = None
    source = None

    if isinstance(target, WebElement):
        image = target.screenshot_as_png
    else:
        if full_page is True:
            if hasattr(target, "get_full_page_screenshot_as_png"):
                image = target.get_full_page_screenshot_as_png()
            else:
                if type(target) in (WebDriver_Chrome, WebDriver_Chromium, WebDriver_Edge):
                    try:
                        image = _get_full_page_screenshot_chromium(target)
                    except Exception:
                        image = target.get_screenshot_as_png()
                else:
                    image = target.get_screenshot_as_png()
        else:
            image = target.get_screenshot_as_png()
        if page_source:
            try:
                source = target.page_source
            except Exception:
                pass
    return image, source


def _get_playwright_screenshot(target, full_page=True, page_source=False) -> tuple[Optional[bytes], Optional[str]]:
    """
    Returns the screenshot in PNG format as bytes and the webpage source.

    Args:
        target (Page | Locator): The target of the screenshot.
        full_page (bool): Whether to take a full-page screenshot if the target is a Page or Locator instance.
        page_source (bool): Whether to gather the webpage source.

    Returns:
        The image as bytes and the webpage source if applicable.
    """
    from playwright.sync_api import Page

    image = None
    source = None

    if isinstance(target, Page):
        if target.is_closed():
            raise Exception("Page instance is closed")
        image = target.screenshot(full_page=full_page)
        if page_source:
            try:
                source = target.content()
            except Exception:
                pass
    else:
        image = target.screenshot()
    return image, source


def _get_full_page_screenshot_chromium(driver) -> bytes:
    """ Returns the full-page screenshot in PNG format as bytes when using the Chromium WebDriver. """
    # get window size
    page_rect = driver.execute_cdp_cmd("Page.getLayoutMetrics", {})
    # parameters needed for full page screenshot
    # note we are setting the width and height of the viewport to screenshot, same as the site's content size
    screenshot_config = {
        "captureBeyondViewport": True,
        "fromSurface": True,
        "format": "png",
        "clip": {
            "x": 0,
            "y": 0,
            "width": page_rect["contentSize"]["width"],
            "height": page_rect["contentSize"]["height"],
            "scale": 1,
        },
    }
    # Dictionary with 1 key: data
    base_64_png = driver.execute_cdp_cmd("Page.captureScreenshot", screenshot_config)
    return base64.urlsafe_b64decode(base_64_png["data"])


#
# Persistence functions
#
def save_data_and_get_link(
    report_html: str,
    data: str | bytes,
    extension: Optional[str],
    folder: Literal["downloads", "images", "sources", "videos", "audio"]
) -> Optional[str]:
    """
    Saves data (as a string or bytes) in a file in the 'downloads' folder
    and returns its relative path to the HTML report folder.

    Args:
        report_html (str): The HTML report folder.
        data (str | bytes): The content in string or bytes to save.
        extension (str): The extension for the destination file.
        folder (str): The destination folder.

    Returns:
        The relative path to the HTML report folder of the created file.
    """
    if data in (None, ''):
        return None
    extension = '' if extension is None else '.' + extension
    filename = str(uuid.uuid4()) + extension
    try:
        destination = f"{report_html}{os.sep}{folder}{os.sep}{filename}"
        if isinstance(data, bytes):
            f = open(destination, 'wb')
        else:
            f = open(destination, 'wt')
        f.write(data)
        f.close()
        return f"{folder}{os.sep}{filename}"
    except OSError as error:
        log_error(None, f"Error saving file into '{folder}' folder:", error)
        raise


def copy_file_and_get_link(
    report_html: str,
    filepath: str,
    extension: Optional[str],
    folder: Literal["downloads", "images", "sources", "videos", "audio"]
) -> Optional[str]:
    """
    Saves a copy of a file in a given folder
    and returns its relative path to the HTML report folder.

    Args:
        report_html (str): The HTML report folder.
        filepath (str): The name of the file to copy.
        extension (str): The extension for the destination file.
        folder (str): The destination folder.

    Returns:
        The relative path to the HTML report folder of the saved file.
    """
    if filepath in (None, ''):
        return None
    # Skip copy if file already present in destination folder
    if pathlib.Path(filepath).parent == pathlib.Path(pathlib.Path.cwd(), report_html, folder):
        return f"{folder}{os.sep}{pathlib.Path(filepath).name}"
    if extension is None and filepath.rfind('.') != -1:
        extension = filepath[filepath.rfind('.') + 1:]
    extension = '' if extension is None else '.' + extension
    filename = str(uuid.uuid4()) + extension
    try:
        destination = f"{report_html}{os.sep}{folder}{os.sep}{filename}"
        shutil.copyfile(filepath, destination)
        return f"{folder}{os.sep}{filename}"
    except OSError as error:
        log_error(None, f"Error copying file '{filepath}' into '{folder}' folder:", error)
        raise


#
# Marker functions
#
def get_marker_links(
    item: pytest.Item,
    link_type: Literal["issue", "tms", "link"],
    fx_link_pattern: Optional[str] = None
) -> list[Link]:
    """
    Returns the urls and labels, as a list of tuples, of the links of a given marker.

    Args:
        item (pytest.Item): The test item.
        link_type: The marker.
        fx_link_pattern: The link pattern of the marker's url.
    """
    if fx_link_pattern is None and link_type in ("issue", "tms"):
        return []
    links = []
    if link_type == "link":
        for marker in item.iter_markers(name=link_type):
            url = marker.args[0] if len(marker.args) > 0 else None
            name = marker.args[1] if len(marker.args) > 1 else None
            icon = marker.args[2] if len(marker.args) > 2 else None
            url = marker.kwargs.get("url", url)
            name = marker.kwargs.get("name", name)
            icon = marker.kwargs.get("icon", icon)
            if url not in (None, ''):
                name = url if name is None else name
                links.append(Link(url, name, link_type, icon))
    else:
        for marker in item.iter_markers(name=link_type):
            keys = marker.args[0] if len(marker.args) > 0 else ""
            keys = marker.kwargs.get("keys", keys)
            keys = keys.replace(' ', '').split(',') if len(keys) > 0 else []
            icon = marker.args[1] if len(marker.args) > 1 else None
            icon = marker.kwargs.get("icon", icon)
            for key in keys:
                if key not in (None, ''):
                    links.append(Link(fx_link_pattern.replace("{}", key), key, link_type, icon))

    return links


def get_all_markers_links(
    item: pytest.Item,
    fx_issue_link_pattern: Optional[str],
    fx_tms_link_pattern: Optional[str]
) -> list[Link]:
    """
    Returns the urls and labels, as a list of tuples, of the links of all markers.

    Args:
        item (pytest.Item): The test item.
        fx_issue_link_pattern: The link pattern for the "issues" marker.
        fx_tms_link_pattern: The link pattern for the "tms" marker.
    """
    links1 = get_marker_links(item, "issue", fx_issue_link_pattern)
    links2 = get_marker_links(item, "tms", fx_tms_link_pattern)
    links3 = get_marker_links(item, "link")
    return links1 + links2 + links3


def add_links(
    item: pytest.Item,
    extras,
    links: list[Link],
    fx_html: Optional[str],
    fx_allure: Optional[str],
    fx_links_column: Literal["all", "link", "issue", "tms", "none"] = "all"
) -> None:
    """
    Add links to the report.

    Args:
        item (pytest.Item): The test item.
        extras (List[pytest_html.extras.extra]): The test extras.
        links (List[tuple[str, str]]: The links to add.
        fx_html (str): The report_html fixture.
        fx_allure (str): The report_allure fixture.
        fx_links_column (str): The links_column fixture.
    """
    pytest_html = item.config.pluginmanager.getplugin("html")
    for link in links:
        if fx_html is not None and pytest_html is not None:
            if fx_links_column in ("all", link.type):
                extras.append(pytest_html.extras.url(link.url, name=f"{link.icon} {link.name}"))
        if fx_allure is not None and importlib.util.find_spec("allure") is not None:
            import allure
            from allure_commons.types import LinkType
            allure_link_type = None
            if link.type == "link":
                allure_link_type = LinkType.LINK
            if link.type == "issue":
                allure_link_type = LinkType.ISSUE
            if link.type == "tms":
                allure_link_type = LinkType.TEST_CASE
            allure.dynamic.link(url=link.url, link_type=allure_link_type, name=link.name)


#
# Logger function
#
def log_error(
    report: Optional[pytest.TestReport],
    message: Optional[str],
    error: Optional[Exception] = None
) -> None:
    """
    Appends an error message in the stderr section of a test report.

    Args:
        report (pytest.TestReport): The pytest test report (optional).
        message (str): The message to log.
        error (Exception): The exception to log (optional).
    """
    if message is None and error is None:
        return
    message = f"{message}\n" if error is None else f"{message}\n{repr(error)}\n"
    if report is None:
        print(message, file=sys.stderr)
    else:
        found = False
        for i in range(len(report.sections)):
            if "stderr" in report.sections[i][0]:
                report.sections[i] = (
                    report.sections[i][0],
                    report.sections[i][1] + '\n' + message
                )
                found = True
                break
        if not found:
            report.sections.append(("Captured stderr call", message))
