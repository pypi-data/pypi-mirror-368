#!/usr/bin/env python3
"""
WorldQuant BRAIN MCP Server - Python Version
A comprehensive Model Context Protocol (MCP) server for WorldQuant BRAIN platform integration.
"""

import json
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import os
import sys
from time import sleep

import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, EmailStr

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pydantic models for type safety
class AuthCredentials(BaseModel):
    email: EmailStr
    password: str

class SimulationSettings(BaseModel):
    instrumentType: str = "EQUITY"
    region: str = "USA"
    universe: str = "TOP3000"
    delay: int = 1
    decay: float = 0.0
    neutralization: str = "NONE"
    truncation: float = 0.0
    maxTrade: Optional[str] = None
    pasteurization: Optional[str] = None
    testPeriod: str = "P1Y6M"
    unitHandling: str = "NONE"
    nanHandling: str = "NONE"
    language: str = "FASTEXPR"
    visualization: bool = True

class SimulationData(BaseModel):
    type: str = "REGULAR"  # "REGULAR" or "SUPER"
    settings: {SimulationSettings} 
    regular: Optional[str] = None
    combo: Optional[str] = None
    selection: Optional[str] = None

class BrainApiClient:
    """WorldQuant BRAIN API client with comprehensive functionality."""
    
    def __init__(self):
        self.base_url = "https://api.worldquantbrain.com"
        self.session = requests.Session()
        self.auth_credentials = None
        self.is_authenticating = False
        
        # Configure session
        self.session.timeout = 30
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def log(self, message: str, level: str = "INFO"):
        """Log messages to stderr to avoid MCP protocol interference."""
        print(f"[{level}] {message}", file=sys.stderr)
    
    async def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate with WorldQuant BRAIN platform using Basic Authentication."""
        self.log("🔐 Starting Basic Authentication process...", "INFO")
        
        try:
            # Store credentials for potential re-authentication
            self.auth_credentials = {'email': email, 'password': password}
            
            # Clear any existing session data
            self.session.cookies.clear()
            self.session.auth = None
            
            # Create Basic Authentication header (base64 encoded credentials)
            import base64
            credentials = f"{email}:{password}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            # Send POST request with Basic Authentication header
            headers = {
                'Authorization': f'Basic {encoded_credentials}'
            }
            
            response = self.session.post('https://api.worldquantbrain.com/authentication', headers=headers)
            
            # Check for successful authentication (status code 201)
            if response.status_code == 201:
                self.log("✅ Basic Authentication successful", "SUCCESS")
                
                # Check if JWT token was automatically stored by session
                jwt_token = self.session.cookies.get('t')
                if jwt_token:
                    self.log("✅ JWT token automatically stored by session", "SUCCESS")
                else:
                    self.log("⚠️ No JWT token found in session", "WARNING")
                
                # Return success response
                return {
                    'user': {'email': email},
                    'status': 'authenticated',
                    'permissions': ['read', 'write'],
                    'message': 'Basic Authentication successful',
                    'status_code': response.status_code,
                    'has_jwt': jwt_token is not None
                }
            else:
                raise Exception(f"Authentication failed with status code: {response.status_code}")
                    
        except requests.HTTPError as e:
            self.log(f"❌ HTTP error during authentication: {e}", "ERROR")
            raise
        except Exception as e:
            self.log(f"❌ Authentication failed: {str(e)}", "ERROR")
            raise
    
    async def is_authenticated(self) -> bool:
        """Check if currently authenticated using JWT token."""
        try:
            # Check if we have a JWT token in cookies
            jwt_token = self.session.cookies.get('t')
            if not jwt_token:
                self.log("❌ No JWT token found", "INFO")
                return False
            
            # Test authentication with a simple API call
            response = self.session.get(f"{self.base_url}/authentication")
            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                self.log("❌ JWT token expired or invalid (401)", "INFO")
                return False
            else:
                self.log(f"⚠️ Unexpected status code during auth check: {response.status_code}", "WARNING")
                return False
        except Exception as e:
            self.log(f"❌ Error checking authentication: {str(e)}", "ERROR")
            return False
    
    async def ensure_authenticated(self):
        """Ensure authentication is valid, re-authenticate if needed."""
        if not await self.is_authenticated() and self.auth_credentials:
            self.log("🔄 Re-authenticating...", "INFO")
            await self.authenticate(self.auth_credentials['email'], self.auth_credentials['password'])
        elif not self.auth_credentials:
            raise Exception("Not authenticated and no stored credentials available. Please call authenticate() first.")
    
    async def get_authentication_status(self) -> Optional[Dict[str, Any]]:
        """Get current authentication status and user info."""
        try:
            response = self.session.get(f"{self.base_url}/users/self")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get auth status: {str(e)}", "ERROR")
            return None
    
    async def create_simulation(self, simulation_data: SimulationData) -> Dict[str, str]:
        """Create a new simulation on BRAIN platform."""
        await self.ensure_authenticated()
        
        try:
            self.log("🚀 Creating simulation...", "INFO")
            
            # Prepare simulation payload
            payload = {
                'type': simulation_data.type,
                'settings': simulation_data.settings.dict(),
                'regular': simulation_data.regular,
                'combo': simulation_data.combo,
                'selection': simulation_data.selection
            }
            
            response = self.session.post(f"{self.base_url}/simulations", json=payload)
            response.raise_for_status()
            
            result = response.json()
            simulation_id = result.get('id')
            location = result.get('location', '')
            
            self.log(f"✅ Simulation created with ID: {simulation_id}", "SUCCESS")
            return {'simulationId': simulation_id, 'location': location}
            
        except Exception as e:
            self.log(f"❌ Failed to create simulation: {str(e)}", "ERROR")
            raise
    
    async def get_simulation_status(self, simulation_id: str) -> Dict[str, Any]:
        """Get the status of a simulation."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/simulations/{simulation_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get simulation status: {str(e)}", "ERROR")
            raise
    
    async def wait_for_simulation_completion(self, simulation_id: str, max_wait_time: int = 300) -> Dict[str, Any]:
        """Wait for simulation to complete."""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status = await self.get_simulation_status(simulation_id)
            
            if status.get('status') in ['COMPLETE', 'ERROR', 'TIMEOUT', 'FAIL']:
                return status
            
            self.log(f"⏳ Simulation {simulation_id} status: {status.get('status')}", "INFO")
            await asyncio.sleep(10)
        
        raise Exception(f"Simulation {simulation_id} timed out after {max_wait_time} seconds")
    
    async def get_alpha_details(self, alpha_id: str) -> Dict[str, Any]:
        """Get detailed information about an alpha."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/alphas/{alpha_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get alpha details: {str(e)}", "ERROR")
            raise
    
    async def get_datasets(self, instrument_type: str = "EQUITY", region: str = "USA", 
                          delay: int = 1, universe: str = "TOP3000", theme: str = "false") -> Dict[str, Any]:
        """Get available datasets."""
        await self.ensure_authenticated()
        
        try:
            params = {
                'instrumentType': instrument_type,
                'region': region,
                'delay': delay,
                'universe': universe,
                'theme': theme
            }
            
            response = self.session.get(f"{self.base_url}/data-sets", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get datasets: {str(e)}", "ERROR")
            raise
    
    async def get_datafields(self, instrument_type: str = "EQUITY", region: str = "USA",
                            delay: int = 1, universe: str = "TOP3000", theme: str = "false",
                            dataset_id: Optional[str] = None, data_type: str = "MATRIX",
                            search: Optional[str] = None) -> Dict[str, Any]:
        """Get available data fields."""
        await self.ensure_authenticated()
        
        try:
            params = {
                'instrumentType': instrument_type,
                'region': region,
                'delay': delay,
                'universe': universe,
                'limit': '50',
                'offset': '0'
            }
            
            if data_type != 'ALL':
                params['type'] = data_type
            
            if dataset_id:
                params['dataset.id'] = dataset_id
            if search:
                params['search'] = search
            
            response = self.session.get(f"{self.base_url}/data-fields", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get datafields: {str(e)}", "ERROR")
            raise
    
    async def get_alpha_pnl(self, alpha_id: str, pnl_type: str = "pnl") -> Dict[str, Any]:
        """Get PnL data for an alpha."""
        await self.ensure_authenticated()
        
        try:
            params = {'type': pnl_type}
            response = self.session.get(f"{self.base_url}/alphas/{alpha_id}/recordsets/{pnl_type}", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get alpha PnL: {str(e)}", "ERROR")
            raise
    
    async def get_user_alphas(self, stage: str = "IS", limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get user's alphas."""
        await self.ensure_authenticated()
        
        try:
            params = {
                'stage': stage,
                'limit': limit,
                'offset': offset
            }
            
            response = self.session.get(f"{self.base_url}/users/self/alphas", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get user alphas: {str(e)}", "ERROR")
            raise
    
    async def submit_alpha(self, alpha_id: str) -> bool:
        """Submit an alpha for production."""
        await self.ensure_authenticated()
        
        try:
            self.log(f"📤 Submitting alpha {alpha_id} for production...", "INFO")
            
            response = self.session.post(f"{self.base_url}/alphas/{alpha_id}/submit")
            response.raise_for_status()
            
            self.log(f"✅ Alpha {alpha_id} submitted successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to submit alpha: {str(e)}", "ERROR")
            return False
    
    async def get_events(self) -> Dict[str, Any]:
        """Get available events and competitions."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/events")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get events: {str(e)}", "ERROR")
            raise
    
    async def get_leaderboard(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get leaderboard data."""
        await self.ensure_authenticated()
        
        try:
            params = {}
            
            if user_id:
                params['user'] = user_id
            else:
                # Get current user ID if not specified
                user_response = self.session.get(f"{self.base_url}/users/self")
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    params['user'] = user_data.get('id')
            
            response = self.session.get(f"{self.base_url}/consultant/boards/leader", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get leaderboard: {str(e)}", "ERROR")
            raise

    async def get_operators(self) -> Dict[str, Any]:
        """Get available operators for alpha creation."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/operators")
            response.raise_for_status()
            operators_data = response.json()
            
            # Ensure we return a dictionary format even if API returns a list
            if isinstance(operators_data, list):
                return {"operators": operators_data, "count": len(operators_data)}
            else:
                return operators_data
        except Exception as e:
            self.log(f"Failed to get operators: {str(e)}", "ERROR")
            raise

    async def run_selection(
        self, 
        selection: str, 
        instrument_type: str = "EQUITY",
        region: str = "USA", 
        delay: int = 1,
        selection_limit: int = 1000,
        selection_handling: str = "POSITIVE"
    ) -> Dict[str, Any]:
        """Run a selection query to filter instruments."""
        await self.ensure_authenticated()
        
        try:
            data = {
                "selection": selection,
                "instrumentType": instrument_type,
                "region": region,
                "delay": delay,
                "selectionLimit": selection_limit,
                "selectionHandling": selection_handling
            }
            
            response = self.session.post(f"{self.base_url}/selection", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to run selection: {str(e)}", "ERROR")
            raise

    async def get_user_profile(self, user_id: str = "self") -> Dict[str, Any]:
        """Get user profile information."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/users/{user_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get user profile: {str(e)}", "ERROR")
            raise

    async def get_tutorials(self) -> Dict[str, Any]:
        """Get available tutorials and learning materials."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/tutorials")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get tutorials: {str(e)}", "ERROR")
            raise

    async def get_messages_summary(self) -> Dict[str, Any]:
        """Get summary of user messages and notifications."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/users/self/messages/summary")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get messages summary: {str(e)}", "ERROR")
            raise

    async def get_messages(self) -> Dict[str, Any]:
        """Get all messages for the current user."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/users/self/messages")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get messages: {str(e)}", "ERROR")
            raise

    async def get_glossary_terms(self, email: str, password: str, headless: bool = False) -> Dict[str, Any]:
        """Get glossary terms from forum."""
        try:
            # Import and use forum functions
            from forum_functions import forum_client
            return await forum_client.get_glossary_terms(email, password, headless)
        except ImportError:
            self.log("Forum functions not available - install selenium and run forum_functions.py", "WARNING")
            return {"error": "Forum functions require selenium. Use forum_functions.py directly."}
        except Exception as e:
            self.log(f"Glossary extraction failed: {str(e)}", "ERROR")
            return {"error": str(e)}

    async def search_forum_posts(self, email: str, password: str, search_query: str, 
                               max_results: int = 50, headless: bool = True) -> Dict[str, Any]:
        """Search forum posts."""
        try:
            # Import and use forum functions
            from forum_functions import forum_client
            return await forum_client.search_forum_posts(email, password, search_query, max_results, headless)
        except ImportError:
            self.log("Forum functions not available - install selenium and run forum_functions.py", "WARNING")
            return {"error": "Forum functions require selenium. Use forum_functions.py directly."}
        except Exception as e:
            self.log(f"Forum search failed: {str(e)}", "ERROR")
            return {"error": str(e)}

    async def get_forum_post(self, email: str, password: str, article_id: str, 
                           headless: bool = False) -> Dict[str, Any]:
        """Get forum post."""
        try:
            # Import and use forum functions
            from forum_functions import forum_client
            return await forum_client.read_full_forum_post(email, password, article_id, headless, include_comments=True)
        except ImportError:
            self.log("Forum functions not available - install selenium and run forum_functions.py", "WARNING")
            return {"error": "Forum functions require selenium. Use forum_functions.py directly."}
        except Exception as e:
            self.log(f"Forum post retrieval failed: {str(e)}", "ERROR")
            return {"error": str(e)}

    async def get_alpha_yearly_stats(self, alpha_id: str) -> Dict[str, Any]:
        """Get yearly statistics for an alpha."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/alphas/{alpha_id}/recordsets/yearly-stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get alpha yearly stats: {str(e)}", "ERROR")
            raise

    async def get_production_correlation(self, alpha_id: str) -> Dict[str, Any]:
        """Get production correlation data for an alpha."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/alphas/{alpha_id}/recordsets/production-correlation")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get production correlation: {str(e)}", "ERROR")
            raise

    async def get_self_correlation(self, alpha_id: str) -> Dict[str, Any]:
        """Get self-correlation data for an alpha."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/alphas/{alpha_id}/recordsets/self-correlation")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get self correlation: {str(e)}", "ERROR")
            raise

    async def check_production_correlation(self, alpha_id: str, threshold: float = 0.7) -> Dict[str, Any]:
        """Validate alpha uniqueness vs production alphas."""
        await self.ensure_authenticated()
        
        try:
            correlation_data = await self.get_production_correlation(alpha_id)
            
            # Analyze correlation data
            if correlation_data and 'results' in correlation_data:
                correlations = correlation_data['results']
                max_correlation = max([corr.get('correlation', 0) for corr in correlations]) if correlations else 0
                
                return {
                    'alpha_id': alpha_id,
                    'threshold': threshold,
                    'max_correlation': max_correlation,
                    'passes_check': max_correlation < threshold,
                    'correlation_data': correlation_data
                }
            else:
                return {
                    'alpha_id': alpha_id,
                    'threshold': threshold,
                    'max_correlation': 0,
                    'passes_check': True,
                    'correlation_data': correlation_data
                }
        except Exception as e:
            self.log(f"Failed to check production correlation: {str(e)}", "ERROR")
            raise

    async def check_self_correlation(self, alpha_id: str, threshold: float = 0.7) -> Dict[str, Any]:
        """Check alpha against similar user alphas."""
        await self.ensure_authenticated()
        
        try:
            correlation_data = await self.get_self_correlation(alpha_id)
            
            # Analyze correlation data
            if correlation_data and 'results' in correlation_data:
                correlations = correlation_data['results']
                max_correlation = max([corr.get('correlation', 0) for corr in correlations]) if correlations else 0
                
                return {
                    'alpha_id': alpha_id,
                    'threshold': threshold,
                    'max_correlation': max_correlation,
                    'passes_check': max_correlation < threshold,
                    'correlation_data': correlation_data
                }
            else:
                return {
                    'alpha_id': alpha_id,
                    'threshold': threshold,
                    'max_correlation': 0,
                    'passes_check': True,
                    'correlation_data': correlation_data
                }
        except Exception as e:
            self.log(f"Failed to check self correlation: {str(e)}", "ERROR")
            raise

    async def get_submission_check(self, alpha_id: str) -> Dict[str, Any]:
        """Comprehensive pre-submission check."""
        await self.ensure_authenticated()
        
        try:
            # Get all relevant checks
            production_check = await self.check_production_correlation(alpha_id)
            self_check = await self.check_self_correlation(alpha_id)
            
            # Get alpha details for additional validation
            alpha_details = await self.get_alpha_details(alpha_id)
            
            # Compile comprehensive check results
            checks = {
                'production_correlation': production_check,
                'self_correlation': self_check,
                'alpha_details': alpha_details,
                'all_passed': production_check['passes_check'] and self_check['passes_check']
            }
            
            return checks
        except Exception as e:
            self.log(f"Failed to get submission check: {str(e)}", "ERROR")
            raise

    async def set_alpha_properties(self, alpha_id: str, name: Optional[str] = None, 
                                 color: Optional[str] = None, tags: List[str] = None,
                                 selection_desc: str = "None", combo_desc: str = "None") -> Dict[str, Any]:
        """Update alpha properties (name, color, tags, descriptions)."""
        await self.ensure_authenticated()
        
        try:
            data = {}
            if name:
                data['name'] = name
            if color:
                data['color'] = color
            if tags:
                data['tags'] = tags
            if selection_desc:
                data['selectionDesc'] = selection_desc
            if combo_desc:
                data['comboDesc'] = combo_desc
            
            response = self.session.patch(f"{self.base_url}/alphas/{alpha_id}", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to set alpha properties: {str(e)}", "ERROR")
            raise

    async def get_record_sets(self, alpha_id: str) -> Dict[str, Any]:
        """List available record sets for an alpha."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/alphas/{alpha_id}/recordsets")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get record sets: {str(e)}", "ERROR")
            raise

    async def get_record_set_data(self, alpha_id: str, record_set_name: str) -> Dict[str, Any]:
        """Get data from a specific record set."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/alphas/{alpha_id}/recordsets/{record_set_name}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get record set data: {str(e)}", "ERROR")
            raise

    async def get_user_activities(self, user_id: str, grouping: Optional[str] = None) -> Dict[str, Any]:
        """Get user activity diversity data."""
        await self.ensure_authenticated()
        
        try:
            params = {}
            if grouping:
                params['grouping'] = grouping
            
            response = self.session.get(f"{self.base_url}/users/{user_id}/activities", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get user activities: {str(e)}", "ERROR")
            raise

    async def get_pyramid_multipliers(self, region: Optional[str] = None, delay: Optional[int] = None, 
                                    category: Optional[str] = None) -> Dict[str, Any]:
        """Get current pyramid multipliers showing BRAIN's encouragement levels."""
        await self.ensure_authenticated()
        
        try:
            params = {}
            if region:
                params['region'] = region
            if delay is not None:
                params['delay'] = delay
            if category:
                params['category'] = category
            
            response = self.session.get(f"{self.base_url}/pyramid/multipliers", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get pyramid multipliers: {str(e)}", "ERROR")
            raise

    async def get_pyramid_alphas(self, region: Optional[str] = None, delay: Optional[int] = None,
                               category: Optional[str] = None, start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get user's current alpha distribution across pyramid categories."""
        await self.ensure_authenticated()
        
        try:
            params = {}
            if region:
                params['region'] = region
            if delay is not None:
                params['delay'] = delay
            if category:
                params['category'] = category
            if start_date:
                params['startDate'] = start_date
            if end_date:
                params['endDate'] = end_date
            
            response = self.session.get(f"{self.base_url}/pyramid/alphas", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get pyramid alphas: {str(e)}", "ERROR")
            raise

    async def get_user_competitions(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get list of competitions that the user is participating in."""
        await self.ensure_authenticated()
        
        try:
            if not user_id:
                # Get current user ID if not specified
                user_response = self.session.get(f"{self.base_url}/users/self")
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    user_id = user_data.get('id')
                else:
                    user_id = 'self'
            
            response = self.session.get(f"{self.base_url}/users/{user_id}/competitions")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get user competitions: {str(e)}", "ERROR")
            raise

    async def get_competition_details(self, competition_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific competition."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/competitions/{competition_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get competition details: {str(e)}", "ERROR")
            raise

    async def get_competition_agreement(self, competition_id: str) -> Dict[str, Any]:
        """Get the rules, terms, and agreement for a specific competition."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/competitions/{competition_id}/agreement")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get competition agreement: {str(e)}", "ERROR")
            raise

    async def get_instrument_options(self) -> Dict[str, Any]:
        """Get available instrument types, regions, delays, and universes."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/instrument-options")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get instrument options: {str(e)}", "ERROR")
            raise

    async def performance_comparison(self, alpha_id: str, team_id: Optional[str] = None, 
                                   competition: Optional[str] = None) -> Dict[str, Any]:
        """Get performance comparison data for an alpha."""
        await self.ensure_authenticated()
        
        try:
            params = {}
            if team_id:
                params['team_id'] = team_id
            if competition:
                params['competition'] = competition
            
            response = self.session.get(f"{self.base_url}/alphas/{alpha_id}/performance-comparison", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get performance comparison: {str(e)}", "ERROR")
            raise

    async def combine_test_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate test results across multiple alphas to identify patterns."""
        try:
            combined_results = {
                'total_alphas': len(results),
                'test_summary': {},
                'common_issues': [],
                'validation_patterns': {}
            }
            
            # Analyze test results
            for result in results:
                alpha_id = result.get('alpha_id', 'unknown')
                test_data = result.get('test_results', {})
                
                # Collect validation patterns
                for test_type, test_result in test_data.items():
                    if test_type not in combined_results['validation_patterns']:
                        combined_results['validation_patterns'][test_type] = {
                            'passed': 0,
                            'failed': 0,
                            'alphas': []
                        }
                    
                    if test_result.get('passed', False):
                        combined_results['validation_patterns'][test_type]['passed'] += 1
                    else:
                        combined_results['validation_patterns'][test_type]['failed'] += 1
                        combined_results['validation_patterns'][test_type]['alphas'].append(alpha_id)
            
            # Identify common issues
            for test_type, pattern in combined_results['validation_patterns'].items():
                if pattern['failed'] > 0:
                    combined_results['common_issues'].append({
                        'test_type': test_type,
                        'failed_count': pattern['failed'],
                        'failed_alphas': pattern['alphas']
                    })
            
            return combined_results
        except Exception as e:
            self.log(f"Failed to combine test results: {str(e)}", "ERROR")
            raise

    async def expand_nested_data(self, data: List[Dict[str, Any]], preserve_original: bool = True) -> List[Dict[str, Any]]:
        """Flatten complex nested data structures into tabular format."""
        try:
            expanded_data = []
            
            for item in data:
                expanded_item = {}
                
                for key, value in item.items():
                    if isinstance(value, dict):
                        # Expand nested dictionary
                        for nested_key, nested_value in value.items():
                            expanded_key = f"{key}_{nested_key}"
                            expanded_item[expanded_key] = nested_value
                        
                        # Preserve original if requested
                        if preserve_original:
                            expanded_item[key] = value
                    elif isinstance(value, list):
                        # Handle list values
                        expanded_item[key] = str(value) if value else []
                        
                        # Preserve original if requested
                        if preserve_original:
                            expanded_item[key] = value
                    else:
                        # Simple value
                        expanded_item[key] = value
                
                expanded_data.append(expanded_item)
            
            return expanded_data
        except Exception as e:
            self.log(f"Failed to expand nested data: {str(e)}", "ERROR")
            raise

    async def generate_alpha_links(self, alpha_ids: List[str], base_url: str = "https://platform.worldquantbrain.com") -> Dict[str, Any]:
        """Create clickable HTML links to BRAIN platform alphas."""
        try:
            links = {
                'base_url': base_url,
                'alpha_links': [],
                'html_output': '',
                'markdown_output': ''
            }
            
            html_links = []
            markdown_links = []
            
            for alpha_id in alpha_ids:
                alpha_url = f"{base_url}/alphas/{alpha_id}"
                
                # Create HTML link
                html_link = f'<a href="{alpha_url}" target="_blank">Alpha {alpha_id}</a>'
                html_links.append(html_link)
                
                # Create Markdown link
                markdown_link = f'[Alpha {alpha_id}]({alpha_url})'
                markdown_links.append(markdown_link)
                
                links['alpha_links'].append({
                    'alpha_id': alpha_id,
                    'url': alpha_url,
                    'html_link': html_link,
                    'markdown_link': markdown_link
                })
            
            # Generate combined outputs
            links['html_output'] = '<br>'.join(html_links)
            links['markdown_output'] = '\n'.join(markdown_links)
            
            return links
        except Exception as e:
            self.log(f"Failed to generate alpha links: {str(e)}", "ERROR")
            raise

    async def get_tutorial_page(self, page_id: str) -> Dict[str, Any]:
        """Retrieve detailed content of a specific tutorial page/article."""
        await self.ensure_authenticated()
        
        try:
            response = self.session.get(f"{self.base_url}/tutorial-pages/{page_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Failed to get tutorial page: {str(e)}", "ERROR")
            raise

    # Badge status function removed as requested

# Initialize MCP server
mcp = FastMCP('brain_mcp_server')

# Initialize API client
brain_client = BrainApiClient()

# Configuration management
CONFIG_FILE = "user_config.json"

def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
    return {}

def load_brain_credentials() -> Optional[tuple]:
    """Load credentials from .brain_credentials file in home directory."""
    try:
        from os.path import expanduser
        credentials_file = expanduser('~/.brain_credentials')
        if os.path.exists(credentials_file):
            with open(credentials_file, 'r') as f:
                credentials = json.load(f)
                if isinstance(credentials, list) and len(credentials) == 2:
                    return tuple(credentials)
    except Exception as e:
        logger.error(f"Failed to load .brain_credentials: {e}")
    return None

def save_config(config: Dict[str, Any]):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save config: {e}")

# MCP Tools

@mcp.tool()
async def authenticate(email: str = "", password: str = "") -> Dict[str, Any]:
    """
    🔐 Authenticate with WorldQuant BRAIN platform.
    
    This is the first step in any BRAIN workflow. You must authenticate before using any other tools.
    
    Args:
        email: Your BRAIN platform email address (optional if in config or .brain_credentials)
        password: Your BRAIN platform password (optional if in config or .brain_credentials)
    
    Returns:
        Authentication result with user info and permissions
    """
    try:
        # First try to load from .brain_credentials file
        brain_creds = load_brain_credentials()
        if brain_creds and not email and not password:
            email, password = brain_creds
            print(f"📧 Using credentials from .brain_credentials file: {email}")
        
        # If still no credentials, try config file
        if not email or not password:
            config = load_config()
            if 'credentials' in config:
                if not email:
                    email = config['credentials'].get('email', '')
                if not password:
                    password = config['credentials'].get('password', '')
        
        if not email or not password:
            return {"error": "Email and password required. Either provide them as arguments, configure them in user_config.json, or create a .brain_credentials file in your home directory with format: [\"email\", \"password\"]"}
        
        result = await brain_client.authenticate(email, password)
        
        # Save credentials to config for future use
        config = load_config()
        if 'credentials' not in config:
            config['credentials'] = {}
        config['credentials']['email'] = email
        config['credentials']['password'] = password
        save_config(config)
        
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_config() -> Dict[str, Any]:
    """
    🔧 Get current configuration settings.
    
    Returns:
        Current configuration including authentication status
    """
    config = load_config()
    auth_status = await brain_client.get_authentication_status()
    
    return {
        "config": config,
        "auth_status": auth_status,
        "is_authenticated": await brain_client.is_authenticated()
    }

@mcp.tool()
async def set_config(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    🔧 Update configuration settings.
    
    Args:
        settings: Configuration settings to update
    
    Returns:
        Updated configuration
    """
    config = load_config()
    config.update(settings)
    save_config(config)
    return config

@mcp.tool()
async def create_simulation(
    type: str = "REGULAR",
    instrument_type: str = "EQUITY",
    region: str = "USA",
    universe: str = "TOP3000",
    delay: int = 1,
    decay: float = 0.0,
    neutralization: str = "NONE",
    truncation: float = 0.0,
    test_period: str = "P1Y6M",
    unit_handling: str = "NONE",
    nan_handling: str = "NONE",
    language: str = "FASTEXPR",
    visualization: bool = True,
    regular: Optional[str] = None,
    combo: Optional[str] = None,
    selection: Optional[str] = None
) -> Dict[str, Any]:
    """
    🚀 Create a new simulation on BRAIN platform.
    
    This tool creates and starts a simulation with your alpha code. Use this after you have your alpha formula ready.
    
    Args:
        type: Simulation type ("REGULAR" or "SUPER")
        instrument_type: Type of instruments (e.g., "EQUITY")
        region: Market region (e.g., "USA")
        universe: Universe of stocks (e.g., "TOP3000")
        delay: Data delay (0 or 1)
        decay: Decay value for the simulation
        neutralization: Neutralization method
        truncation: Truncation value
        test_period: Test period (e.g., "P1Y6M" for 1 year 6 months)
        unit_handling: Unit handling method
        nan_handling: NaN handling method
        language: Expression language (e.g., "FASTEXPR")
        visualization: Enable visualization
        regular: Regular simulation code (for REGULAR type)
        combo: Combo code (for SUPER type)
        selection: Selection code (for SUPER type)
    
    Returns:
        Simulation creation result with ID and location
    """
    try:
        settings = SimulationSettings(
            instrumentType=instrument_type,
            region=region,
            universe=universe,
            delay=delay,
            decay=decay,
            neutralization=neutralization,
            truncation=truncation,
            testPeriod=test_period,
            unitHandling=unit_handling,
            nanHandling=nan_handling,
            language=language,
            visualization=visualization
        )
        
        simulation_data = SimulationData(
            type=type,
            settings=settings,
            regular=regular,
            combo=combo,
            selection=selection
        )
        
        result = await brain_client.create_simulation(simulation_data)
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_simulation_status(simulation_id: str) -> Dict[str, Any]:
    """
    📊 Get the current status of a simulation.
    
    Use this to check if your simulation is complete or still running.
    
    Args:
        simulation_id: The ID of the simulation to check
    
    Returns:
        Current simulation status and details
    """
    try:
        return await brain_client.get_simulation_status(simulation_id)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def wait_for_simulation(simulation_id: str, max_wait_time: int = 300) -> Dict[str, Any]:
    """
    ⏳ Wait for simulation to complete.
    
    This tool will poll the simulation status until it completes or times out.
    
    Args:
        simulation_id: The ID of the simulation to wait for
        max_wait_time: Maximum time to wait in seconds (default: 300)
    
    Returns:
        Final simulation result
    """
    try:
        return await brain_client.wait_for_simulation_completion(simulation_id, max_wait_time)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_alpha_details(alpha_id: str) -> Dict[str, Any]:
    """
    📋 Get detailed information about an alpha.
    
    Args:
        alpha_id: The ID of the alpha to retrieve
    
    Returns:
        Detailed alpha information
    """
    try:
        return await brain_client.get_alpha_details(alpha_id)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_datasets(
    instrument_type: str = "EQUITY",
    region: str = "USA",
    delay: int = 1,
    universe: str = "TOP3000",
    theme: str = "false",
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    📚 Get available datasets for research.
    
    Use this to discover what data is available for your alpha research.
    
    Args:
        instrument_type: Type of instruments (e.g., "EQUITY")
        region: Market region (e.g., "USA")
        delay: Data delay (0 or 1)
        universe: Universe of stocks (e.g., "TOP3000")
        theme: Theme filter
    
    Returns:
        Available datasets
    """
    try:
        return await brain_client.get_datasets(instrument_type, region, delay, universe, theme,search)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_datafields(
    instrument_type: str = "EQUITY",
    region: str = "USA",
    delay: int = 1,
    universe: str = "TOP3000",
    theme: str = "false",
    dataset_id: Optional[str] = None,
    data_type: str = "MATRIX",
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    🔍 Get available data fields for alpha construction.
    
    Use this to find specific data fields you can use in your alpha formulas.
    
    Args:
        instrument_type: Type of instruments (e.g., "EQUITY")
        region: Market region (e.g., "USA")
        delay: Data delay (0 or 1)
        universe: Universe of stocks (e.g., "TOP3000")
        theme: Theme filter
        dataset_id: Specific dataset ID to filter by
        data_type: Type of data (e.g., "MATRIX")
        search: Search term to filter fields
    
    Returns:
        Available data fields
    """
    try:
        return await brain_client.get_datafields(
            instrument_type, region, delay, universe, theme, 
            dataset_id, data_type, search
        )
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_alpha_pnl(alpha_id: str, pnl_type: str = "pnl") -> Dict[str, Any]:
    """
    📈 Get PnL (Profit and Loss) data for an alpha.
    
    Args:
        alpha_id: The ID of the alpha
        pnl_type: Type of PnL data ("pnl" for cumulative, "daily-pnl" for daily)
    
    Returns:
        PnL data for the alpha
    """
    try:
        return await brain_client.get_alpha_pnl(alpha_id, pnl_type)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_user_alphas(stage: str = "IS", limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """
    👤 Get user's alphas.
    
    Args:
        stage: Alpha stage ("IS" for in-sample, "OS" for out-of-sample)
        limit: Maximum number of alphas to return
        offset: Offset for pagination
    
    Returns:
        User's alphas
    """
    try:
        return await brain_client.get_user_alphas(stage, limit, offset)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def submit_alpha(alpha_id: str) -> Dict[str, Any]:
    """
    📤 Submit an alpha for production.
    
    Use this when your alpha is ready for production deployment.
    
    Args:
        alpha_id: The ID of the alpha to submit
    
    Returns:
        Submission result
    """
    try:
        success = await brain_client.submit_alpha(alpha_id)
        return {"success": success, "alpha_id": alpha_id}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_events() -> Dict[str, Any]:
    """
    🏆 Get available events and competitions.
    
    Returns:
        Available events and competitions
    """
    try:
        return await brain_client.get_events()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_leaderboard(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    🏅 Get leaderboard data.
    
    Args:
        user_id: Optional user ID to filter results
    
    Returns:
        Leaderboard data
    """
    try:
        return await brain_client.get_leaderboard(user_id)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def batch_process_alphas(alpha_ids: List[str], operation: str) -> Dict[str, Any]:
    """
    🔄 Process multiple alphas in batch.
    
    Args:
        alpha_ids: List of alpha IDs to process
        operation: Operation to perform ("submit", "delete", etc.)
    
    Returns:
        Batch processing results
    """
    try:
        results = []
        for alpha_id in alpha_ids:
            if operation == "submit":
                success = await brain_client.submit_alpha(alpha_id)
                results.append({"alpha_id": alpha_id, "success": success})
            # Add more operations as needed
        
        return {"results": results, "total_processed": len(alpha_ids)}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def save_simulation_data(simulation_id: str, filename: str) -> Dict[str, Any]:
    """
    💾 Save simulation data to a file.
    
    Args:
        simulation_id: The simulation ID
        filename: Filename to save the data
    
    Returns:
        Save operation result
    """
    try:
        # Get simulation data
        simulation_data = await brain_client.get_simulation_status(simulation_id)
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(simulation_data, f, indent=2)
        
        return {"success": True, "filename": filename, "simulation_id": simulation_id}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def analyze_alpha_performance(alpha_id: str) -> Dict[str, Any]:
    """
    📊 Comprehensive alpha performance analysis.
    
    Args:
        alpha_id: The alpha ID to analyze
    
    Returns:
        Comprehensive performance analysis
    """
    try:
        # Get alpha details
        alpha_details = await brain_client.get_alpha_details(alpha_id)
        
        # Get PnL data
        pnl_data = await brain_client.get_alpha_pnl(alpha_id)
        
        # Get yearly stats if available
        yearly_stats = await brain_client.get_alpha_yearly_stats(alpha_id)
        
        return {
            "alpha_details": alpha_details,
            "pnl_data": pnl_data,
            "yearly_stats": yearly_stats,
            "analysis_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_operators() -> Dict[str, Any]:
    """
    🔧 Get available operators for alpha creation.
    
    Returns:
        Dictionary containing operators list and count
    """
    try:
        return await brain_client.get_operators()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def run_selection(
    selection: str,
    instrument_type: str = "EQUITY",
    region: str = "USA",
    delay: int = 1,
    selection_limit: int = 1000,
    selection_handling: str = "POSITIVE"
) -> Dict[str, Any]:
    """
    🎯 Run a selection query to filter instruments.
    
    Args:
        selection: Selection criteria
        instrument_type: Type of instruments
        region: Geographic region
        delay: Delay setting
        selection_limit: Maximum number of results
        selection_handling: How to handle selection results
    
    Returns:
        Selection results
    """
    try:
        return await brain_client.run_selection(
            selection, instrument_type, region, delay, selection_limit, selection_handling
        )
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_user_profile(user_id: str = "self") -> Dict[str, Any]:
    """
    👤 Get user profile information.
    
    Args:
        user_id: User ID (default: "self" for current user)
    
    Returns:
        User profile data
    """
    try:
        return await brain_client.get_user_profile(user_id)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_tutorials() -> Dict[str, Any]:
    """
    📚 Get available tutorials and learning materials.
    
    Returns:
        List of tutorials
    """
    try:
        return await brain_client.get_tutorials()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_messages_summary() -> Dict[str, Any]:
    """
    💬 Get summary of user messages and notifications.
    
    Returns:
        Messages summary
    """
    try:
        return await brain_client.get_messages_summary()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_messages() -> Dict[str, Any]:
    """
    💬 Get all messages for the current user.
    
    Returns:
        All messages for the current user.
    """
    try:
        return await brain_client.get_messages()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_glossary_terms(email: str = "", password: str = "", headless: bool = False) -> Dict[str, Any]:
    """
    📚 Get glossary terms from WorldQuant BRAIN forum.
    
    Note: This requires Selenium and is implemented in forum_functions.py
    
    Args:
        email: Your BRAIN platform email address (optional if in config)
        password: Your BRAIN platform password (optional if in config)
        headless: Run browser in headless mode (default: False)
    
    Returns:
        Glossary terms with definitions
    """
    try:
        # Load config to get credentials if not provided
        config = load_config()
        
        # Use provided credentials or fall back to config
        if not email and 'credentials' in config:
            email = config['credentials'].get('email', '')
        if not password and 'credentials' in config:
            password = config['credentials'].get('password', '')
        
        if not email or not password:
            return {"error": "Email and password required. Either provide them as arguments or configure them in user_config.json"}
        
        return await brain_client.get_glossary_terms(email, password, headless)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def search_forum_posts(search_query: str, email: str = "", password: str = "", 
                           max_results: int = 50, headless: bool = True) -> Dict[str, Any]:
    """
    🔍 Search forum posts on WorldQuant BRAIN support site.
    
    Note: This requires Selenium and is implemented in forum_functions.py
    
    Args:
        email: Your BRAIN platform email address (optional if in config)
        password: Your BRAIN platform password (optional if in config)
        search_query: Search term or phrase
        max_results: Maximum number of results to return (default: 50)
        headless: Run browser in headless mode (default: True)
    
    Returns:
        Search results with analysis
    """
    try:
        # Load config to get credentials if not provided
        config = load_config()
        
        # Use provided credentials or fall back to config
        if not email and 'credentials' in config:
            email = config['credentials'].get('email', '')
        if not password and 'credentials' in config:
            password = config['credentials'].get('password', '')
        
        if not email or not password:
            return {"error": "Email and password required. Either provide them as arguments or configure them in user_config.json"}
        
        return await brain_client.search_forum_posts(email, password, search_query, max_results, headless)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_forum_post(article_id: str, email: str = "", password: str = "", 
                        headless: bool = False) -> Dict[str, Any]:
    """
    📄 Get a specific forum post by article ID.
    
    Note: This requires Selenium and is implemented in forum_functions.py
    
    Args:
        article_id: The article ID to retrieve (e.g., "32984819083415-新人求模板")
        email: Your BRAIN platform email address (optional if in config)
        password: Your BRAIN platform password (optional if in config)
        headless: Run browser in headless mode (default: False)
    
    Returns:
        Forum post content with comments
    """
    try:
        # Load config to get credentials if not provided
        config = load_config()
        
        # Use provided credentials or fall back to config
        if not email and 'credentials' in config:
            email = config['credentials'].get('email', '')
        if not password and 'credentials' in config:
            password = config['credentials'].get('password', '')
        
        if not email or not password:
            return {"error": "Email and password required. Either provide them as arguments or configure them in user_config.json"}
        
        # Import and use forum functions directly
        from forum_functions import forum_client
        return await forum_client.read_full_forum_post(email, password, article_id, headless, include_comments=True)
    except ImportError:
        return {"error": "Forum functions require selenium. Use forum_functions.py directly."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_alpha_yearly_stats(alpha_id: str) -> Dict[str, Any]:
    """Get yearly statistics for an alpha."""
    try:
        return await brain_client.get_alpha_yearly_stats(alpha_id)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def check_production_correlation(alpha_id: str, threshold: float = 0.7) -> Dict[str, Any]:
    """Validate alpha uniqueness vs production alphas."""
    try:
        return await brain_client.check_production_correlation(alpha_id, threshold)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def check_self_correlation(alpha_id: str, threshold: float = 0.7) -> Dict[str, Any]:
    """Check alpha against similar user alphas."""
    try:
        return await brain_client.check_self_correlation(alpha_id, threshold)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_submission_check(alpha_id: str) -> Dict[str, Any]:
    """Comprehensive pre-submission check."""
    try:
        return await brain_client.get_submission_check(alpha_id)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def set_alpha_properties(alpha_id: str, name: Optional[str] = None, 
                             color: Optional[str] = None, tags: List[str] = None,
                             selection_desc: str = "None", combo_desc: str = "None") -> Dict[str, Any]:
    """Update alpha properties (name, color, tags, descriptions)."""
    try:
        return await brain_client.set_alpha_properties(alpha_id, name, color, tags, selection_desc, combo_desc)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_record_sets(alpha_id: str) -> Dict[str, Any]:
    """List available record sets for an alpha."""
    try:
        return await brain_client.get_record_sets(alpha_id)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_record_set_data(alpha_id: str, record_set_name: str) -> Dict[str, Any]:
    """Get data from a specific record set."""
    try:
        return await brain_client.get_record_set_data(alpha_id, record_set_name)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_user_activities(user_id: str, grouping: Optional[str] = None) -> Dict[str, Any]:
    """Get user activity diversity data."""
    try:
        return await brain_client.get_user_activities(user_id, grouping)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_pyramid_multipliers(region: Optional[str] = None, delay: Optional[int] = None, 
                                category: Optional[str] = None) -> Dict[str, Any]:
    """Get current pyramid multipliers showing BRAIN's encouragement levels."""
    try:
        return await brain_client.get_pyramid_multipliers(region, delay, category)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_pyramid_alphas(region: Optional[str] = None, delay: Optional[int] = None,
                           category: Optional[str] = None, start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> Dict[str, Any]:
    """Get user's current alpha distribution across pyramid categories."""
    try:
        return await brain_client.get_pyramid_alphas(region, delay, category, start_date, end_date)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_user_competitions(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get list of competitions that the user is participating in."""
    try:
        return await brain_client.get_user_competitions(user_id)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_competition_details(competition_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific competition."""
    try:
        return await brain_client.get_competition_details(competition_id)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_competition_agreement(competition_id: str) -> Dict[str, Any]:
    """Get the rules, terms, and agreement for a specific competition."""
    try:
        return await brain_client.get_competition_agreement(competition_id)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_instrument_options() -> Dict[str, Any]:
    """Get available instrument types, regions, delays, and universes."""
    try:
        return await brain_client.get_instrument_options()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def performance_comparison(alpha_id: str, team_id: Optional[str] = None, 
                               competition: Optional[str] = None) -> Dict[str, Any]:
    """Get performance comparison data for an alpha."""
    try:
        return await brain_client.performance_comparison(alpha_id, team_id, competition)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def combine_test_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate test results across multiple alphas to identify patterns."""
    try:
        return await brain_client.combine_test_results(results)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def expand_nested_data(data: List[Dict[str, Any]], preserve_original: bool = True) -> List[Dict[str, Any]]:
    """Flatten complex nested data structures into tabular format."""
    try:
        return await brain_client.expand_nested_data(data, preserve_original)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def generate_alpha_links(alpha_ids: List[str], base_url: str = "https://platform.worldquantbrain.com") -> Dict[str, Any]:
    """Create clickable HTML links to BRAIN platform alphas."""
    try:
        return await brain_client.generate_alpha_links(alpha_ids, base_url)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_tutorial_page(page_id: str) -> Dict[str, Any]:
    """Retrieve detailed content of a specific tutorial page/article."""
    try:
        return await brain_client.get_tutorial_page(page_id)
    except Exception as e:
        return {"error": str(e)}

# Badge status MCP tool removed as requested

if __name__ == "__main__":
    print("🧠 WorldQuant BRAIN MCP Server Starting...", file=sys.stderr)
    mcp.run()