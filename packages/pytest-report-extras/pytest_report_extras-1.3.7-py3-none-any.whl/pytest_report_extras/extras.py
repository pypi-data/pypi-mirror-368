import base64
from bs4 import BeautifulSoup
from typing import Literal, Optional
from . import utils
from .attachment import Attachment
from .mime import Mime


class Extras:
    """
    Class to hold pytest-html 'extras' to be added for each test in the HTML report.
    """

    def __init__(
        self,
        report_html: str,
        single_page: bool,
        screenshots: Literal["all", "last", "fail", "none"],
        sources: bool,
        indent: int,
        report_allure: str
    ):
        """
        Args:
            report_html (str): The HTML report folder.
            single_page (bool): Whether to generate the HTML report in a single webpage.
            screenshots (str): The screenshot strategy. Possible values: 'all' or 'last'.
            sources (bool): Whether to gather webpage sources.
            indent (int): The indent to use to format XML, JSON and YAML documents.
            report_allure (str): The Allure report folder.
        """
        self.comments = []
        self.multimedia = []
        self.sources = []
        self.attachments = []
        self.target = None
        self.fx_screenshots = screenshots
        self.fx_sources = sources
        self.fx_single_page = single_page
        self.fx_html = report_html
        self.fx_allure = report_allure
        self.fx_indent = indent
        self.last_screenshot = False
        self.Mime = Mime

    def __repr__(self) -> str:
        source_list = self.sources if any( element for element in self.sources ) else []
        multimedia_list = self.multimedia if any( element for element in self.multimedia ) else []
        attachment_list = self.attachments if any( element for element in self.attachments ) else []
        return (
            f"{{id: {hex(id(self))}, comments: {self.comments}, attachments: {attachment_list}, "
            f"multimedia: {multimedia_list}, sources: {source_list}}}"
        )

    def screenshot(
        self,
        comment: str,
        target=None,
        full_page: bool = True,
        page_source: bool = False,
        escape_html: bool = True
    ) -> None:
        """
        Adds a step with a screenshot to the report.

        Args:
            comment (str): The comment of the test step.
            target (WebDriver | WebElement | Page | Locator): The target of the screenshot.
            full_page (bool): Whether to take a full-page screenshot.
            page_source (bool): Whether to include the page source. Overrides the global `sources` fixture.
            escape_html (bool): Whether to escape HTML characters in the comment.

        Raises:
            Exception: If the screenshot action raises an exception and self.last_screenshot = True.
        """
        if self.fx_allure is None and self.fx_html is None:
            return
        target_check, target_obj, _ = utils.check_screenshot_target_type(target)
        self.target = target_obj if target_obj is not None else self.target
        if target is not None and not target_check:
            utils.log_error(None, "The screenshot target is not an instance of WebDriver, WebElement, Page or Locator")
        if self.fx_screenshots != "all":
            target = None
        try:
            image, source = self._get_image_source(target, full_page, page_source)
        except Exception as error:
            if not self.last_screenshot:
                self.comments.append(comment)
                self.multimedia.append(utils.error_screenshot)
                self.sources.append(None)
                self.attachments.append(None)
                utils.log_error(None, "Error gathering screenshot", error)
                return
            else:
                self._add_extra("Error gathering last screenshot", None, None, escape_html)
                raise error
        if target is None:  # A comment alone
            self._add_extra(comment, None, None, escape_html)
        else:
            self._add_extra(comment, source, Attachment(image, None, Mime.PNG, None), escape_html)

    def attach(
        self,
        comment: str,
        body: str | bytes | dict | list[str] = None,
        source: str = None,
        mime: Mime | str = None,
        csv_delimiter: str = ',',
        escape_html: bool = True
    ) -> None:
        """
        Adds a step with an attachment to the report.
        The 'body' and 'source' parameters are exclusive.

        Args:
            comment (str): The comment of the test step.
            body (str | bytes | dict | list[str]): The content/body of the attachment or the bytes of the screenshot.
                Can be of type 'dict' for JSON mime type.
                Can be of type 'list[str]' for uri-list mime type.
                Can be of type 'bytes' for image mime type.
            source (str): The filepath of the source of the attachment.
            mime (Mime | str): The mime type of the attachment.
            csv_delimiter (str): The delimiter for CSV documents.
            escape_html (bool): Whether to escape HTML characters in the comment.
        """
        if self.fx_allure is None and self.fx_html is None:
            return
        if body is None and source is None and mime is None:
            if comment is not None:  # A comment alone
                attachment = Attachment(body="", mime=Mime.TEXT)
            else:
                attachment = None
        else:
            if body is not None and mime is None:
                attachment = Attachment(error="Mime is required for attachments with body")
            elif body is None and source is None and mime is not None:
                attachment = Attachment(error="Attachment body or source is None")
            else:
                mime = Mime.get_mime(Mime.get_extension(source)) if mime is None else Mime.get_mime(mime)
                attachment = self._get_attachment(body, source, mime, csv_delimiter)
        self._add_extra(comment, None, attachment, escape_html)

    def _get_attachment(
        self,
        body: str | dict | list[str] | bytes = None,
        source: str = None,
        mime: Mime = None,
        delimiter=',',
    ) -> Attachment:
        """
        Creates an attachment from its body or source.

        Args:
            body (str | bytes | dict | list[str]): The content/body of the attachment or the bytes of the screenshot.
                Can be of type 'dict' for JSON mime type.
                Can be of type 'list[str]' for uri-list mime type.
                Can be of type 'bytes' for image mime type.
            source (str): The filepath of the source of the attachment.
            mime (Mime): The mime type of the attachment.
            delimiter (str): The delimiter for CSV documents.

        Returns:
            An attachment instance.
        """
        if source is not None:
            if mime == Mime.HTML or Mime.is_unsupported(mime):
                return Attachment.parse_source(source, mime, self)
            elif Mime.is_multimedia(mime) and mime != Mime.SVG:
                return Attachment(source=source, mime=mime)
            else:
                try:
                    f = open(source, 'r')
                    body = f.read()
                    f.close()
                except Exception as error:
                    error_msg = f"Error creating attachment from source {source}"
                    utils.log_error(None, error_msg, error)
                    return Attachment(error=f"{error_msg}\n{error}")
        else:
            if mime == Mime.HTML or Mime.is_unsupported(mime):
                return Attachment.parse_body(body=body, mime=mime, report=self)
        if mime == Mime.SVG:
            return Attachment(body=body, source=source, mime=mime)
        return Attachment.parse_body(body, mime, self.fx_indent, delimiter, self)

    def _get_image_source(
        self,
        target=None,
        full_page: bool = True,
        page_source: bool = False
    ) -> tuple[Optional[bytes], Optional[str]]:
        """
        Gets the screenshot as bytes and the webpage source if applicable.

        Args:
            target (WebDriver | WebElement | Page | Locator): The target of the screenshot.
            full_page (bool): Whether to take a full-page screenshot.
            page_source (bool): Whether to include the page source. Overrides the global `sources` fixture.

        Returns: The screenshot as bytes and the webpage source if applicable.
        """
        if target is None or self.fx_screenshots == "last":
            return None, None
        return utils.get_screenshot(target, full_page, self.fx_sources or page_source)

    def _save_data(self, data: Optional[bytes | str], mime: Optional[Mime]) -> Optional[str]:
        """
        Saves multimedia data.

        When not using the --self-contained-html option, saves the data
            and returns the filepaths relative to the <report_html> folder.
        The image is saved in <report_html>/images folder.
        The video is saved in <report_html>/videos folder.
        The audio is saved in <report_html>/audio folder.

        When using the --self-contained-html option, returns the data URI schema of the data.

        Args:
            data (bytes | str): The data as bytes or base64 string.
            mime (Mime): The mime type of the data.

        Returns:
            The uri of the data.
        """
        if data is None:
            return None
        if mime is None or Mime.is_not_multimedia(mime):
            utils.log_error(None, "Invalid mime type '{mime}' for multimedia content:")
            return None

        link_multimedia = None
        data_str = None
        data_b64 = None
        extension = Mime.get_extension(mime)

        if isinstance(data, str):
            if mime == Mime.SVG:
                data_str = data
                data_b64 = data
            else:
                try:
                    data_str = data
                    data_b64 = base64.b64decode(data.encode())
                except Exception as error:
                    utils.log_error(None, "Error decoding image/video/audio base64 string:", error)
                    return None
        else:
            try:
                data_b64 = data
                data_str = base64.b64encode(data).decode()
            except Exception as error:
                utils.log_error(None, "Error encoding image/video/audio bytes:", error)
                return None

        if Mime.is_video(mime) or Mime.is_audio(mime):
            if self.fx_single_page is False:
                if Mime.is_video(mime):
                    link_multimedia = utils.save_data_and_get_link(self.fx_html, data_b64, extension, "videos")
                if Mime.is_audio(mime):
                    link_multimedia = utils.save_data_and_get_link(self.fx_html, data_b64, extension, "audio")
            else:
                link_multimedia = f"data:{mime};base64,{data_str}"
            return link_multimedia

        if Mime.is_image(mime):
            if self.fx_single_page is False:
                link_multimedia = utils.save_data_and_get_link(self.fx_html, data_b64, extension, "images")
            else:
                link_multimedia = f"data:{mime};base64,{data_str}"

        return link_multimedia

    def _save_webpage_source(self, source: Optional[str]) -> Optional[str]:
        """
        Saves a webpage source.

        When not using the --self-contained-html option, saves the webpage in <report_html>/sources folder
           and returns the filepaths relative to the <report_html> folder.
        When using the --self-contained-html option, returns the data URI schema of the webpage source.

        Args:
            source (str): The webpage source.

        Returns:
            The uri of the webpage source.
        """
        if source is None:
            return None

        link_source = None
        if self.fx_single_page is False:
            link_source = utils.save_data_and_get_link(self.fx_html, source, None, "sources")
        else:
            link_source = f"data:text/plain;base64,{base64.b64encode(source.encode()).decode()}"

        return link_source

    def _copy_file(self, filepath: str, mime: Optional[Mime]) -> Optional[str]:
        """
        Copies a multimedia file.

        When not using the --self-contained-html option, copies the file
            and returns the filepaths relative to the <report_html> folder.
        The image is copied into <report_html>/images folder.
        The video is copied into <report_html>/videos folder.
        The audio is copied into <report_html>/audio folder.

        When using the --self-contained-html option, returns the data URI schema of the file data.

        Args:
            filepath (str): The filepath of the file to copy.
            mime (Mime): The mime type of the file

        Returns:
            The uri of the file copy.
        """
        if mime is None or Mime.is_not_multimedia(mime):
            utils.log_error(None, f"invalid mime type '{mime}' for multimedia file '{filepath}")
            return None

        data_str = ""
        extension = Mime.get_extension(mime)
        if self.fx_single_page:
            try:
                f = open(filepath, "rb")
                data_b64 = f.read()
                f.close()
                data_str = base64.b64encode(data_b64).decode()
            except Exception as error:
                utils.log_error(None, f"Error reading image/video/audio file '{filepath}'", error)
                return None
            return f"data:{mime};base64,{data_str}"

        if Mime.is_video(mime):
            return utils.copy_file_and_get_link(self.fx_html, filepath, extension, "videos")

        if Mime.is_audio(mime):
            return utils.copy_file_and_get_link(self.fx_html, filepath, extension, "audio")

        if Mime.is_image(mime):
            return utils.copy_file_and_get_link(self.fx_html, filepath, extension, "images")

    def _add_extra(
        self,
        comment: str,
        websource: Optional[str],
        attachment: Optional[Attachment],
        escape_html: bool
    ) -> None:
        """
        Adds the comment, webpage source and attachment to the lists of the 'report' fixture.
        Screenshots are stored in the attachment argument.
        Images are saved in <report_html>/images folder.
        Webpage sources are saved in <report_html>/sources folder.
        Videos are saved in <report_html>/videos folder.
        Audios are saved in <report_html>/audio folder.
        Other types of files are saved in <report_html>/downloads folder.

        Args:
            comment (str): The comment of the test step.
            websource (str): The webpage source code.
            attachment (Attachment): The attachment.
            escape_html (bool): Whether to escape HTML characters in the comment.
        """
        link_multimedia = None
        link_source = None
        mime = attachment.mime if attachment is not None else None

        # Add extras to Allure report if allure-pytest plugin is being used.
        if self.fx_allure:
            comment_allure = BeautifulSoup(comment, 'html.parser').text if not escape_html else comment
            import allure
            if attachment is not None:
                try:
                    if attachment.body is not None:
                        allure.attach(attachment.body, name=comment_allure, attachment_type=mime)
                    elif attachment.source is not None:
                        allure.attach.file(attachment.source, name=comment_allure)
                    if websource is not None:
                        allure.attach(websource, name="page source", attachment_type=allure.attachment_type.TEXT)
                except Exception as err:
                    allure.attach(str(err), name="Error adding attachment", attachment_type=allure.attachment_type.TEXT)
            else:  # Comment alone
                allure.attach("", name=comment_allure, attachment_type=allure.attachment_type.TEXT)

        # Add extras to pytest-html report if pytest-html plugin is being used.
        if self.fx_html:
            comment_html = utils.escape_html(comment) if escape_html else comment
            if comment_html is None and attachment is None:
                utils.log_error(None, "Empty test step will be ignored.", None)
                return
            if attachment is not None and Mime.is_multimedia(mime):
                error_msg = None
                if attachment.source is not None:
                    try:
                        link_multimedia = self._copy_file(attachment.source, mime)
                    except OSError as error:
                        error_msg = f"Error copying file {attachment.source}\n{error}"
                else:
                    try:
                        link_multimedia = self._save_data(attachment.body, mime)
                        link_source = self._save_webpage_source(websource)
                    except OSError as error:
                        error_msg = f"Error saving data\n{error}"
                if error_msg is not None:
                    attachment = Attachment(error=error_msg)
                else:  # Cleanup of useless attachment's info
                    if Mime.is_video(mime):
                        attachment.body = None
                    if Mime.is_image_binary(mime):
                        attachment = None
            self.comments.append(comment_html)
            self.multimedia.append(link_multimedia)
            self.sources.append(link_source)
            self.attachments.append(attachment)

    def _last_screenshot(
        self,
        comment: str,
        target=None
    ) -> None:
        """
        Adds a step with the last screenshot to the report
        Returns the CSS class to apply to the comment table row of the pytest HTML report.

        Args:
            comment (str): The comment of the test step.
            target (WebDriver | WebElement | Page | Locator): The target of the screenshot.
        """
        self.fx_screenshots = "all"
        self.last_screenshot = True
        self.screenshot(comment, target, full_page=True)
