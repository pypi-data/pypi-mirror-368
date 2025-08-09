"""IBM Cloud Deployable Architectures MCP Server"""

import json
import os
import subprocess
from typing import Dict, Any, Optional
from fastmcp import FastMCP

mcp = FastMCP("IBM Cloud DA Catalog")

@mcp.tool()
def get_slz_details() -> str:
    """Get SLZ Landing Zone deployment details: name, description, features, and readme"""
    version_locator = "1082e7d2-5e2f-0a11-a3bc-f88a8e1931fc.c15a99be-f334-4dfe-b1d2-b650ae01c9ca-global"
    
    try:
        result = subprocess.run([
            'ibmcloud', 'catalog', 'offering', 'version', 'get',
            '--vl', version_locator,
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        data = json.loads(result.stdout)
        version = data['kinds'][0]['versions'][0]
        
        # Extract features without i18n
        features = []
        if data.get('features'):
            for feature in data['features']:
                features.append({
                    'title': feature.get('title'),
                    'description': feature.get('description')
                })
        
        # Extract required configuration parameters only
        configuration = []
        if version.get('configuration'):
            for config in version['configuration']:
                if config.get('required'):
                    configuration.append({
                        'key': config.get('key'),
                        'description': config.get('description'),
                        'required': config.get('required'),
                        'default_value': config.get('default_value')
                    })
        
        details = {
            'name': data.get('name'),
            'description': data.get('short_description'),
            'long_description': data.get('long_description'),
            'features': features,
            'architecture_overview': version.get('long_description'),
            'configuration': configuration
        }
        
        return json.dumps(details, indent=2)
        
    except subprocess.CalledProcessError as e:
        return json.dumps({'error': f'CLI error: {e.stderr}'})
    except (KeyError, IndexError) as e:
        return json.dumps({'error': f'Data structure error: {e}'})

@mcp.tool()
def get_required_configs() -> str:
    """Get all required configuration parameters for SLZ deployment"""
    version_locator = "1082e7d2-5e2f-0a11-a3bc-f88a8e1931fc.c15a99be-f334-4dfe-b1d2-b650ae01c9ca-global"
    
    try:
        result = subprocess.run([
            'ibmcloud', 'catalog', 'offering', 'version', 'get',
            '--vl', version_locator,
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        data = json.loads(result.stdout)
        version = data['kinds'][0]['versions'][0]
        
        required_configs = []
        if version.get('configuration'):
            for i, config in enumerate(version['configuration']):
                if config.get('required') and config.get('key') != 'ibmcloud_api_key':
                    required_configs.append({
                        'index': i,
                        'key': config.get('key'),
                        'description': config.get('description'),
                        'required': config.get('required'),
                        'default_value': config.get('default_value')
                    })
        
        return json.dumps(required_configs, indent=2)
        
    except subprocess.CalledProcessError as e:
        return json.dumps({'error': f'CLI error: {e.stderr}'})
    except (KeyError, IndexError) as e:
        return json.dumps({'error': f'Data structure error: {e}'})

@mcp.tool()
def get_config_details(index: int) -> str:
    """Get full details of a configuration parameter by its index"""
    version_locator = "1082e7d2-5e2f-0a11-a3bc-f88a8e1931fc.c15a99be-f334-4dfe-b1d2-b650ae01c9ca-global"
    
    try:
        result = subprocess.run([
            'ibmcloud', 'catalog', 'offering', 'version', 'get',
            '--vl', version_locator,
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        data = json.loads(result.stdout)
        version = data['kinds'][0]['versions'][0]
        
        if not version.get('configuration') or index >= len(version['configuration']):
            return json.dumps({'error': f'Configuration index {index} not found'})
        
        config = version['configuration'][index]
        return json.dumps(config, indent=2)
        
    except subprocess.CalledProcessError as e:
        return json.dumps({'error': f'CLI error: {e.stderr}'})
    except (KeyError, IndexError) as e:
        return json.dumps({'error': f'Data structure error: {e}'})

@mcp.tool()
def list_account_resources() -> str:
    """List resources in IBM Cloud account with name, type, and region"""
    try:
        result = subprocess.run([
            'ibmcloud', 'resources',
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        data = json.loads(result.stdout)
        
        resources = []
        for resource in data.get('items', []):
            resources.append({
                'name': resource.get('name'),
                'type': resource.get('type'),
                'family': resource.get('family'),
                'region': resource.get('region')
            })
        
        return json.dumps(resources, indent=2)
        
    except subprocess.CalledProcessError as e:
        return json.dumps({'error': f'CLI error: {e.stderr}'})
    except json.JSONDecodeError as e:
        return json.dumps({'error': f'JSON decode error: {e}'})

@mcp.tool()
def list_projects() -> str:
    """List IBM Cloud projects with id, location, name, and description"""
    try:
        result = subprocess.run([
            'ibmcloud', 'project', 'list',
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        data = json.loads(result.stdout)
        
        projects = []
        for project in data.get('projects', []):
            projects.append({
                'id': project.get('id'),
                'location': project.get('location'),
                'name': project.get('definition', {}).get('name'),
                'description': project.get('definition', {}).get('description')
            })
        
        return json.dumps(projects, indent=2)
        
    except subprocess.CalledProcessError as e:
        return json.dumps({'error': f'CLI error: {e.stderr}'})
    except json.JSONDecodeError as e:
        return json.dumps({'error': f'JSON decode error: {e}'})

@mcp.tool()
def create_project(name: str) -> str:
    """Create a new IBM Cloud project with the given name"""
    try:
        definition = json.dumps({
            "name": name,
            "destroy_on_delete": True,
            "description": "",
            "auto_deploy": False,
            "monitoring_enabled": False
        })
        
        result = subprocess.run([
            'ibmcloud', 'project', 'create',
            '--definition', definition,
            '--location', 'us-south',
            '--resource-group', 'Default'
        ], capture_output=True, text=True, check=True)
        
        return result.stdout
        
    except subprocess.CalledProcessError as e:
        return json.dumps({'error': f'CLI error: {e.stderr}'})

@mcp.tool()
def create_project_config(project_id: str, name: str, inputs: Dict[str, Any], secrets_manager_ref: str) -> str:
    """Create a new project configuration for SLZ Landing Zone deployment with API key from Secrets Manager"""
    try:
        version_locator = "1082e7d2-5e2f-0a11-a3bc-f88a8e1931fc.c15a99be-f334-4dfe-b1d2-b650ae01c9ca-global"
        
        # Create authorization object with Secrets Manager reference
        authorizations = {
            "api_key": secrets_manager_ref,
            "method": "api_key"
        }
        
        cmd = [
            'ibmcloud', 'project', 'config-create',
            '--project-id', project_id,
            '--definition-name', name,
            '--definition-locator-id', version_locator,
            '--definition-authorizations', json.dumps(authorizations)
        ]
        
        if inputs:
            cmd.extend(['--definition-inputs', json.dumps(inputs)])
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        return result.stdout
        
    except subprocess.CalledProcessError as e:
        return json.dumps({'error': f'CLI error: {e.stderr}'})

@mcp.tool()
def list_secrets_manager_instances() -> str:
    """List all Secrets Manager service instances with name and GUID"""
    try:
        result = subprocess.run([
            'ibmcloud', 'resource', 'service-instances',
            '--service-name', 'secrets-manager',
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        data = json.loads(result.stdout)
        
        instances = []
        for instance in data:
            instances.append({
                'name': instance.get('name'),
                'guid': instance.get('guid')
            })
        
        return json.dumps(instances, indent=2)
        
    except subprocess.CalledProcessError as e:
        return json.dumps({'error': f'CLI error: {e.stderr}'})
    except json.JSONDecodeError as e:
        return json.dumps({'error': f'JSON decode error: {e}'})

@mcp.tool()
def build_secrets_manager_ref(instance_name: str, region: str, secret_name: str, secret_group_id: str, resource_group: str = "Default") -> str:
    """Build a Secrets Manager reference string for use in project configurations"""
    try:
        ref = f"ref://secrets-manager.{region}.{resource_group}.{instance_name}/{secret_group_id}/{secret_name}"
        return json.dumps({"secrets_manager_ref": ref})
        
    except Exception as e:
        return json.dumps({'error': f'Error building reference: {e}'})

@mcp.tool()
def list_secrets(instance_id: str) -> str:
    """List all secrets in a Secrets Manager instance with name, description, and ID"""
    try:
        result = subprocess.run([
            'ibmcloud', 'secrets-manager', 'secrets',
            '--instance-id', instance_id,
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        data = json.loads(result.stdout)
        
        secrets = []
        for secret in data.get('secrets', []):
            secrets.append({
                'name': secret.get('name'),
                'description': secret.get('description'),
                'id': secret.get('id'),
                'secret_group_id': secret.get('secret_group_id')
            })
        
        return json.dumps(secrets, indent=2)
        
    except subprocess.CalledProcessError as e:
        return json.dumps({'error': f'CLI error: {e.stderr}'})
    except json.JSONDecodeError as e:
        return json.dumps({'error': f'JSON decode error: {e}'})

if __name__ == "__main__":
    mcp.run()