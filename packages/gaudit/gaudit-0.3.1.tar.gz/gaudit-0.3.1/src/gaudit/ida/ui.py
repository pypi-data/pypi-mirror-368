"""
GAudit IDA Pro Plugin UI Components
====================================

This module provides user interface components for the GAudit IDA Pro plugin,
including dialogs for configuration, dataset management, and library selection.

The UI components use IDA Pro's form system to create interactive dialogs
that integrate seamlessly with the IDA Pro interface.
"""

from typing import List, Optional, Any, Callable
import ida_kernwin


class IDAWaitBox:
    """
    Context manager for displaying wait/progress boxes in IDA Pro.

    This class provides a convenient way to show progress indicators
    during long-running operations, automatically handling the display
    and cleanup of wait boxes.

    Example:
        ```python
        with IDAWaitBox("Processing data..."):
            # Long running operation
            process_data()
        ```

    Attributes:
        text (Optional[str]): The text to display in the wait box
    """

    def __init__(self, text: Optional[str] = None) -> None:
        """
        Initialize the wait box.

        Args:
            text: Optional text to display in the wait box
        """
        self.text: Optional[str] = text

    def update(self, text: Optional[str]) -> None:
        """
        Update the wait box text.

        Args:
            text: New text to display, or None to hide the wait box
        """
        if not text:
            if self.text:
                ida_kernwin.hide_wait_box()
        elif self.text:
            ida_kernwin.replace_wait_box(text)
        else:
            ida_kernwin.show_wait_box(text)
        self.text = text

    def __enter__(self) -> "IDAWaitBox":
        """
        Enter the context manager and show the wait box.

        Returns:
            IDAWaitBox: Self reference for context manager
        """
        if self.text:
            ida_kernwin.show_wait_box(self.text)
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        """
        Exit the context manager and hide the wait box.

        If an exception occurred, display an error message.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        if self.text:
            ida_kernwin.hide_wait_box()

        if exc_type:
            print(exc_type)
            print(exc_tb)
            print(f"val: '{exc_val!r}'")
            fname = exc_tb.tb_frame.f_code.co_filename
            error_msg = str(exc_val) or f"Unspecified Error at {fname}:{exc_tb.tb_lineno}"
            ida_kernwin.warning(error_msg)


# Form template for GAudit configuration
SETTINGS_FORM_TEXT: str = r"""
Gaudit configuration
{FormChangeCall}

< %40s {GauditServerUrl}>
<Ignore server certificate: {cert}>{IgnoreServerCert}>

< %40s {GauditEmail}>

< %40s {GauditPassword}>

""" % ("Server:", "Email:", "Password:")


class Configuration(ida_kernwin.Form):
    """
    Configuration dialog for GAudit plugin settings.

    This form allows users to configure:
    - GAudit server URL
    - SSL certificate verification
    - Authentication credentials (email and password)

    Attributes:
        save_cache (bool): Whether to save form cache
        show_dialog (bool): Whether to show as dialog
        GauditServerUrl (Form.StringInput): Server URL input field
        GauditEmail (Form.StringInput): Email input field
        GauditPassword (Form.StringInput): Password input field
        IgnoreServerCert (Form.ChkGroupControl): SSL verification checkbox
    """

    def __init__(self) -> None:
        """Initialize the configuration form with input fields."""
        form_dict = {
            "FormChangeCall": ida_kernwin.Form.FormChangeCb(self.OnFormChange),
            "IgnoreServerCert": ida_kernwin.Form.ChkGroupControl(("GLocal", "cert")),
            "GauditServerUrl": ida_kernwin.Form.StringInput(),
            "GauditEmail": ida_kernwin.Form.StringInput(),
            "GauditPassword": ida_kernwin.Form.StringInput(),
        }
        ida_kernwin.Form.__init__(self, SETTINGS_FORM_TEXT, form_dict)
        self.save_cache: bool = True
        self.show_dialog: bool = True

    def OnFormChange(self, fid: int) -> int:
        """
        Handle form change events.

        Args:
            fid: Form field ID that triggered the change

        Returns:
            int: 1 to indicate successful handling
        """
        return 1


# Form template for new analysis
NEW_ANALYSIS_FORM_TEXT: str = r"""
New analysis
{FormChangeCall}

