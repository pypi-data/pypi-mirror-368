import os
import json
import time
import requests
import logging
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

logger = logging.getLogger(__name__)

class CodicentAuth:
    def __init__(self, base_url="https://codicent.com"):
        self.base_url = base_url
        self.client_id = "cli-app"
        self.console = Console()
        self.token_file = Path.home() / ".codicent_token"
        
    def get_cached_token(self):
        """Get cached token if it exists and is valid."""
        if not self.token_file.exists():
            return None
            
        try:
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
            
            # Check if token has expired (with some buffer)
            if token_data.get('expires_at', 0) > time.time() + 300:  # 5 min buffer
                return token_data.get('access_token')
            else:
                logger.info("Cached token has expired")
                return None
                
        except (json.JSONDecodeError, KeyError, IOError) as e:
            logger.warning(f"Could not read cached token: {e}")
            return None
    
    def save_token(self, access_token, expires_in):
        """Save token to cache file."""
        try:
            token_data = {
                'access_token': access_token,
                'expires_at': time.time() + expires_in,
                'created_at': time.time()
            }
            
            # Create directory if it doesn't exist
            self.token_file.parent.mkdir(exist_ok=True)
            
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
                
            # Set restrictive permissions on the token file
            self.token_file.chmod(0o600)
            logger.info(f"Token saved to {self.token_file}")
            
        except IOError as e:
            logger.error(f"Could not save token: {e}")
            self.console.print(f"[yellow]Warning: Could not save token to cache: {e}[/yellow]")
    
    def clear_token(self):
        """Clear cached token."""
        try:
            if self.token_file.exists():
                self.token_file.unlink()
                logger.info("Token cache cleared")
        except IOError as e:
            logger.error(f"Could not clear token cache: {e}")
    
    def device_flow_auth(self):
        """Perform device flow authentication."""
        try:
            # Step 1: Request device code
            self.console.print("[blue]🔐 Starting device authorization flow...[/blue]")
            
            auth_data = {
                "ClientId": self.client_id,
                "Scope": "api"
            }
            
            # Project is selected by user during web authorization, no need to include it here
            
            response = requests.post(
                f"{self.base_url}/oauth/device_authorization",
                data=auth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = f"Device authorization request failed: {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text}"
                self.console.print(f"[red]❌ {error_msg}[/red]")
                return None
            
            auth_response = response.json()
            logger.info(f"Device authorization response: {auth_response}")
            
            # Step 2: Display user instructions
            self.console.print(f"\n[bold green]📱 To authorize this CLI application:[/bold green]")
            
            # Ensure verification URI uses HTTPS
            verification_uri = auth_response['verificationUri'].replace('http://', 'https://')
            verification_uri_complete = auth_response['verificationUriComplete'].replace('http://', 'https://')
            
            self.console.print(f"[green]1. Visit:[/green] [bold blue]{verification_uri}[/bold blue]")
            self.console.print(f"[green]2. Enter the code:[/green] [bold yellow]{auth_response['userCode']}[/bold yellow]")
            self.console.print(f"\n[green]Or visit directly:[/green] [bold blue]{verification_uri_complete}[/bold blue]")
            self.console.print(f"\n[dim]⏳ Waiting for authorization (expires in {auth_response['expiresIn']} seconds)...[/dim]")
            
            # Step 3: Poll for token
            device_code = auth_response["deviceCode"]
            interval = auth_response["interval"]
            expires_in = auth_response["expiresIn"]
            
            start_time = time.time()
            
            # Wait for the initial interval before first poll
            self.console.print(".", end="", style="dim")
            time.sleep(interval)
            
            while time.time() - start_time < expires_in:
                token_data = {
                    "GrantType": "urn:ietf:params:oauth:grant-type:device_code",
                    "DeviceCode": device_code,
                    "ClientId": self.client_id
                }
                
                logger.info(f"Polling for token with data: {token_data}")
                
                try:
                    token_response = requests.post(
                        f"{self.base_url}/oauth/token",
                        data=token_data,
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                        timeout=30
                    )
                    
                    logger.info(f"Token response: {token_response.status_code}")
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"Token response body: {token_response.text}")
                    
                    if token_response.status_code == 200:
                        token_data = token_response.json()
                        logger.info(f"Successful token response: {token_data}")
                        
                        # Handle different possible field names for access token
                        access_token = (token_data.get("AccessToken") or 
                                      token_data.get("access_token") or 
                                      token_data.get("accessToken") or  # Added camelCase variant
                                      token_data.get("token"))
                        
                        if not access_token:
                            self.console.print(f"\n[red]❌ No access token in response: {token_data}[/red]")
                            return None
                        
                        expires_in_seconds = (token_data.get("ExpiresIn") or 
                                            token_data.get("expires_in") or 
                                            token_data.get("expiresIn") or  # Added camelCase variant
                                            3600)
                        
                        self.console.print(f"\n[bold green]✅ Authorization successful![/bold green]")
                        
                        # Save token to cache
                        self.save_token(access_token, expires_in_seconds)
                        
                        return access_token
                    else:
                        try:
                            error_data = token_response.json()
                            error_type = error_data.get("error", "unknown_error")
                            # Handle both snake_case and camelCase error descriptions
                            error_description = (error_data.get("error_description") or 
                                               error_data.get("errorDescription") or 
                                               f"HTTP {token_response.status_code}")
                            
                            # Always log the actual response when verbose is enabled
                            if logger.isEnabledFor(logging.INFO):
                                logger.info(f"Token response error: {error_type} - {error_description}")
                                logger.info(f"Full error response: {error_data}")
                            
                            if error_type == "authorization_pending":
                                self.console.print(".", end="", style="dim")
                                continue
                            elif error_type == "slow_down":
                                interval += 5  # Increase polling interval
                                self.console.print("⏳", end="", style="yellow")
                                continue
                            elif error_type == "invalid_grant":
                                if "device_code" in error_description.lower():
                                    self.console.print(f"\n[red]❌ Device code expired or invalid. Please try again.[/red]")
                                else:
                                    self.console.print(f"\n[red]❌ Error: {error_description}[/red]")
                                return None
                            else:
                                self.console.print(f"\n[red]❌ Error: {error_description}[/red]")
                                if logger.isEnabledFor(logging.INFO):
                                    self.console.print(f"[red]   Response: {token_response.text}[/red]")
                                return None
                        except json.JSONDecodeError:
                            self.console.print(f"\n[red]❌ HTTP {token_response.status_code}: {token_response.text}[/red]")
                            return None
                            
                except requests.RequestException as e:
                    logger.error(f"Token request error: {e}")
                    self.console.print("⚠", end="", style="yellow")
                    
                # Wait before next poll
                time.sleep(interval)
            
            self.console.print(f"\n[red]❌ Authorization timed out[/red]")
            return None
            
        except requests.RequestException as e:
            self.console.print(f"[red]❌ Network error: {e}[/red]")
            logger.error(f"Device flow auth network error: {e}")
            return None
        except KeyError as e:
            self.console.print(f"[red]❌ Invalid response format: missing {e}[/red]")
            logger.error(f"Device flow auth response error: {e}")
            return None
        except Exception as e:
            self.console.print(f"[red]❌ Unexpected error: {e}[/red]")
            logger.error(f"Device flow auth unexpected error: {e}")
            return None
    
    def get_token(self, force_reauth=False):
        """Get a valid token, either from cache or by performing device flow."""
        if not force_reauth:
            # Try to get cached token first
            cached_token = self.get_cached_token()
            if cached_token:
                logger.info("Using cached token")
                return cached_token
        
        # Perform device flow authentication (project selected during web auth)
        return self.device_flow_auth()
    
    def logout(self):
        """Clear stored authentication."""
        self.clear_token()
        self.console.print("[green]✅ Successfully logged out[/green]")
