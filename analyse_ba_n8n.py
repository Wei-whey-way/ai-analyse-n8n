from dotenv import load_dotenv
import os
import re
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from pypdf import PdfReader
from collections import Counter
from pathlib import Path
import pandas as pd
import numpy as np
import json, datetime

load_dotenv()

# Check if API key is available
if not os.getenv("GOOGLE_API_KEY"):
    print("⚠️  Warning: GOOGLE_API_KEY not found in environment variables")
    print("Please set your Google API key in a .env file or environment variable")

# --- Define State ---
class StatementState(TypedDict):
    file_path: str
    text: str
    metrics: dict
    ratios: dict

# --- Step 1: Read and extract totals from xlsx ---
def read_statement(state: StatementState) -> StatementState:
    # Currently accepting csv, xlsx and xls files
    try:
        #Extract data type
        #data_type = Path(state["file_path"]).suffix
        df = pd.read_excel(state["file_path"])
        df = df.replace({np.nan: None}) #Sanitize df

        #Insert warning if no extraction
        print(f"✅ Successfully extracted dataframe from Excel")

        # Select rows that contain Sales
        filtered_rows = df[df['Item Name'].str.contains(r'sales', case=False, na=False)]
        
        state["metrics"] = filtered_rows.to_dict()
        # print('test s tate after converting from df', state["metrics"])

        # with open("metrics_output.json", "w", encoding="utf-8") as f: json.dump(state["metrics"], f)
        return state
        
    except Exception as e:
        print(f"❌ Error reading files: {e}")
        state["text"] = ""
        state["metrics"] = {}
        return state

# --- Step 2: Calculate Financial Ratios ---
def calculate_ratios(state: StatementState) -> StatementState:
    m = state["metrics"]
    ratios = {}
    
    print(f"\n📊 Calculating ratios from {len(m)} metrics...")
    # print('Debugging calculate_ratios\n', m)

    # Collect all total sale value (List)
    if "Total Sale Value" in m:
        try:
            ratios["Total Sale"] = sum(m["Total Sale Value"].values())
            # print(ratios["Total Sale"])
            print(f"✅ Extracted Sales Data: {ratios['Total Sale']}")
        except:
            print("⚠️  Cannot extract Total Sale data")

    # Collect all total units sold? Skip for now

    # Sales + units sold per month(? <- To show growth in analyze_statement) Skip for now

    # Collect channel + revenue
    if "Channel" in m and "Total Sale Value" in m:
        try:
            #This portion unusable because type changed to dictionary instead of pandas df
            # channel_df = (
            #     m.groupby("Channel")["Total Sale Value"]   #  Key = Channel
            #     .sum()                                     #  Value = Total Sale Value 
            #     .reset_index()
            # )
            
            channels = m["Channel"]
            values = m["Total Sale Value"]

            channel_data = {}

            for i in channels.keys():
                ch = channels[i]
                val = values[i]

                if ch not in channel_data:
                    channel_data[ch] = []

                channel_data[ch].append(val)

            ratios["Channel Data"] = channel_data

            # ratios["Channel Data"] = dict(zip(m["Channel"].values(), m["Total Sale Value"].values()))
            print(f"✅ Calculated Channel Data: {ratios['Channel Data']}")
        except:
            print("⚠️  Cannot generate Channel data")
    
    # Collect salesperson + revenue  
    if "Salesperson" in m and "Total Sale Value" in m:
        try:
            sales_map = {}
            salesperson_list = list(m["Salesperson"].values())
            sales_list = list(m["Total Sale Value"].values())

            for person, value in zip(salesperson_list, sales_list):
                sales_map.setdefault(person, []).append(value)

            ratios["Salesperson Data"] = sales_map
            # dict(zip(m["Salesperson"].values(), m["Total Sale Value"].values()))
            print(f"✅ Calculated Salesperson Data: {ratios['Salesperson Data']}")
        except:
            print("⚠️  Cannot generate Salesperson data")      
    
    # Collect customers (List)
    if "Customer ID" in m:
        try:
            id_list = list(m["Customer ID"].values())

            ratios["Customer ID Counter"] = Counter(id_list)
            print(f"✅ Extracted Customer Data: {ratios['Customer ID Counter']}")
        except:
            print("⚠️  Cannot extract Customer ID data")

    state["ratios"] = ratios
    print(f"📈 Calculated {len(ratios)} financial ratios")
    return state

# --- Build LangGraph ---
memory = MemorySaver()
builder = StateGraph(StatementState)
builder.add_node("read", read_statement)
builder.add_node("ratios", calculate_ratios)

builder.add_edge(START, "read")
builder.add_edge("read", "ratios")
builder.add_edge("ratios", END)
graph = builder.compile(checkpointer=memory)

# --- Main Execution ---
if __name__ == "__main__":
    print("🚀 Starting Financial Statement Analysis...")
    print("=" * 50)
    
    # You can change this file path to analyze different PDFs
    # pdf_file = "data_pdf.pdf"
    # pdf_file = "SME_Business_Advisory_Template.pdf"
    xlsx_file = "data.xlsx"
    # xlsx_file = "data.xls"
    # csv_file = "data_csv.csv"
    # xlsx_file = pdf_file
    
    if not os.path.exists(xlsx_file):
        print(f"❌ PDF file not found: {xlsx_file}")
        print("Please ensure the Excel file exists in the current directory")
        exit(1)
    
    print(f"📄 Analyzing xlsx: {xlsx_file}")
    
    try:
        config = {"configurable": {"thread_id": "analysis_thread"}}
        state = graph.invoke({"file_path": xlsx_file}, config=config)
        
        print("\n" + "=" * 50)
        print("📊 ANALYSIS RESULTS")
        print("=" * 50)

        if state["metrics"]:
            print("\n💰 Extracted Financial Metrics:")
            print(state["metrics"])
        else:
            print("\n⚠️  No financial metrics were extracted")
        
        # print('Test ratios')
        if state["ratios"]:
            print("\n📈 Calculated Financial Ratios:")
            for key, value in state["ratios"].items():
                print(f"   {key}: {value}")
        else:
            print("\n⚠️  No financial ratios were calculated")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("Please check your Excel file and ensure it's a valid financial statement")
