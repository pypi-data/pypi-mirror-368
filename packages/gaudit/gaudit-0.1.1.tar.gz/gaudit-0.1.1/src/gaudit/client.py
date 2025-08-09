"""
GLIMPS Audit API Client Library

A Python client library for interacting with the GLIMPS Audit API v2.0.4
"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from urllib.parse import urlparse, urlunparse

requests.packages.urllib3.disable_warnings()


class GlimpsAuditClient:
    """Python client for GLIMPS Audit API v2.0.4"""

    def __init__(self, url: str = "https://gaudit.glimps.re", verify_ssl: bool = True):
        """
        Initialize the GLIMPS Audit API client.

        Args:
            url: Any URL for the GLIMPS server (will be converted to API endpoint)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        self.base_url = self._compute_base_url(url)
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.token = None
        self.token_expiry = None

    def _compute_base_url(self, url: str) -> str:
        """
        Extract the base domain from any URL and construct the API endpoint.

        Examples:
            https://gaudit.glimps.re → https://gaudit.glimps.re/api/v2
            https://gaudit.glimps.re/some/path → https://gaudit.glimps.re/api/v2
            https://example.com:8080 → https://example.com:8080/api/v2
        """
        parsed = urlparse(url)
        # Reconstruct URL with just scheme, netloc (host:port)
        base = urlunparse((parsed.scheme, parsed.netloc, '', '', '', ''))
        return f"{base}/api/v2"

    def _get_headers(self, auth_required: bool = True) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if auth_required and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _make_request(
        self,
        method: str,
        endpoint: str,
        auth_required: bool = True,
        json_data: Optional[Dict] = None,
        data: Optional[Any] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> requests.Response:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}{endpoint}"

        if headers is None:
            headers = self._get_headers(auth_required)
        else:
            if auth_required and self.token:
                headers["Authorization"] = f"Bearer {self.token}"

        response = self.session.request(
            method=method,
            url=url,
            json=json_data,
            data=data,
            files=files,
            params=params,
            headers=headers,
            verify=self.verify_ssl,
        )

        return response

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and raise exceptions for errors."""
        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_msg = error_data.get("error", "Unknown error")
                details = error_data.get("details", "")
                raise Exception(f"API Error {response.status_code}: {error_msg}. Details: {details}")
            except json.JSONDecodeError:
                raise Exception(f"API Error {response.status_code}: {response.text}")

        # Handle different content types
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return response.json()
        elif "text/plain" in content_type:
            return response.text
        elif "application/octet-stream" in content_type:
            return response.content
        else:
            return response.text

    # User Management Endpoints

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate with the server.

        Args:
            email: User email
            password: User password

        Returns:
            Authentication response with token and user info
        """
        data = {"email": email, "password": password}
        response = self._make_request("POST", "/user/login", auth_required=False, json_data=data)
        result = self._handle_response(response)

        # Store token and calculate expiry
        if "token" in result:
            self.token = result["token"]
            validity_ms = result.get("validity", 86400000)  # Default 24 hours
            self.token_expiry = datetime.now() + timedelta(milliseconds=validity_ms)

        return result

    def refresh_token(self) -> Dict[str, Any]:
        """
        Refresh the authentication token.

        Returns:
            New authentication response with refreshed token
        """
        response = self._make_request("POST", "/user/refresh")
        result = self._handle_response(response)

        # Update token and expiry
        if "token" in result:
            self.token = result["token"]
            validity_ms = result.get("validity", 86400000)
            self.token_expiry = datetime.now() + timedelta(milliseconds=validity_ms)

        return result

    def change_password(self, current_password: str, new_password: str) -> Dict[str, Any]:
        """
        Change user password.

        Args:
            current_password: Current password
            new_password: New password (min 6 characters)

        Returns:
            Status response
        """
        data = {"current_password": current_password, "password": new_password}
        response = self._make_request("POST", "/user/password", json_data=data)
        return self._handle_response(response)

    def get_user_properties(self) -> Dict[str, Any]:
        """
        Get user properties.

        Returns:
            User properties including username, email, admin status, and services
        """
        response = self._make_request("GET", "/user/properties")
        return self._handle_response(response)

    def get_user_analyses(self) -> Dict[str, Any]:
        """
        Get user analyses statistics.

        Returns:
            Analysis statistics including count, disk usage, and duration
        """
        response = self._make_request("GET", "/user/analyses")
        return self._handle_response(response)

    def delete_user_analyses(self) -> Dict[str, Any]:
        """
        Delete all user analyses (only own analyses, not group analyses).

        Returns:
            Status response
        """
        response = self._make_request("POST", "/user/delete_analyses")
        return self._handle_response(response)

    # Audit Endpoints

    def get_audit_groups(self) -> List[str]:
        """
        Get user audit groups.

        Returns:
            List of audit group names
        """
        response = self._make_request("GET", "/audits/groups")
        return self._handle_response(response)

    def create_audit(
        self,
        group: str,
        files: Dict[str, str],
        comment: Optional[str] = None,
        services: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Submit new files for analysis.

        Args:
            group: Audit group name
            files: Dictionary mapping file IDs to filenames
            comment: Optional comment for the audit
            services: Optional services configuration

        Returns:
            Response with audit IDs and file IDs
        """
        data = {"group": group, "files": [files] if isinstance(files, dict) else files}
        if comment:
            data["comment"] = comment
        if services:
            data["services"] = [services] if isinstance(services, dict) else services

        response = self._make_request("POST", "/audits", json_data=data)
        return self._handle_response(response)

    def list_audits(
        self, filter: Optional[str] = None, sort_order: str = "desc", page_number: int = 0, page_size: int = 25
    ) -> Dict[str, Any]:
        """
        List audits with optional filtering and pagination.

        Args:
            filter: Filter string to search in group, description, filename, SHA256
            sort_order: Sort order - "asc" or "desc" (default: "desc")
            page_number: Page number (default: 0)
            page_size: Page size (default: 25, max: 1000)

        Returns:
            List of audits with count
        """
        params = {"sortOrder": sort_order, "pageNumber": page_number, "pageSize": page_size}
        if filter:
            params["filter"] = filter

        response = self._make_request("GET", "/audits", params=params)
        return self._handle_response(response)

    def get_audit(self, audit_id: str) -> Dict[str, Any]:
        """
        Get audit result by ID.

        Args:
            audit_id: Audit UUID

        Returns:
            Detailed audit information including libraries found
        """
        response = self._make_request("GET", f"/audits/{audit_id}")
        return self._handle_response(response)

    def delete_audit(self, audit_id: str) -> Dict[str, Any]:
        """
        Delete an audit.

        Args:
            audit_id: Audit UUID

        Returns:
            Status response
        """
        response = self._make_request("DELETE", f"/audits/{audit_id}")
        return self._handle_response(response)

    def upload_file_for_audit(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a binary file to be used in an audit.

        Args:
            file_path: Path to the file to upload (EXE, ELF, or PDB)

        Returns:
            Response with file ID (SHA256)
        """
        with open(file_path, "rb") as f:
            files = {"file": f}
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            response = self._make_request("POST", "/audits/upload", auth_required=False, files=files, headers=headers)
        return self._handle_response(response)

    def generate_idc(self, audit_id: str, library_ids: List[str]) -> str:
        """
        Generate IDC file for an audit.

        Args:
            audit_id: Audit UUID
            library_ids: List of library IDs to document with

        Returns:
            IDC file content as string
        """
        data = {"libs": ",".join(library_ids)}
        headers = {"Content-Type": "multipart/form-data"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        # For multipart/form-data, we need to use data instead of json
        response = self._make_request(
            "POST", f"/audits/{audit_id}/idc", auth_required=False, data=data, headers=headers
        )
        return self._handle_response(response)

    def download_audit_binary(self, audit_id: str, file_id: str, save_path: Optional[str] = None) -> bytes:
        """
        Download binary file from an audit.

        Args:
            audit_id: Audit UUID
            file_id: File ID (SHA256)
            save_path: Optional path to save the file

        Returns:
            Binary content of the file
        """
        response = self._make_request("GET", f"/audits/{audit_id}/{file_id}/binary")
        content = self._handle_response(response)

        if save_path:
            with open(save_path, "wb") as f:
                f.write(content)

        return content

    # Library Endpoints

    def list_libraries(
        self, filter: Optional[str] = None, page_number: int = 0, page_size: int = 25, sort: str = "asc"
    ) -> Dict[str, Any]:
        """
        List libraries with optional filtering and pagination.

        Args:
            filter: Filter string to search in arch, SHA256, binary_name, project_name
            page_number: Page number (default: 0)
            page_size: Page size (default: 25, max: 2000)
            sort: Sort order - "asc" or "desc" (default: "asc")

        Returns:
            List of libraries with count
        """
        params = {"pageNumber": page_number, "pageSize": page_size, "sort": sort}
        if filter:
            params["filter"] = filter

        response = self._make_request("GET", "/libraries", params=params)
        return self._handle_response(response)

    # Dataset Endpoints

    def list_datasets(self) -> Dict[str, Any]:
        """
        List user datasets.

        Returns:
            List of datasets with count
        """
        response = self._make_request("GET", "/datasets")
        return self._handle_response(response)

    def create_dataset(self, name: str, comment: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new dataset.

        Args:
            name: Dataset name (4-26 chars, alphanumeric with _ and -)
            comment: Optional comment describing the dataset

        Returns:
            Response with dataset ID
        """
        data = {"name": name}
        if comment:
            data["comment"] = comment

        response = self._make_request("POST", "/datasets", json_data=data)
        return self._handle_response(response)

    def upload_file_for_dataset(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a binary file to be used in a dataset.

        Args:
            file_path: Path to the file to upload (EXE, ELF, or PDB)

        Returns:
            Response with file ID
        """
        with open(file_path, "rb") as f:
            files = {"file": f}
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            response = self._make_request(
                "POST", "/datasets/upload", auth_required=False, files=files, headers=headers
            )
        return self._handle_response(response)

    def get_dataset_entries(
        self, dataset_name: str, size: int = 25, from_index: int = 0, filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List dataset entries.

        Args:
            dataset_name: Dataset name
            size: Number of entries to fetch (default: 25)
            from_index: Number of entries to skip (default: 0)
            filter: Filter string to search in arch, SHA256, binary_name, project_name

        Returns:
            List of dataset entries with count
        """
        params = {"size": size, "from": from_index}
        if filter:
            params["filter"] = filter

        response = self._make_request("GET", f"/datasets/{dataset_name}", params=params)
        return self._handle_response(response)

    def delete_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """
        Delete a user dataset.

        Args:
            dataset_name: Dataset name

        Returns:
            Status response
        """
        response = self._make_request("DELETE", f"/datasets/{dataset_name}")
        return self._handle_response(response)

    def add_dataset_entries(
        self,
        dataset_name: str,
        project_name: str,
        files: List[Dict[str, str]],
        source_name: Optional[str] = None,
        license: Optional[str] = None,
        home_page: Optional[str] = None,
        project_description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add entries to a dataset.

        Args:
            dataset_name: Dataset name
            project_name: Project name (e.g., "Glib", "openssl")
            files: List of file entries with 'id', 'binary_name', and optional 'version', 'dbg_id'
            source_name: Optional source name
            license: Optional license information
            home_page: Optional project homepage URL
            project_description: Optional project description

        Returns:
            Response with status for each added file
        """
        data = {"project_name": project_name, "files": files}
        if source_name:
            data["source_name"] = source_name
        if license:
            data["license"] = license
        if home_page:
            data["home_page"] = home_page
        if project_description:
            data["project_description"] = project_description

        response = self._make_request("POST", f"/datasets/{dataset_name}", json_data=data)
        return self._handle_response(response)

    def update_dataset(self, dataset_name: str) -> None:
        """
        Update a dataset to the latest version.

        Args:
            dataset_name: Dataset name

        Note:
            This returns 202 Accepted. Check status with get_dataset_entries()
        """
        response = self._make_request("POST", f"/datasets/{dataset_name}/update")
        if response.status_code != 202:
            self._handle_response(response)

    # Helper methods

    def is_token_valid(self) -> bool:
        """Check if the current token is still valid."""
        if not self.token or not self.token_expiry:
            return False
        return datetime.now() < self.token_expiry

    def ensure_authenticated(self) -> None:
        """Ensure the client is authenticated, refreshing token if needed."""
        if not self.is_token_valid():
            if self.token:
                self.refresh_token()
            else:
                raise Exception("Not authenticated. Please call login() first.")
