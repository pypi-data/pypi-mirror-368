"""
Simple S3-based module deployment for HLA-Compass SDK
No authentication, just direct S3 upload for dev environment
"""

import os
import json
import boto3
from pathlib import Path
from typing import Dict, Any
import uuid
from datetime import datetime

class SimpleDeployer:
    """
    Minimal module deployment - uploads directly to S3
    No auth, no database, just S3 + Lambda
    """
    
    def __init__(self, env: str = 'dev'):
        self.env = env
        self.s3_client = boto3.client('s3')
        self.lambda_client = boto3.client('lambda')
        
        # Use existing buckets from your infrastructure
        self.modules_bucket = f'hla-compass-modules-{env}'
        self.results_bucket = f'hla-compass-results-{env}'
        
    def deploy(self, package_path: str, module_name: str) -> Dict[str, Any]:
        """
        Deploy module package to S3 and create/update Lambda function
        
        Simple approach:
        1. Upload zip to S3
        2. Create or update Lambda function
        3. Return deployment info
        """
        
        # Generate version ID
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        module_id = f"{module_name}-{version}"
        
        # Upload to S3
        s3_key = f"modules/{module_name}/{version}/package.zip"
        
        print(f"📦 Uploading {package_path} to s3://{self.modules_bucket}/{s3_key}")
        
        with open(package_path, 'rb') as f:
            self.s3_client.put_object(
                Bucket=self.modules_bucket,
                Key=s3_key,
                Body=f.read(),
                Metadata={
                    'module-name': module_name,
                    'version': version,
                    'deployed-at': datetime.utcnow().isoformat()
                }
            )
        
        # Create or update Lambda function
        function_name = f"hla-module-{self.env}-{module_name}"
        
        try:
            # Try to update existing function
            response = self.lambda_client.update_function_code(
                FunctionName=function_name,
                S3Bucket=self.modules_bucket,
                S3Key=s3_key
            )
            print(f"✅ Updated Lambda function: {function_name}")
            
        except self.lambda_client.exceptions.ResourceNotFoundException:
            # Create new function
            response = self.lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.11',
                Role=self._get_lambda_role(),
                Handler='backend.main.execute',
                Code={
                    'S3Bucket': self.modules_bucket,
                    'S3Key': s3_key
                },
                Timeout=300,
                MemorySize=1024,
                Environment={
                    'Variables': {
                        'MODULE_NAME': module_name,
                        'MODULE_VERSION': version,
                        'RESULTS_BUCKET': self.results_bucket
                    }
                }
            )
            print(f"✅ Created Lambda function: {function_name}")
        
        # Save deployment info to S3 (instead of database)
        deployment_info = {
            'module_id': module_id,
            'module_name': module_name,
            'version': version,
            's3_key': s3_key,
            'lambda_function': function_name,
            'deployed_at': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        
        # Store deployment metadata
        metadata_key = f"deployments/{module_name}/latest.json"
        self.s3_client.put_object(
            Bucket=self.modules_bucket,
            Key=metadata_key,
            Body=json.dumps(deployment_info, indent=2)
        )
        
        print(f"""
✅ Module deployed successfully!

Module: {module_name}
Version: {version}
Lambda: {function_name}
S3: s3://{self.modules_bucket}/{s3_key}

Test with:
  hla-compass execute {module_name} --input examples/input.json
        """)
        
        return deployment_info
    
    def execute(self, module_name: str, input_data: Dict[str, Any]) -> str:
        """
        Execute module via Lambda invocation
        Returns job_id for tracking
        """
        
        job_id = str(uuid.uuid4())
        function_name = f"hla-module-{self.env}-{module_name}"
        
        # Prepare payload
        payload = {
            'job_id': job_id,
            'input_data': input_data,
            'context': {
                'job_id': job_id,
                'module_name': module_name,
                'user_id': 'dev-user',
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        print(f"🚀 Executing {module_name} (job_id: {job_id})")
        
        # Invoke Lambda
        response = self.lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',  # Synchronous for now
            Payload=json.dumps(payload)
        )
        
        # Parse response
        result = json.loads(response['Payload'].read())
        
        # Save results to S3
        results_key = f"results/{job_id}/output.json"
        self.s3_client.put_object(
            Bucket=self.results_bucket,
            Key=results_key,
            Body=json.dumps(result, indent=2)
        )
        
        print(f"""
✅ Execution complete!

Job ID: {job_id}
Status: {result.get('status', 'unknown')}
Results: s3://{self.results_bucket}/{results_key}

View results:
  hla-compass results {job_id}
        """)
        
        return job_id
    
    def get_results(self, job_id: str) -> Dict[str, Any]:
        """
        Retrieve results from S3
        """
        results_key = f"results/{job_id}/output.json"
        
        response = self.s3_client.get_object(
            Bucket=self.results_bucket,
            Key=results_key
        )
        
        return json.loads(response['Body'].read())
    
    def list_modules(self) -> list:
        """
        List deployed modules from S3
        """
        response = self.s3_client.list_objects_v2(
            Bucket=self.modules_bucket,
            Prefix='deployments/',
            Delimiter='/'
        )
        
        modules = []
        for prefix in response.get('CommonPrefixes', []):
            module_name = prefix['Prefix'].split('/')[1]
            
            # Get latest deployment info
            try:
                metadata_response = self.s3_client.get_object(
                    Bucket=self.modules_bucket,
                    Key=f"deployments/{module_name}/latest.json"
                )
                module_info = json.loads(metadata_response['Body'].read())
                modules.append(module_info)
            except:
                pass
        
        return modules
    
    def _get_lambda_role(self) -> str:
        """
        Get or create Lambda execution role
        Using existing role from your infrastructure
        """
        # This should exist from your Terraform/Serverless setup
        return f"arn:aws:iam::803691999371:role/hla-compass-{self.env}-lambda-role"