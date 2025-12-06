#!/usr/bin/env python3
"""
Test client for the Business and Financial Advisory Analysis API
"""

import requests
import json
import time
import os
from pathlib import Path

from test_api_combined import test_health_check, test_queue_status, test_upload_analysis, get_results, wait_for_completion, cleanup_analysis

# API configuration
API_BASE_URL = "http://localhost:8000"

# def test_upload_analysis(sales_file_path: str, finance_file_path: str):
#     """Test file upload and analysis"""
#     print(f"\n📤 Testing file upload analysis for: {sales_file_path} and {finance_file_path}")
    
#     if not os.path.exists(sales_file_path) or not os.path.exists(finance_file_path):
#         print(f"❌ File not found: {sales_file_path} or {finance_file_path}")
#         return None
    
#     try:
#         # Upload file
#         with open(sales_file_path, 'rb') as f_sales, open(finance_file_path, 'rb') as f_finance:
#             files = {
#                 'finance_file': (os.path.basename(finance_file_path), f_finance, 'application/pdf'),
#                 'sales_file': (os.path.basename(sales_file_path), f_sales, 'application/xlsx'),
#             }

#             response = requests.post(
#                 "http://localhost:5678/webhook/combined",
#                 files=files,
#                 params={'analysis_type': 'full'}
#             )

#         # print('Debug response', response)
#         # return
        
#         if response.status_code == 200:
#             data = response.json()
#             print(f"✅ Upload successful: {data}")
#             return data
#         else:
#             print(f"❌ Upload failed: {response.status_code} - {response.text}")
#             return None
            
#     except Exception as e:
#         print(f"❌ Upload error: {e}")
#         return None

# def get_results(data: dict):
#     """Get analysis results"""
#     # print(f"\n📊 Getting results for {request_id}...")
    
#     try:
#         print("✅ Results retrieved successfully!")
#         # print(f"📈 Metrics: {data['metrics']}")
#         # print(f"📊 Ratios: {data['ratios']}")
#         print(f"💰 Finance Analysis: {data['analysis_finance'][:200]}...")
#         print(f"\n💼 Sales Analysis: {data['analysis_sales'][:200]}...")
#         print(f"\n🤖 Business Advisory Analysis: {data['analysis']}...")
#         # print(f"⏱️  Processing time: {data['processing_time']:.2f} seconds")
#         return
            
#     except Exception as e:
#         print(f"❌ Results retrieval error: {e}")
#         return None

def main():
    """Main test function"""
    print("🚀 Business Advisory Analysis Combined API Test Client (API)")
    print("=" * 50)

    # Test health check
    if not test_health_check():
        print("❌ API is not running. Please start the API server first.")
        return
    
    # Test queue status
    test_queue_status()
        
    # Look for excel files in current directory
    excel_files = [f for f in Path(".").iterdir() if f.suffix in [".xlsx", ".xls"]]
    pdf_files = [f for f in Path(".").iterdir() if f.suffix == ".pdf"]

    if not excel_files and not pdf_files:
        print("\n⚠️  No excel or pdf files found in current directory")
        print("Please place an excel or pdf file in the current directory to test with")
        return

    print(f"\n📄 Found {len(excel_files)} Excel file(s) and {len(pdf_files)} PDF file(s):")
    for excel_file in excel_files:
        print(f"   - {excel_file}")
    for pdf_file in pdf_files:
        print(f"   - {pdf_file}")
    
    # Test with first Excel and Pdf files
    test_excel = str(excel_files[0])
    test_pdf = str(pdf_files[0])
    print(f"\n🎯 Testing with: {test_excel} and {test_pdf}")
    
    # Test file upload analysis
    request_id = test_upload_analysis(test_excel, test_pdf)
    
    # Get results
    if request_id:
        # Wait for completion
        if wait_for_completion(request_id):
            # Get results
            results = get_results(request_id)
            
            if results:
                print("\n🎉 Test completed successfully!")
                
                # Clean up
                cleanup_analysis(request_id)
            else:
                print("\n❌ Failed to retrieve results")
        else:
            print("\n❌ Analysis did not complete in time")
    else:
        print("\n❌ Failed to start analysis")
    
    # Test queue status again
    test_queue_status()
    # if (state):
    #     get_results(state)
    # else:
    #     print("\n❌ Failed to retrieve results")

    
if __name__ == "__main__":
    main()
