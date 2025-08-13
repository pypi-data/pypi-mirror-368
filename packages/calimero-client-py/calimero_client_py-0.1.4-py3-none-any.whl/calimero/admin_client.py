"""
Admin Client for Calimero Network
A client for performing admin operations without requiring authentication.
"""

import asyncio
import time
import base58
import json
from typing import Optional, Dict, Any, TypedDict, List
import aiohttp
from .keypair import Ed25519Keypair

class AdminApiResponse(TypedDict):
    """Type definition for Admin API response."""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]

class AdminClient:
    """Admin client for Calimero.
    
    This client handles communication with the Calimero admin API server,
    including request formatting and response handling.
    """
    
    # Constants
    DEFAULT_TIMEOUT = 30
    
    def __init__(self, admin_url: str):
        """Initialize the admin client.
        
        Args:
            admin_url: The URL of the Calimero admin API server.
        """
        self.admin_url = admin_url.rstrip('/')
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> AdminApiResponse:
        """Make a request to the admin API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Optional data to send
            
        Returns:
            The admin API response.
        """
        try:
            url = f"{self.admin_url}{endpoint}"
            headers = {'Content-Type': 'application/json'}
            
            async with aiohttp.ClientSession() as session:
                if method.upper() == 'GET':
                    async with session.get(url, headers=headers, timeout=self.DEFAULT_TIMEOUT) as response:
                        if response.status in [200, 201]:
                            result = await response.json()
                            return {'success': True, 'data': result}
                        else:
                            error_text = await response.text()
                            return {'success': False, 'error': f"HTTP {response.status}: {error_text}"}
                elif method.upper() == 'POST':
                    async with session.post(url, json=data, headers=headers, timeout=self.DEFAULT_TIMEOUT) as response:
                        if response.status in [200, 201]:
                            result = await response.json()
                            return {'success': True, 'data': result}
                        else:
                            error_text = await response.text()
                            return {'success': False, 'error': f"HTTP {response.status}: {error_text}"}
                elif method.upper() == 'DELETE':
                    async with session.delete(url, headers=headers, timeout=self.DEFAULT_TIMEOUT) as response:
                        if response.status in [200, 201, 204]:
                            result = await response.json() if response.content_length else {}
                            return {'success': True, 'data': result}
                        else:
                            error_text = await response.text()
                            return {'success': False, 'error': f"HTTP {response.status}: {error_text}"}
                else:
                    return {'success': False, 'error': f"Unsupported HTTP method: {method}"}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ============================================================================
    # Context Management Methods
    # ============================================================================
    
    async def create_context(self, application_id: str, protocol: str = "near", initialization_params: list = None) -> AdminApiResponse:
        """Create a new context.
        
        Args:
            application_id: The ID of the application to run in the context.
            protocol: The protocol to use for the context (default: "near").
            initialization_params: Optional initialization parameters.
            
        Returns:
            The admin API response containing the new context ID and member public key.
        """
        payload = {
            "applicationId": application_id,
            "protocol": protocol,
            "initializationParams": initialization_params or []
        }
        return await self._make_request('POST', '/admin-api/contexts', payload)
    
    async def list_contexts(self) -> AdminApiResponse:
        """List all contexts.
        
        Returns:
            The admin API response containing the list of contexts.
        """
        return await self._make_request('GET', '/admin-api/contexts')
    
    async def get_context(self, context_id: str) -> AdminApiResponse:
        """Get information about a specific context.
        
        Args:
            context_id: The ID of the context to retrieve.
            
        Returns:
            The admin API response containing the context information.
        """
        return await self._make_request('GET', f'/admin-api/contexts/{context_id}')
    
    async def delete_context(self, context_id: str) -> AdminApiResponse:
        """Delete a context.
        
        Args:
            context_id: The ID of the context to delete.
            
        Returns:
            The admin API response confirming the deletion.
        """
        return await self._make_request('DELETE', f'/admin-api/contexts/{context_id}')
    
    # ============================================================================
    # Identity Management Methods
    # ============================================================================
    
    async def generate_identity(self) -> AdminApiResponse:
        """Generate a new identity.
        
        Returns:
            The admin API response containing the new identity public key.
        """
        return await self._make_request('POST', '/admin-api/identity/context')
    
    async def list_identities(self, context_id: str) -> AdminApiResponse:
        """List all identities in a context.
        
        Args:
            context_id: The ID of the context.
            
        Returns:
            The admin API response containing the list of identities.
        """
        return await self._make_request('GET', f'/admin-api/contexts/{context_id}/identities')
    
    # ============================================================================
    # Invitation and Join Methods
    # ============================================================================
    
    async def invite_to_context(self, context_id: str, inviter_id: str, invitee_id: str) -> AdminApiResponse:
        """Invite an identity to a context.
        
        Args:
            context_id: The ID of the context to invite to.
            inviter_id: The public key of the inviter (context member).
            invitee_id: The public key of the identity to invite.
            
        Returns:
            The admin API response containing the invitation data.
        """
        payload = {
            "contextId": context_id,
            "inviterId": inviter_id,
            "inviteeId": invitee_id
        }
        return await self._make_request('POST', '/admin-api/contexts/invite', payload)
    
    async def join_context(self, context_id: str, invitee_id: str, invitation_payload: str) -> AdminApiResponse:
        """Join a context using an invitation.
        
        Args:
            context_id: The ID of the context to join.
            invitee_id: The public key of the identity joining the context.
            invitation_payload: The invitation data/token to join the context.
            
        Returns:
            The admin API response containing the join result.
        """
        payload = {
            "contextId": context_id,
            "inviteeId": invitee_id,
            "invitationPayload": invitation_payload
        }
        return await self._make_request('POST', '/admin-api/contexts/join', payload)
    
    # ============================================================================
    # Application Management Methods
    # ============================================================================
    
    async def install_dev_application(self, path: str, metadata: bytes = b"") -> AdminApiResponse:
        """Install a development application.
        
        Args:
            path: The local path to install the application from.
            metadata: Application metadata as bytes.
            
        Returns:
            The admin API response containing the application ID.
        """
        payload = {
            "path": path,
            "metadata": list(metadata)  # Convert bytes to list for JSON serialization
        }
        return await self._make_request('POST', '/admin-api/install-dev-application', payload)
    
    async def install_application(self, url: str, hash: str = None, metadata: bytes = b"") -> AdminApiResponse:
        """Install an application from URL.
        
        Args:
            url: The URL to install the application from.
            hash: Optional hash for verification.
            metadata: Application metadata as bytes.
            
        Returns:
            The admin API response containing the application ID.
        """
        payload = {
            "url": url,
            "metadata": list(metadata)  # Convert bytes to list for JSON serialization
        }
        if hash:
            payload["hash"] = hash
        return await self._make_request('POST', '/admin-api/install-application', payload)
    
    async def list_applications(self) -> AdminApiResponse:
        """List all installed applications.
        
        Returns:
            The admin API response containing the list of applications.
        """
        return await self._make_request('GET', '/admin-api/applications')
    
    async def get_application(self, application_id: str) -> AdminApiResponse:
        """Get information about a specific application.
        
        Args:
            application_id: The ID of the application to retrieve.
            
        Returns:
            The admin API response containing the application information.
        """
        return await self._make_request('GET', f'/admin-api/applications/{application_id}')
    
    # ============================================================================
    # Health and System Methods
    # ============================================================================
    
    async def health_check(self) -> AdminApiResponse:
        """Check the health status of the server.
        
        Returns:
            The admin API response containing the health status.
        """
        return await self._make_request('GET', '/admin-api/health')
    
    async def is_authenticated(self) -> AdminApiResponse:
        """Check if the current session is authenticated.
        
        Returns:
            The admin API response indicating authentication status.
        """
        return await self._make_request('GET', '/admin-api/is-authed')
    
    async def get_peers(self) -> AdminApiResponse:
        """Get information about connected peers.
        
        Returns:
            The admin API response containing peer information.
        """
        return await self._make_request('GET', '/admin-api/peers')
    
    async def get_peers_count(self) -> AdminApiResponse:
        """Get the count of connected peers.
        
        Returns:
            The admin API response containing the peer count.
        """
        return await self._make_request('GET', '/admin-api/peers/count')
    
    async def get_certificate(self) -> AdminApiResponse:
        """Get the server certificate.
        
        Returns:
            The admin API response containing the certificate.
        """
        return await self._make_request('GET', '/admin-api/certificate')
    
    # ============================================================================
    # Application Management Methods (Admin API)
    # ============================================================================
    
    async def install_application(self, url: str, hash: str = None, metadata: bytes = b"") -> AdminApiResponse:
        """Install an application from URL.
        
        Args:
            url: The URL to install the application from.
            hash: Optional hash for verification.
            metadata: Application metadata as bytes.
            
        Returns:
            The admin API response containing the application ID.
        """
        payload = {
            "url": url,
            "metadata": list(metadata)  # Convert bytes to list for JSON serialization
        }
        if hash:
            payload["hash"] = hash
        return await self._make_request('POST', '/admin-api/install-application', payload)
    
    async def install_dev_application(self, path: str, metadata: bytes = b"") -> AdminApiResponse:
        """Install a development application.
        
        Args:
            path: The local path to install the application from.
            metadata: Application metadata as bytes.
            
        Returns:
            The admin API response containing the application ID.
        """
        payload = {
            "path": path,
            "metadata": list(metadata)  # Convert bytes to list for JSON serialization
        }
        return await self._make_request('POST', '/admin-api/install-dev-application', payload)
    
    async def uninstall_application(self, application_id: str) -> AdminApiResponse:
        """Uninstall an application.
        
        Args:
            application_id: The ID of the application to uninstall.
            
        Returns:
            The admin API response confirming the uninstallation.
        """
        return await self._make_request('DELETE', f'/admin-api/applications/{application_id}')
    
    # ============================================================================
    # Blob Management Methods (Admin API)
    # ============================================================================
    
    async def upload_blob(self, data: bytes, metadata: bytes = b"") -> AdminApiResponse:
        """Upload a blob to the server.
        
        Args:
            data: The blob data to upload.
            metadata: Optional metadata for the blob.
            
        Returns:
            The admin API response containing the blob ID.
        """
        payload = {
            "data": list(data),  # Convert bytes to list for JSON serialization
            "metadata": list(metadata)  # Convert bytes to list for JSON serialization
        }
        return await self._make_request('POST', '/admin-api/blobs', payload)
    
    async def download_blob(self, blob_id: str) -> AdminApiResponse:
        """Download a blob from the server.
        
        Args:
            blob_id: The ID of the blob to download.
            
        Returns:
            The admin API response containing the blob data.
        """
        return await self._make_request('GET', f'/admin-api/blobs/{blob_id}')
    
    async def list_blobs(self) -> AdminApiResponse:
        """List all blobs on the server.
        
        Returns:
            The admin API response containing the list of blobs.
        """
        return await self._make_request('GET', '/admin-api/blobs')
    
    async def get_blob_info(self, blob_id: str) -> AdminApiResponse:
        """Get information about a specific blob.
        
        Args:
            blob_id: The ID of the blob.
            
        Returns:
            The admin API response containing the blob information.
        """
        return await self._make_request('GET', f'/admin-api/blobs/{blob_id}/info')
    
    async def delete_blob(self, blob_id: str) -> AdminApiResponse:
        """Delete a blob from the server.
        
        Args:
            blob_id: The ID of the blob to delete.
            
        Returns:
            The admin API response confirming the deletion.
        """
        return await self._make_request('DELETE', f'/admin-api/blobs/{blob_id}')
    
    # ============================================================================
    # Context Operations (Admin API)
    # ============================================================================
    
    async def invite_to_context(self, context_id: str, inviter_id: str, invitee_id: str) -> AdminApiResponse:
        """Invite an identity to a context.
        
        Args:
            context_id: The ID of the context to invite to.
            inviter_id: The public key of the inviter (context member).
            invitee_id: The public key of the identity to invite.
            
        Returns:
            The admin API response containing the invitation data.
        """
        payload = {
            "contextId": context_id,
            "inviterId": inviter_id,
            "inviteeId": invitee_id
        }
        return await self._make_request('POST', '/admin-api/contexts/invite', payload)
    
    async def join_context(self, context_id: str, invitee_id: str, invitation_payload: str) -> AdminApiResponse:
        """Join a context using an invitation.
        
        Args:
            context_id: The ID of the context to join.
            invitee_id: The public key of the identity joining the context.
            invitation_payload: The invitation data/token to join the context.
            
        Returns:
            The admin API response containing the join result.
        """
        payload = {
            "contextId": context_id,
            "inviteeId": invitee_id,
            "invitationPayload": invitation_payload
        }
        return await self._make_request('POST', '/admin-api/contexts/join', payload)
    
    async def update_context_application(self, context_id: str, application_id: str) -> AdminApiResponse:
        """Update the application running in a context.
        
        Args:
            context_id: The ID of the context.
            application_id: The new application ID.
            
        Returns:
            The admin API response confirming the update.
        """
        payload = {
            "contextId": context_id,
            "applicationId": application_id
        }
        return await self._make_request('PUT', f'/admin-api/contexts/{context_id}/application', payload)
    
    async def get_context_storage(self, context_id: str) -> AdminApiResponse:
        """Get the storage for a context.
        
        Args:
            context_id: The ID of the context.
            
        Returns:
            The admin API response containing the context storage.
        """
        return await self._make_request('GET', f'/admin-api/contexts/{context_id}/storage')
    
    async def get_context_identities(self, context_id: str) -> AdminApiResponse:
        """Get all identities in a context.
        
        Args:
            context_id: The ID of the context.
            
        Returns:
            The admin API response containing the list of identities.
        """
        return await self._make_request('GET', f'/admin-api/contexts/{context_id}/identities')
    
    async def sync_context(self, context_id: str = None) -> AdminApiResponse:
        """Sync a context or all contexts.
        
        Args:
            context_id: Optional specific context ID to sync.
            
        Returns:
            The admin API response confirming the sync.
        """
        if context_id:
            return await self._make_request('POST', f'/admin-api/contexts/{context_id}/sync')
        else:
            return await self._make_request('POST', '/admin-api/contexts/sync')
    
    async def get_context_value(self, context_id: str, key: str) -> AdminApiResponse:
        """Get a value from context storage.
        
        Args:
            context_id: The ID of the context.
            key: The storage key.
            
        Returns:
            The admin API response containing the value.
        """
        return await self._make_request('GET', f'/admin-api/contexts/{context_id}/storage/{key}')
    
    async def get_context_storage_entries(self, context_id: str, prefix: str = "", limit: int = 100) -> AdminApiResponse:
        """Get storage entries from a context.
        
        Args:
            context_id: The ID of the context.
            prefix: Optional prefix to filter keys.
            limit: Maximum number of entries to return.
            
        Returns:
            The admin API response containing the storage entries.
        """
        params = {"limit": limit}
        if prefix:
            params["prefix"] = prefix
        return await self._make_request('GET', f'/admin-api/contexts/{context_id}/storage/entries', params)
    
    async def get_proxy_contract(self, context_id: str) -> AdminApiResponse:
        """Get the proxy contract for a context.
        
        Args:
            context_id: The ID of the context.
            
        Returns:
            The admin API response containing the proxy contract.
        """
        return await self._make_request('GET', f'/admin-api/contexts/{context_id}/proxy-contract')
    
    # ============================================================================
    # Capability Management (Admin API)
    # ============================================================================
    
    async def grant_capabilities(self, context_id: str, granter_id: str, grantee_id: str, capability: str) -> AdminApiResponse:
        """Grant capabilities to a user in a context.
        
        Args:
            context_id: The ID of the context.
            granter_id: The public key of the granter.
            grantee_id: The public key of the grantee.
            capability: The capability to grant.
            
        Returns:
            The admin API response confirming the capability grant.
        """
        payload = {
            "contextId": context_id,
            "granterId": granter_id,
            "granteeId": grantee_id,
            "capability": capability
        }
        return await self._make_request('POST', f'/admin-api/contexts/{context_id}/capabilities/grant', payload)
    
    async def revoke_capabilities(self, context_id: str, revoker_id: str, revokee_id: str, capability: str) -> AdminApiResponse:
        """Revoke capabilities from a user in a context.
        
        Args:
            context_id: The ID of the context.
            revoker_id: The public key of the revoker.
            revokee_id: The public key of the revokee.
            capability: The capability to revoke.
            
        Returns:
            The admin API response confirming the capability revocation.
        """
        payload = {
            "contextId": context_id,
            "revokerId": revoker_id,
            "revokeeId": revokee_id,
            "capability": capability
        }
        return await self._make_request('POST', f'/admin-api/contexts/{context_id}/capabilities/revoke', payload)
    
    # ============================================================================
    # Proposal Management (Admin API)
    # ============================================================================
    
    async def get_proposals(self, context_id: str, offset: int = 0, limit: int = 100) -> AdminApiResponse:
        """Get proposals for a context.
        
        Args:
            context_id: The ID of the context.
            offset: The offset for pagination.
            limit: The maximum number of proposals to return.
            
        Returns:
            The admin API response containing the list of proposals.
        """
        params = {"offset": offset, "limit": limit}
        return await self._make_request('GET', f'/admin-api/contexts/{context_id}/proposals', params)
    
    async def get_proposal(self, context_id: str, proposal_id: str) -> AdminApiResponse:
        """Get a specific proposal.
        
        Args:
            context_id: The ID of the context.
            proposal_id: The ID of the proposal.
            
        Returns:
            The admin API response containing the proposal.
        """
        return await self._make_request('GET', f'/admin-api/contexts/{context_id}/proposals/{proposal_id}')
    
    async def get_number_of_active_proposals(self, context_id: str) -> AdminApiResponse:
        """Get the number of active proposals in a context.
        
        Args:
            context_id: The ID of the context.
            
        Returns:
            The admin API response containing the count.
        """
        return await self._make_request('GET', f'/admin-api/contexts/{context_id}/proposals/active/count')
    
    async def get_proposal_approvals_count(self, context_id: str, proposal_id: str) -> AdminApiResponse:
        """Get the approval count for a proposal.
        
        Args:
            context_id: The ID of the context.
            proposal_id: The ID of the proposal.
            
        Returns:
            The admin API response containing the approval count.
        """
        return await self._make_request('GET', f'/admin-api/contexts/{context_id}/proposals/{proposal_id}/approvals/count')
    
    async def get_proposal_approvers(self, context_id: str, proposal_id: str) -> AdminApiResponse:
        """Get the approvers for a proposal.
        
        Args:
            context_id: The ID of the context.
            proposal_id: The ID of the proposal.
            
        Returns:
            The admin API response containing the list of approvers.
        """
        return await self._make_request('GET', f'/admin-api/contexts/{context_id}/proposals/{proposal_id}/approvers')
    
    # ============================================================================
    # Alias Management (Admin API)
    # ============================================================================
    
    async def create_context_alias(self, name: str, context_id: str) -> AdminApiResponse:
        """Create an alias for a context ID.
        
        Args:
            name: The alias name.
            context_id: The context ID to alias.
            
        Returns:
            The admin API response confirming the alias creation.
        """
        payload = {
            "alias": name,
            "value": {"contextId": context_id}
        }
        return await self._make_request('POST', '/admin-api/aliases', payload)
    
    async def create_application_alias(self, name: str, application_id: str) -> AdminApiResponse:
        """Create an alias for an application ID.
        
        Args:
            name: The alias name.
            application_id: The application ID to alias.
            
        Returns:
            The admin API response confirming the alias creation.
        """
        payload = {
            "alias": name,
            "value": {"applicationId": application_id}
        }
        return await self._make_request('POST', '/admin-api/aliases', payload)
    
    async def create_identity_alias(self, context_id: str, name: str, identity_id: str) -> AdminApiResponse:
        """Create an alias for an identity in a context.
        
        Args:
            context_id: The ID of the context.
            name: The alias name.
            identity_id: The identity to alias.
            
        Returns:
            The admin API response confirming the alias creation.
        """
        payload = {
            "alias": name,
            "value": {"contextId": context_id, "identityId": identity_id}
        }
        return await self._make_request('POST', '/admin-api/aliases', payload)
    
    async def lookup_context_alias(self, name: str) -> AdminApiResponse:
        """Look up a context ID by alias.
        
        Args:
            name: The alias name to look up.
            
        Returns:
            The admin API response containing the context ID.
        """
        return await self._make_request('GET', f'/admin-api/aliases/{name}')
    
    async def lookup_application_alias(self, name: str) -> AdminApiResponse:
        """Look up an application ID by alias.
        
        Args:
            name: The alias name to look up.
            
        Returns:
            The admin API response containing the application ID.
        """
        return await self._make_request('GET', f'/admin-api/aliases/{name}')
    
    async def lookup_identity_alias(self, context_id: str, name: str) -> AdminApiResponse:
        """Look up an identity by alias in a context.
        
        Args:
            context_id: The ID of the context.
            name: The alias name to look up.
            
        Returns:
            The admin API response containing the identity.
        """
        return await self._make_request('GET', f'/admin-api/aliases/{name}')
    
    async def list_context_aliases(self) -> AdminApiResponse:
        """List all context ID aliases.
        
        Returns:
            The admin API response containing the list of aliases.
        """
        return await self._make_request('GET', '/admin-api/aliases/contexts')
    
    async def list_application_aliases(self) -> AdminApiResponse:
        """List all application ID aliases.
        
        Returns:
            The admin API response containing the list of aliases.
        """
        return await self._make_request('GET', '/admin-api/aliases/applications')
    
    async def list_identity_aliases(self, context_id: str) -> AdminApiResponse:
        """List all identity aliases in a context.
        
        Args:
            context_id: The ID of the context.
            
        Returns:
            The admin API response containing the list of aliases.
        """
        return await self._make_request('GET', f'/admin-api/aliases/contexts/{context_id}/identities')
    
    async def delete_context_alias(self, name: str) -> AdminApiResponse:
        """Delete a context ID alias.
        
        Args:
            name: The alias name to delete.
            
        Returns:
            The admin API response confirming the deletion.
        """
        return await self._make_request('DELETE', f'/admin-api/aliases/{name}')
    
    async def delete_application_alias(self, name: str) -> AdminApiResponse:
        """Delete an application ID alias.
        
        Args:
            name: The alias name to delete.
            
        Returns:
            The admin API response confirming the deletion.
        """
        return await self._make_request('DELETE', f'/admin-api/aliases/{name}')
    
    async def delete_identity_alias(self, context_id: str, name: str) -> AdminApiResponse:
        """Delete an identity alias in a context.
        
        Args:
            context_id: The ID of the context.
            name: The alias name to delete.
            
        Returns:
            The admin API response confirming the deletion.
        """
        return await self._make_request('DELETE', f'/admin-api/aliases/{name}')
