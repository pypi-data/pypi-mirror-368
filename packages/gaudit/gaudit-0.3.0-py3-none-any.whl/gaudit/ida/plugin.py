"""
GAudit IDA Pro Plugin
=====================

A plugin for IDA Pro that integrates with the GLIMPS Audit (GAudit) platform
to analyze binaries, document databases, and manage datasets.

This plugin provides functionality to:
- Document IDA Pro databases using GAudit's library matching
- Add binaries to GAudit datasets
- Build ELF files from IDA Pro databases
- Integrate with GAudit's API for binary analysis
"""

import os
import shutil
import tempfile
import time
from typing import Optional, List, Dict, Any

from gaudit.client import GlimpsAuditClient
import ida_nalt
import idaapi
import ida_kernwin
import idc

from .idbtoelf import build_elf
from .ui import AddBinaryToDataset, Configuration, GauditLibChooser, IDAWaitBox, NewDataset, NewAnalysis
from .version import VERSION
from gaudit import Config


def get_version() -> str:
    """
    Get the current plugin version.

    Returns:
        str: The version string of the plugin
    """
    return VERSION


# Polling delay in seconds for checking analysis status
GAUDIT_POLLING_DELAY: float = 1.0


class GauditPlugin(idaapi.plugin_t):
    """
    Main IDA Pro plugin class for GAudit integration.

    This plugin provides menu items and functionality for:
    - Documenting databases with matched libraries
    - Adding binaries to datasets
    - Building ELF files from IDA databases

    Attributes:
        comment (str): Plugin description shown in IDA
        help (str): Help text for the plugin
        wanted_name (str): Name displayed in IDA's plugin menu
        wanted_hotkey (str): Keyboard shortcut (empty for none)
        flags (int): Plugin flags (PLUGIN_KEEP to keep loaded)
        gaudit_api (Optional[GlimpsAuditClient]): API client instance
        config (Config): Configuration object for storing settings
        document_handler (DocumentHandler): Handler for documentation actions
        add_to_dataset (AddToDatasetHandler): Handler for dataset operations
        build_elf (BuildElfHandler): Handler for ELF building
    """

    comment: str = "GAudit plugin for IDA Pro"
    help: str = "GAudit plugin"
    wanted_name: str = "GAudit settings"
    wanted_hotkey: str = ""
    flags: int = idaapi.PLUGIN_KEEP
    gaudit_api: Optional[GlimpsAuditClient] = None
    config: Config
    document_handler: "DocumentHandler"
    add_to_dataset: "AddToDatasetHandler"
    build_elf: "BuildElfHandler"

    def init(self) -> int:
        """
        Initialize the plugin when IDA Pro loads it.

        This method:
        1. Checks for required dependencies
        2. Creates action handlers
        3. Registers menu items
        4. Loads or creates configuration

        Returns:
            int: PLUGIN_KEEP to keep the plugin loaded, or PLUGIN_SKIP to skip
        """
        # Check for required libraries
        try:
            import construct  # noqa: F401
        except ImportError:
            print("GAudit: construct library is missing")
            print("python3 -m pip install construct")
            return idaapi.PLUGIN_SKIP

        try:
            import requests  # noqa: F401
        except ImportError:
            print("GAudit: requests library is missing")
            print("python3 -m pip install requests")
            return idaapi.PLUGIN_SKIP

        # Initialize action handlers
        self.document_handler = DocumentHandler(self)
        self.add_to_dataset = AddToDatasetHandler(self)
        self.build_elf = BuildElfHandler(self)

        # Register and attach menu actions
        self._register_menu_actions()

        # Initialize configuration
        self._initialize_config()

        return idaapi.PLUGIN_KEEP

    def _register_menu_actions(self) -> None:
        """Register plugin actions and attach them to IDA's menu system."""
        # Document database action
        document_action = idaapi.action_desc_t(
            "my:documentdb", "Document database", self.document_handler, None, "Document database"
        )
        idaapi.register_action(document_action)
        idaapi.attach_action_to_menu("Edit/GAudit/Document database", "my:documentdb", idaapi.SETMENU_APP)

        # Add to dataset action
        dataset_add_action = idaapi.action_desc_t(
            "my:addtodataset", "Add database to a dataset", self.add_to_dataset, None, "Add database to a dataset"
        )
        idaapi.register_action(dataset_add_action)
        idaapi.attach_action_to_menu("Edit/GAudit/Add database to a dataset", "my:addtodataset", idaapi.SETMENU_APP)

        # Build ELF action
        produce_elf_action = idaapi.action_desc_t("my:produceelf", "Build ELF", self.build_elf, None, "Build ELF")
        idaapi.register_action(produce_elf_action)
        idaapi.attach_action_to_menu("Edit/GAudit/Build ELF", "my:produceelf", idaapi.SETMENU_APP)

    def _initialize_config(self) -> None:
        """Initialize plugin configuration from file or create defaults."""
        self.config = Config()
        if os.path.exists(self.config.config_path):
            self.config.load_config()
        else:
            print(f"GAudit plugin config file not found at {self.config.config_path}, using defaults")
            self.config.url = "https://gauditsdk.glimps.lan"
            self.config.verify_ssl = True
            self.config.email = "user@glimps.lan"
            self.config.password = "mypassword"
            self.config.save_config()

    def get_api(self) -> Optional[GlimpsAuditClient]:
        """
        Get or create an authenticated GAudit API client.

        This method:
        1. Shows configuration dialog
        2. Creates client if needed
        3. Ensures authentication

        Returns:
            Optional[GlimpsAuditClient]: Authenticated API client or None if auth fails
        """
        if self.config.client is None:
            self.config.client = GlimpsAuditClient(url=self.config.url, verify_ssl=self.config.verify_ssl)
            if self.config.token:
                self.config.client.token = self.config.token

        try:
            self.config.client.ensure_authenticated()
        except Exception:
            with IDAWaitBox("Authenticating"):
                try:
                    self.config.client.login(self.config.email, self.config.password)
                except Exception:
                    self._display_configuration()
                    try:
                        self.config.client.login(self.config.email, self.config.password)
                    except Exception:
                        ida_kernwin.warning("Unable to authenticate to GAudit server")
                        return None

        return self.config.client

    def term(self) -> None:
        """
        Terminate the plugin when IDA Pro unloads it.

        This method is called when the plugin is being unloaded.
        """
        pass

    def run(self, *args, **kwargs) -> None:
        """
        Run the plugin when selected from IDA's menu.

        Args:
            *args: Variable positional arguments from IDA
            **kwargs: Variable keyword arguments from IDA
        """
        print("Running GAudit plugin")
        self._display_configuration()

    def _save_configuration(self) -> None:
        """Save the current configuration to disk."""
        self.config.save_config()

    def _display_configuration(self) -> None:
        """
        Display and handle the configuration dialog.

        Shows a form for editing GAudit server settings and credentials.
        Updates configuration if user confirms changes.
        """
        conf_form = Configuration()
        conf_form.Compile()
        conf_form.GauditServerUrl.value = self.config.url
        conf_form.GauditEmail.value = self.config.email
        conf_form.GauditPassword.value = self.config.password
        conf_form.IgnoreServerCert.value = not self.config.verify_ssl

        if conf_form.Execute() == 1:
            self.config.url = conf_form.GauditServerUrl.value
            self.config.email = conf_form.GauditEmail.value
            self.config.password = conf_form.GauditPassword.value
            self.config.verify_ssl = not conf_form.IgnoreServerCert.value
            self._save_configuration()
            if self.config.client:
                self.config.client = None