< %40s {AnalysisComment}>

< %40s {AnalysisDataset}>

""" % ("Comment:", "Dataset:")


class NewAnalysis(ida_kernwin.Form):
    """
    Dialog for creating a new GAudit analysis.

    This form allows users to:
    - Enter a comment describing the analysis
    - Select a dataset to use for library matching

    Attributes:
        save_cache (bool): Whether to save form cache
        show_dialog (bool): Whether to show as dialog
        AnalysisComment (Form.StringInput): Comment input field
        AnalysisDataset (Form.DropdownListControl): Dataset selection dropdown
    """

    def __init__(self, datasets: List[str]) -> None:
        """
        Initialize the new analysis form.

        Args:
            datasets: List of available dataset names for the dropdown
        """
        form_dict = {
            "FormChangeCall": ida_kernwin.Form.FormChangeCb(self.OnFormChange),
            "AnalysisComment": ida_kernwin.Form.StringInput(),
            "AnalysisDataset": ida_kernwin.Form.DropdownListControl(items=datasets),
        }
        ida_kernwin.Form.__init__(self, NEW_ANALYSIS_FORM_TEXT, form_dict)
        self.save_cache: bool = True
        self.show_dialog: bool = True

    def OnFormChange(self, fid: int) -> int:
        """
        Handle form change events.

        Args:
            fid: Form field ID that triggered the change

        Returns:
            int: 1 to indicate successful handling
        """
        return 1


# Form template for adding binary to dataset
ADD_BINARY_TO_DATASET_FORM_TEXT: str = r"""
Add binary to a dataset
{FormChangeCall}

< %40s {ProjectName}>
< %40s {SourceName}>
< %40s {License}>
< %40s {Homepage}>
< %40s {ProjectDescription}>

< %s {AnalysisDataset} > < %s {AddDataset} >

""" % ("Project name (mandatory):", "Source name:", "License:", "Homepage:", "Project description:", "Dataset:", "+:")


class AddBinaryToDataset(ida_kernwin.Form):
    """
    Dialog for adding a binary to a GAudit dataset.

    This form collects metadata about the binary being added:
    - Project name (required)
    - Source name
    - License information
    - Homepage URL
    - Project description
    - Target dataset selection

    The form also includes a button to create new datasets.

    Attributes:
        save_cache (bool): Whether to save form cache
        show_dialog (bool): Whether to show as dialog
        ProjectName (Form.StringInput): Project name input (required)
        SourceName (Form.StringInput): Source name input
        License (Form.StringInput): License information input
        Homepage (Form.StringInput): Homepage URL input
        ProjectDescription (Form.StringInput): Project description input
        AnalysisDataset (Form.DropdownListControl): Dataset selection dropdown
        AddDataset (Form.ButtonInput): Button to add new dataset
    """

    def __init__(self, datasets: List[str], add_dataset_callback: Callable[[int], None]) -> None:
        """
        Initialize the add binary to dataset form.

        Args:
            datasets: List of available dataset names
            add_dataset_callback: Callback function for the add dataset button
        """
        form_dict = {
            "FormChangeCall": ida_kernwin.Form.FormChangeCb(self.OnFormChange),
            "ProjectName": ida_kernwin.Form.StringInput(),
            "SourceName": ida_kernwin.Form.StringInput(),
            "License": ida_kernwin.Form.StringInput(),
            "Homepage": ida_kernwin.Form.StringInput(),
            "ProjectDescription": ida_kernwin.Form.StringInput(),
            "AnalysisDataset": ida_kernwin.Form.DropdownListControl(items=datasets),
            "AddDataset": ida_kernwin.Form.ButtonInput(add_dataset_callback),
        }
        ida_kernwin.Form.__init__(self, ADD_BINARY_TO_DATASET_FORM_TEXT, form_dict)
        self.save_cache: bool = True
        self.show_dialog: bool = True

    def OnFormChange(self, fid: int) -> int:
        """
        Handle form change events.

        Args:
            fid: Form field ID that triggered the change

        Returns:
            int: 1 to indicate successful handling
        """
        return 1


# Form template for creating new dataset
NEW_DATASET_FORM_TEXT: str = r"""
Create a new dataset
{FormChangeCall}

