from dotenv import load_dotenv
import os
import re
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from pypdf import PdfReader

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

# --- Step 1: Read and extract totals from PDF ---
def read_statement(state: StatementState) -> StatementState:
    try:
        reader = PdfReader(state["file_path"])
        text = ""
        for page in reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                print(f"⚠️  Warning: Could not extract text from page: {e}")
                continue
        
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")
            
        state["text"] = text
        print(f"✅ Successfully extracted {len(text)} characters from PDF")

        # Extract key totals from your PDF
        metrics = {}
        patterns = {
            "Total Revenue": r"Total Revenue\s+([\d,]+\.\d+)",
            "Total Cost of Sales": r"Total Cost of sales\s+\(([\d,]+\.\d+)\)",
            "Profit Before Tax": r"Profit Before Tax\s+([\d,]+\.\d+)",
            "Total Expenses": r"Total Expenses\s+\(([\d,]+\.\d+)\)",
            "Net Profit": r"Net Profit/\(Loss\)\s+([\d,]+\.\d+)",
            "Income Tax Expenses": r"Income Tax Expenses\s+([\d,]+\.\d+)",
            "Profit For the Year": r"Profit For the Year\s+([\d,]+\.\d+)"
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1).replace(",", ""))
                    metrics[key] = value
                    print(f"✅ Found {key}: {value}")
                except ValueError:
                    print(f"⚠️  Could not parse value for {key}: {match.group(1)}")
            else:
                print(f"⚠️  Could not find {key}")

        state["metrics"] = metrics
        return state
        
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        state["text"] = ""
        state["metrics"] = {}
        return state

# --- Step 2: Calculate Financial Ratios ---
def calculate_ratios(state: StatementState) -> StatementState:
    m = state["metrics"]
    ratios = {}
    
    print(f"\n📊 Calculating ratios from {len(m)} metrics...")

    if "Total Revenue" in m and "Total Cost of Sales" in m:
        try:
            gross_margin = ((m['Total Revenue'] - m['Total Cost of Sales']) / m['Total Revenue']) * 100
            ratios["Gross Margin"] = f"{round(gross_margin, 2)}%"
            print(f"✅ Calculated Gross Margin: {ratios['Gross Margin']}")
        except ZeroDivisionError:
            print("⚠️  Cannot calculate Gross Margin: Total Revenue is zero")

    if "Net Profit" in m and "Total Revenue" in m:
        try:
            net_margin = (m['Net Profit'] / m['Total Revenue']) * 100
            ratios["Net Profit Margin"] = f"{round(net_margin, 2)}%"
            print(f"✅ Calculated Net Profit Margin: {ratios['Net Profit Margin']}")
        except ZeroDivisionError:
            print("⚠️  Cannot calculate Net Profit Margin: Total Revenue is zero")

    if "Profit Before Tax" in m and "Total Revenue" in m:
        try:
            pbt_margin = (m['Profit Before Tax'] / m['Total Revenue']) * 100
            ratios["PBT Margin"] = f"{round(pbt_margin, 2)}%"
            print(f"✅ Calculated PBT Margin: {ratios['PBT Margin']}")
        except ZeroDivisionError:
            print("⚠️  Cannot calculate PBT Margin: Total Revenue is zero")

    if "Total Expenses" in m and "Total Revenue" in m:
        try:
            expense_ratio = (m['Total Expenses'] / m['Total Revenue']) * 100
            ratios["Expense Ratio"] = f"{round(expense_ratio, 2)}%"
            print(f"✅ Calculated Expense Ratio: {ratios['Expense Ratio']}")
        except ZeroDivisionError:
            print("⚠️  Cannot calculate Expense Ratio: Total Revenue is zero")

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
    pdf_file = "demo6_fs.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        print("Please ensure the PDF file exists in the current directory")
        exit(1)
    
    print(f"📄 Analyzing PDF: {pdf_file}")
    
    try:
        config = {"configurable": {"thread_id": "analysis_thread"}}
        state = graph.invoke({"file_path": pdf_file}, config=config)
        
        print("\n" + "=" * 50)
        print("📊 ANALYSIS RESULTS")
        print("=" * 50)
        
        if state["metrics"]:
            print("\n💰 Extracted Financial Metrics:")
            for key, value in state["metrics"].items():
                print(f"   {key}: {value:,.2f}")
        else:
            print("\n⚠️  No financial metrics were extracted")
        
        if state["ratios"]:
            print("\n📈 Calculated Financial Ratios:")
            for key, value in state["ratios"].items():
                print(f"   {key}: {value}")
        else:
            print("\n⚠️  No financial ratios were calculated")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("Please check your PDF file and ensure it's a valid financial statement")
