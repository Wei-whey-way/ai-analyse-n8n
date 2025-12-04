#!/usr/bin/env python3
"""
Test client for the Business Advisory Analysis API
"""

import requests
import json
import time
import os
from pathlib import Path

# API configuration
API_BASE_URL = "http://localhost:8000"

# def test_health_check():
#     """Test the health check endpoint"""
#     print("🏥 Testing health check...")
#     try:
#         response = requests.get(f"{API_BASE_URL}/health")
#         if response.status_code == 200:
#             data = response.json()
#             print(f"✅ Health check passed: {data}")
#             return True
#         else:
#             print(f"❌ Health check failed: {response.status_code}")
#             return False
#     except Exception as e:
#         print(f"❌ Health check error: {e}")
#         return False

def test_upload_analysis(xlsx_file_path: str, max_wait_time: int = 300):
    """Test file upload and analysis"""
    print(f"\n📤 Testing file upload analysis for: {xlsx_file_path}")
    
    if not os.path.exists(xlsx_file_path):
        print(f"❌ File not found: {xlsx_file_path}")
        return None
    
    try:
        """Wait for analysis to complete"""
        print(f"\n⏳ Waiting for analysis to complete...")
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            try:
                # Upload file
                with open(xlsx_file_path, 'rb') as f:
                    files = {'file': (os.path.basename(xlsx_file_path), f, 'application/xlsx')}
                    response = requests.post(
                        # 'http://localhost:5678/webhook-test/sales',
                        'http://localhost:5678/webhook/sales',
                        files=files,
                        # params={'analysis_type': 'full'}
                    )
                
                # print('Debug output', response)
                # return
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ n8n retrieval successful: {data.keys()}")
                    return data
                else:
                    print(f"❌ Upload failed: {response.status_code} - {response.text}")
                    return None
            except Exception as e:
                print(f"⚠️  Status check error: {e}")
            
            time.sleep(5)  # Wait 5 seconds before checking again
        
        print(f"⏰ Timeout waiting for analysis to complete")
        exit
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

# def wait_for_completion(request_id: str, max_wait_time: int = 300):
#     """Wait for analysis to complete"""
#     print(f"\n⏳ Waiting for analysis {request_id} to complete...")
    
#     start_time = time.time()
#     while time.time() - start_time < max_wait_time:
#         try:
#             response = requests.get(f"{API_BASE_URL}/status/spreadsheet/{request_id}")
#             if response.status_code == 200:
#                 data = response.json()
#                 status = data['status']
                
#                 if status == 'completed':
#                     print(f"✅ Analysis completed!")
#                     return True
#                 elif status == 'failed':
#                     print(f"❌ Analysis failed!")
#                     return False
#                 elif status in ['queued', 'processing']:
#                     print(f"⏳ Status: {status}...")
#                 else:
#                     print(f"❓ Unknown status: {status}")
#             else:
#                 print(f"⚠️  Status check failed: {response.status_code}")
                
#         except Exception as e:
#             print(f"⚠️  Status check error: {e}")
        
#         time.sleep(5)  # Wait 5 seconds before checking again
    
#     print(f"⏰ Timeout waiting for analysis to complete")
#     return False

def get_results(state: dict):
    """Get analysis results"""
#     print(f"\n📊 Getting results for {request_id}...")
    
    try:
        #Output results
        print("✅ Results retrieved successfully!")
        print(f"📈 Metrics: {state['Metrics']}")
        print(f"📊 Ratios: {state['Ratios']}")
        print(f"🤖 Analysis: {state['Analysis']}")
        # print(f"⏱️  Processing time: {state['processing_time']:.2f} seconds")
        return
    
    except Exception as e:
        print(f"❌ Results retrieval error: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Business Advisory Analysis API Test Client (n8n)")
    print("=" * 50)
    
    # Look for excel files in current directory
    excel_files = [f for f in Path(".").iterdir() if f.suffix in [".xlsx", ".xls"]]
    
    if not excel_files:
        print("\n⚠️  No excel files found in current directory")
        print("Please place a excel file in the current directory to test with")
        return
    
    print(f"\n📄 Found {len(excel_files)} Excel file(s):")
    for pdf_file in excel_files:
        print(f"   - {pdf_file}")
    
    # Test with first PDF file
    test_excel = str(excel_files[0])
    print(f"\n🎯 Testing with: {test_excel}")
    
    # Test file upload analysis
    state = test_upload_analysis(test_excel)
    
    # Get results
    if (state):
        get_results(state)
    else:
        print("\n❌ Failed to retrieve results")

if __name__ == "__main__":
    main()
