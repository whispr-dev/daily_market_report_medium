"""
Script to fix the trading_signals format in the market module.
"""
import os
import traceback
from datetime import datetime

def fix_find_trading_opportunities():
    """Fix the find_trading_opportunities function to return a dictionary."""
    file_path = "mod/analysis/market.py"
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return False
    
    try:
        # Read the file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find the function
        if "def find_trading_opportunities" in content:
            # Find the start and end of the function
            start = content.find("def find_trading_opportunities")
            # Find the next def or end of file
            next_def = content.find("def ", start + 1)
            if next_def == -1:
                end = len(content)
            else:
                end = next_def
            
            # Extract the function
            function = content[start:end]
            
            # Check if the function returns a DataFrame
            if "return df_opportunities" in function:
                # Modify the return statement to convert to dict
                new_function = function.replace(
                    "return df_opportunities", 
                    """    # Convert DataFrame to dictionary for template compatibility
    if not df_opportunities.empty:
        buy_signals = df_opportunities.to_dict('records')
        return {
            'buy_signals': buy_signals,
            'sell_signals': [],  # Add sell signals if you have them
            'errors': []
        }
    else:
        return {
            'buy_signals': [],
            'sell_signals': [],
            'errors': []
        }"""
                )
                
                # Replace the function in the file
                new_content = content.replace(function, new_function)
                
                # Write the file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                
                print(f"Fixed find_trading_opportunities function in {file_path}")
                return True
            else:
                print(f"Function doesn't return df_opportunities as expected")
                return False
        else:
            print(f"Function find_trading_opportunities not found in {file_path}")
            return False
    except Exception as e:
        print(f"Error fixing find_trading_opportunities: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function to run all fixes."""
    print("Starting market module fixes...")
    fix_find_trading_opportunities()
    print("Market module fixes completed.")

if __name__ == "__main__":
    main()