def PLUGIN_ENTRY() -> GauditPlugin:
    """
    Entry point for IDA Pro to load the plugin.

    Returns:
        GauditPlugin: Instance of the plugin class
    """
    return GauditPlugin()


class AddToDatasetHandler(idaapi.action_handler_t):
    """
    Handler for adding the current IDA database to a GAudit dataset.

    This handler:
    1. Builds an ELF from the current database
    2. Uploads it to GAudit
    3. Adds it to a selected dataset with metadata

    Attributes:
        plugin (GauditPlugin): Reference to the main plugin instance
    """

    def __init__(self, plugin: GauditPlugin) -> None:
        """
        Initialize the handler.

        Args:
            plugin: The main GAudit plugin instance
        """
        idaapi.action_handler_t.__init__(self)
        self.plugin: GauditPlugin = plugin

    def activate(self, ctx: Any) -> int:
        """
        Activate the handler when menu item is selected.

        Args:
            ctx: IDA context object

        Returns:
            int: 1 to indicate successful activation
        """
        self._gaudit_dataset_add()
        return 1

    def update(self, ctx: Any) -> int:
        """
        Update handler state for menu display.

        Args:
            ctx: IDA context object

        Returns:
            int: AST_ENABLE_ALWAYS to keep menu item always enabled
        """
        return idaapi.AST_ENABLE_ALWAYS

    def _gaudit_dataset_add(self) -> bool:
        """
        Add the current binary to a GAudit dataset.

        This method:
        1. Builds an ELF from the IDA database
        2. Uploads it to GAudit server
        3. Shows dataset selection dialog
        4. Adds the binary to the selected dataset

        Returns:
            bool: True if successful, False otherwise
        """
        # Build ELF
        with IDAWaitBox("Generating ELF"):
            elf_data = build_elf()

        gaudit_api = self.plugin.get_api()
        if not gaudit_api:
            return False

        # Upload ELF data to GAudit server
        upload_id = self._upload_elf(gaudit_api, elf_data)

        # Get dataset list and show selection dialog
        datasets_list = self._get_datasets_list(gaudit_api)

        # Handle dataset selection and metadata input
        project_info = self._get_project_info(gaudit_api, datasets_list)
        if not project_info:
            return False

        # Add binary to dataset
        self._add_to_dataset(gaudit_api, upload_id, project_info)

        ida_kernwin.info(f"Binary successfully added to dataset {project_info['dataset']}")
        return True

    def _upload_elf(self, gaudit_api: GlimpsAuditClient, elf_data: bytes) -> str:
        """
        Upload ELF data to GAudit server.

        Args:
            gaudit_api: Authenticated GAudit API client
            elf_data: Binary ELF data to upload

        Returns:
            str: Upload ID from the server
        """
        with IDAWaitBox("Uploading ELF to GAudit server"):
            d = tempfile.mkdtemp()
            try:
                tmpf = os.path.join(d, ida_nalt.get_root_filename())
                with open(tmpf, "wb") as f:
                    f.write(elf_data)
                uploads = gaudit_api.upload_file_for_dataset(tmpf)
                return uploads["id"]
            finally:
                shutil.rmtree(d)

    def _get_datasets_list(self, gaudit_api: GlimpsAuditClient) -> List[str]:
        """
        Fetch the list of available datasets.

        Args:
            gaudit_api: Authenticated GAudit API client

        Returns:
            List[str]: List of dataset names
        """
        with IDAWaitBox("Fetching dataset list"):
            datasets = gaudit_api.list_datasets()
        return [ds["name"] for ds in datasets.get("datasets", [])]

    def _get_project_info(self, gaudit_api: GlimpsAuditClient, datasets_list: List[str]) -> Optional[Dict[str, str]]:
        """
        Get project information from user via dialog.

        Args:
            gaudit_api: Authenticated GAudit API client
            datasets_list: List of available datasets

        Returns:
            Optional[Dict[str, str]]: Project information or None if cancelled
        """

        class UpdateDatasetList:
            """Helper class to handle dataset list updates."""

            def __init__(self, datasets_list: List[str]):
                self.datasets_list = datasets_list
                self.form: Optional[AddBinaryToDataset] = None

            def set_form(self, form: AddBinaryToDataset) -> None:
                self.form = form

            def __call__(self, code: int) -> None:
                gaudit_dataset_new(gaudit_api)
                self.datasets_list = self._get_datasets_list(gaudit_api)
                if self.form is not None:
                    self.form.AnalysisDataset.set_items(self.datasets_list)
                    self.form.RefreshField(self.form.AnalysisDataset)

            def _get_datasets_list(self, api: GlimpsAuditClient) -> List[str]:
                with IDAWaitBox("Fetching dataset list"):
                    datasets = api.list_datasets()
                return [ds["name"] for ds in datasets.get("datasets", [])]

        project_name = ""
        while project_name == "":
            update_dataset_list = UpdateDatasetList(datasets_list)
            add_binary_form = AddBinaryToDataset(datasets_list, update_dataset_list)
            update_dataset_list.set_form(add_binary_form)
            add_binary_form.Compile()

            if add_binary_form.Execute() != 1:
                ida_kernwin.warning("Action cancelled by user")
                return None

            datasets_list = update_dataset_list.datasets_list
            selected_dataset = datasets_list[add_binary_form.AnalysisDataset.selval]
            project_name = add_binary_form.ProjectName.value

            if project_name == "":
                ida_kernwin.warning("Invalid empty project name")
                continue

            return {
                "dataset": selected_dataset,
                "project_name": project_name,
                "source_name": add_binary_form.SourceName.value,
                "license": add_binary_form.License.value,
                "homepage": add_binary_form.Homepage.value,
                "project_description": add_binary_form.ProjectDescription.value,
            }

        return None

    def _add_to_dataset(self, gaudit_api: GlimpsAuditClient, upload_id: str, project_info: Dict[str, str]) -> None:
        """
        Add uploaded binary to the selected dataset.

        Args:
            gaudit_api: Authenticated GAudit API client
            upload_id: ID of the uploaded file
            project_info: Dictionary containing project metadata
        """
        with IDAWaitBox("Adding binary to dataset"):
            gaudit_api.add_dataset_entries(
                project_info["dataset"],
                project_info["project_name"],
                [{"id": upload_id, "binary_name": ida_nalt.get_root_filename(), "version": ""}],
                project_info["source_name"],
                project_info["license"],
                project_info["homepage"],
                project_info["project_description"],
            )