< %40s {Name}>
< %40s {Comment}>

""" % ("Name (mandatory):", "Comment:")


class NewDataset(ida_kernwin.Form):
    """
    Dialog for creating a new GAudit dataset.

    This form allows users to:
    - Enter a name for the new dataset (required)
    - Provide an optional comment describing the dataset

    Dataset names must not contain spaces and must be unique.

    Attributes:
        save_cache (bool): Whether to save form cache
        show_dialog (bool): Whether to show as dialog
        Name (Form.StringInput): Dataset name input (required)
        Comment (Form.StringInput): Dataset comment input
    """

    def __init__(self) -> None:
        """Initialize the new dataset form."""
        form_dict = {
            "FormChangeCall": ida_kernwin.Form.FormChangeCb(self.OnFormChange),
            "Name": ida_kernwin.Form.StringInput(),
            "Comment": ida_kernwin.Form.StringInput(),
        }
        ida_kernwin.Form.__init__(self, NEW_DATASET_FORM_TEXT, form_dict)
        self.save_cache: bool = True
        self.show_dialog: bool = True

    def OnFormChange(self, fid: int) -> int:
        """
        Handle form change events.

        Args:
            fid: Form field ID that triggered the change

        Returns:
            int: 1 to indicate successful handling
        """
        return 1


class GauditLibChooser(ida_kernwin.Choose):
    """
    Library selection dialog for GAudit analysis results.

    This chooser displays matched libraries from GAudit analysis,
    allowing users to select which libraries to use for documentation.
    Libraries are displayed with their match count, version, and architecture.

    The chooser supports multiple selection to allow documenting with
    multiple libraries simultaneously.

    Attributes:
        selection (List[int]): List of selected item indices
        items (List[List[Any]]): List of library items to display
        icon (int): Icon index for the chooser
    """

    def __init__(self, title: str, items: List[List[Any]]) -> None:
        """
        Initialize the library chooser.

        Args:
            title: Window title for the chooser
            items: List of library items, each containing:
                   [library_name, filename, match_count, version, architecture]
        """
        ida_kernwin.Choose.__init__(
            self,
            title,
            [
                ["Library", 20 | ida_kernwin.Choose.CHCOL_PLAIN],
                ["Filename", 20 | ida_kernwin.Choose.CHCOL_PLAIN],
                ["MatchCount", 20 | ida_kernwin.Choose.CHCOL_PLAIN],
                ["Version", 20 | ida_kernwin.Choose.CHCOL_PLAIN],
                ["Architecture", 20 | ida_kernwin.Choose.CHCOL_PLAIN],
            ],
            flags=ida_kernwin.Choose.CH_MULTI,
        )
        self.selection: List[int] = []
        self.items: List[List[Any]] = items
        self.icon: int = 41

    def OnGetSize(self) -> int:
        """
        Get the number of items in the chooser.

        Returns:
            int: Number of items to display
        """
        return len(self.items)

    def OnGetLine(self, n: int) -> List[Any]:
        """
        Get the display data for a specific line.

        Args:
            n: Line index (0-based)

        Returns:
            List[Any]: Item data for the specified line
        """
        return self.items[n]

    def OnSelectionChange(self, sel_list: List[int]) -> None:
        """
        Handle selection changes in the chooser.

        Args:
            sel_list: List of selected item indices
        """
        self.selection = sel_list