class DocumentHandler(idaapi.action_handler_t):
    """
    Handler for documenting the current IDA database with GAudit analysis.

    This handler:
    1. Builds an ELF from the current database
    2. Uploads it for analysis
    3. Waits for analysis completion
    4. Allows selection of matched libraries
    5. Applies documentation (function names) to the database

    Attributes:
        plugin (GauditPlugin): Reference to the main plugin instance
    """

    def __init__(self, plugin: GauditPlugin) -> None:
        """
        Initialize the handler.

        Args:
            plugin: The main GAudit plugin instance
        """
        idaapi.action_handler_t.__init__(self)
        self.plugin: GauditPlugin = plugin

    def activate(self, ctx: Any) -> int:
        """
        Activate the handler when menu item is selected.

        Args:
            ctx: IDA context object

        Returns:
            int: 1 to indicate successful activation
        """
        self._gaudit_document_database()
        return 1

    def update(self, ctx: Any) -> int:
        """
        Update handler state for menu display.

        Args:
            ctx: IDA context object

        Returns:
            int: AST_ENABLE_ALWAYS to keep menu item always enabled
        """
        return idaapi.AST_ENABLE_ALWAYS

    def _gaudit_document_database(self) -> bool:
        """
        Document the current database using GAudit analysis.

        This method:
        1. Authenticates to GAudit
        2. Builds and uploads an ELF
        3. Starts analysis
        4. Waits for completion
        5. Shows library selection dialog
        6. Applies selected documentation

        Returns:
            bool: True if successful, False otherwise
        """
        # Authenticate to GAudit server
        gaudit_api = self.plugin.get_api()
        if not gaudit_api:
            return False

        # Build ELF
        with IDAWaitBox("Generating ELF"):
            elf_data = build_elf()

        # Get analysis parameters
        analysis_params = self._get_analysis_parameters(gaudit_api)
        if not analysis_params:
            return False

        # Upload and analyze
        upload_id = self._upload_for_analysis(gaudit_api, elf_data)
        audit_id = self._start_analysis(gaudit_api, upload_id, analysis_params)

        # Wait for completion and get results
        audit = self._wait_for_analysis(gaudit_api, audit_id)

        # Process and apply results
        return self._process_analysis_results(gaudit_api, audit_id, audit)

    def _get_analysis_parameters(self, gaudit_api: GlimpsAuditClient) -> Optional[Dict[str, str]]:
        """
        Get analysis parameters from user dialog.

        Args:
            gaudit_api: Authenticated GAudit API client

        Returns:
            Optional[Dict[str, str]]: Analysis parameters or None if cancelled
        """
        with IDAWaitBox("Fetching dataset list"):
            datasets = gaudit_api.list_datasets()

        datasets_list = ["default"]
        datasets_list.extend(ds["name"] for ds in datasets.get("datasets", []))

        comment = ""
        while comment == "":
            new_analysis_form = NewAnalysis(datasets_list)
            new_analysis_form.Compile()

            if new_analysis_form.Execute() != 1:
                ida_kernwin.warning("New analysis was cancelled by user")
                return None

            selected_dataset = datasets_list[new_analysis_form.AnalysisDataset.selval]
            comment = new_analysis_form.AnalysisComment.value

            if comment == "":
                ida_kernwin.warning("Invalid empty comment")
                continue

            return {"dataset": selected_dataset, "comment": comment}

        return None

    def _upload_for_analysis(self, gaudit_api: GlimpsAuditClient, elf_data: bytes) -> str:
        """
        Upload ELF data for analysis.

        Args:
            gaudit_api: Authenticated GAudit API client
            elf_data: Binary ELF data to upload

        Returns:
            str: Upload ID from the server
        """
        with IDAWaitBox("Uploading ELF to GAudit server"):
            d = tempfile.mkdtemp()
            try:
                tmpf = os.path.join(d, ida_nalt.get_root_filename())
                with open(tmpf, "wb") as f:
                    f.write(elf_data)
                uploads = gaudit_api.upload_file_for_audit(tmpf)
                return uploads["id"]
            finally:
                shutil.rmtree(d)

    def _start_analysis(self, gaudit_api: GlimpsAuditClient, upload_id: str, params: Dict[str, str]) -> str:
        """
        Start analysis on the uploaded file.

        Args:
            gaudit_api: Authenticated GAudit API client
            upload_id: ID of uploaded file
            params: Analysis parameters including dataset and comment

        Returns:
            str: Audit ID for the started analysis
        """
        with IDAWaitBox("Running analysis on GAudit server"):
            services = {"GlimpsLibCorrelate": {"dataset": params["dataset"], "confidence": "1", "valid": "true"}}
            res = gaudit_api.create_audit(
                "ida plugin", {upload_id: ida_nalt.get_root_filename()}, params["comment"], services
            )
            audit_ids = res["aids"]

        if len(audit_ids) != 1:
            ida_kernwin.warning(f"Expecting only one audit ID, got {len(audit_ids)}")
            raise ValueError("Invalid audit response")

        return audit_ids[0]

    def _wait_for_analysis(self, gaudit_api: GlimpsAuditClient, audit_id: str) -> Dict[str, Any]:
        """
        Wait for analysis to complete.

        Args:
            gaudit_api: Authenticated GAudit API client
            audit_id: ID of the running audit

        Returns:
            Dict[str, Any]: Completed audit data
        """
        with IDAWaitBox("Waiting for analysis to complete on GAudit server\n(This may take several minutes)"):
            while True:
                time.sleep(GAUDIT_POLLING_DELAY)
                analysis = gaudit_api.get_audit(audit_id)
                if analysis.get("audit", {}).get("done_at", "") != "":
                    break

        return gaudit_api.get_audit(audit_id)

    def _process_analysis_results(self, gaudit_api: GlimpsAuditClient, audit_id: str, audit: Dict[str, Any]) -> bool:
        """
        Process analysis results and apply documentation.

        Args:
            gaudit_api: Authenticated GAudit API client
            audit_id: ID of the completed audit
            audit: Audit data containing analysis results

        Returns:
            bool: True if documentation was applied, False otherwise
        """
        # Build chooser items from results
        chooser_items = self._build_chooser_items(audit.get("audit", {}))

        if len(chooser_items) == 0:
            ida_kernwin.warning("No match found for this analysis")
            return False

        # Show library selection dialog
        selected_items = self._show_library_chooser(chooser_items)
        if not selected_items:
            return True

        # Generate and apply documentation
        self._apply_documentation(gaudit_api, audit_id, selected_items)
        return True

    def _build_chooser_items(self, audit: Dict[str, Any]) -> List[List[Any]]:
        """
        Build items for the library selection dialog.

        Args:
            audit: Audit data containing matched libraries

        Returns:
            List[List[Any]]: List of chooser items sorted by match count
        """
        chooser_items = []

        if "libraries" in audit and audit["libraries"]:
            for library in audit["libraries"]:
                library_name = library["name"]
                for filename, fileinfos in library["files"].items():
                    for fileinfo in fileinfos:
                        chooser_items.append(
                            [
                                library_name,
                                filename,
                                str(fileinfo["hcc"]),
                                fileinfo["version"],
                                fileinfo["arch"],
                                fileinfo["id"],
                                fileinfo["hcc"],  # For sorting
                            ]
                        )

        # Sort by match count (descending)
        return sorted(chooser_items, key=lambda x: x[6], reverse=True)

    def _show_library_chooser(self, chooser_items: List[List[Any]]) -> Optional[List[List[Any]]]:
        """
        Show library selection dialog.

        Args:
            chooser_items: List of libraries to choose from

        Returns:
            Optional[List[List[Any]]]: Selected items or None if cancelled
        """
        c = GauditLibChooser("Please select libraries", chooser_items)
        c.selection = [0]  # Default selection

        if c.Show(True) == -1:
            ida_kernwin.warning("Action cancelled by user")
            return None

        return [chooser_items[i] for i in c.selection]

    def _apply_documentation(
        self, gaudit_api: GlimpsAuditClient, audit_id: str, selected_items: List[List[Any]]
    ) -> None:
        """
        Generate and apply IDC documentation script.

        Args:
            gaudit_api: Authenticated GAudit API client
            audit_id: ID of the audit
            selected_items: Selected library items
        """
        libs_ids = [item[5] for item in selected_items]

        with IDAWaitBox("Generating documentation on GAudit server\n(This may take several minutes)"):
            idc_script = gaudit_api.generate_idc(audit_id, libs_ids)

        # Filter and process IDC statements
        idc_statements = self._process_idc_script(idc_script)

        with IDAWaitBox("Applying documentation"):
            idc.eval_idc("\n".join(idc_statements))

        print(f"{len(idc_statements)} statements executed")

    def _process_idc_script(self, idc_script: str) -> List[str]:
        """
        Process IDC script by filtering out braces.

        Args:
            idc_script: Raw IDC script from server

        Returns:
            List[str]: Processed IDC statements
        """
        idc_statements = []
        for idc_line in idc_script.splitlines():
            # Filter out braces (used for static main)
            if "{" in idc_line or "}" in idc_line:
                continue
            idc_statements.append(idc_line)
        return idc_statements


class BuildElfHandler(idaapi.action_handler_t):
    """
    Handler for building an ELF file from the current IDA database.

    This handler converts the IDA database into an ELF binary file
    that can be analyzed by GAudit or other tools.

    Attributes:
        plugin (GauditPlugin): Reference to the main plugin instance
    """

    def __init__(self, plugin: GauditPlugin) -> None:
        """
        Initialize the handler.

        Args:
            plugin: The main GAudit plugin instance
        """
        idaapi.action_handler_t.__init__(self)
        self.plugin: GauditPlugin = plugin

    def activate(self, ctx: Any) -> int:
        """
        Activate the handler when menu item is selected.

        Args:
            ctx: IDA context object

        Returns:
            int: 1 if successful, 0 if cancelled or failed
        """
        elf_file = ida_kernwin.ask_file(True, ida_nalt.get_root_filename(), "*")
        if elf_file is None:
            return 0

        # Build ELF
        with IDAWaitBox("Generating ELF"):
            elf_data = build_elf()

        if elf_data is None:
            ida_kernwin.warning("Unable to generate ELF, unknown error")
            return 0

        with open(elf_file, "wb") as f_elf_file:
            f_elf_file.write(elf_data)

        return 1

    def update(self, ctx: Any) -> int:
        """
        Update handler state for menu display.

        Args:
            ctx: IDA context object

        Returns:
            int: AST_ENABLE_ALWAYS to keep menu item always enabled
        """
        return idaapi.AST_ENABLE_ALWAYS


def gaudit_dataset_new(gaudit_api: GlimpsAuditClient) -> bool:
    """
    Create a new dataset through user dialog.

    This function shows a dialog for creating a new dataset,
    validates the input, and creates the dataset via the API.

    Args:
        gaudit_api: Authenticated GAudit API client

    Returns:
        bool: True if dataset was created successfully, False otherwise
    """
    name = ""
    while name == "":
        new_dataset_form = NewDataset()
        new_dataset_form.Compile()

        if new_dataset_form.Execute() != 1:
            ida_kernwin.warning("Action cancelled by user")
            return False

        name = new_dataset_form.Name.value
        comment = new_dataset_form.Comment.value

        if name == "":
            ida_kernwin.warning("Please enter a non-empty dataset name")
            continue

        if " " in name:
            ida_kernwin.warning("Please enter a dataset name without spaces")
            name = ""
            continue

    with IDAWaitBox("Creating dataset"):
        result = gaudit_api.create_dataset(name, comment)
        if result:
            ida_kernwin.info(f"Dataset {name} successfully created")
            return True

    ida_kernwin.warning(f"Dataset {name} not created")
    return False
