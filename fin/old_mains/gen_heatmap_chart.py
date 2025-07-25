def generate_sector_heatmap(df_universe):
    """Generate a sector heatmap showing daily percentage changes."""
    try:
        # Check if we have the necessary columns
        if 'symbol' not in df_universe.columns or 'sector' not in df_universe.columns:
            print("Warning: Missing required columns (symbol or sector) for heatmap.")
            return None
            
        # Ensure we have pct_change and that it's numeric
        if 'pct_change' not in df_universe.columns:
            print("Warning: Missing pct_change column for heatmap.")
            return None
            
        # Make a copy to avoid modifying the original
        df = df_universe.copy()
        
        # Force numeric and drop NaNs
        df['pct_change'] = pd.to_numeric(df['pct_change'], errors='coerce')
        df.dropna(subset=['pct_change', 'sector'], inplace=True)
        
        # Filter out rows with empty sectors
        df = df[df['sector'].str.strip() != ""]
        
        if len(df) < 5:  # Arbitrary threshold - need enough data to make a meaningful heatmap
            print("Warning: Not enough valid data for sector heatmap.")
            return None

        # Create pivot table
        pivoted = df.pivot_table(
            index='sector', 
            columns='symbol', 
            values='pct_change', 
            aggfunc='mean'
        )
        
        if pivoted.empty or pivoted.shape[0] < 2 or pivoted.shape[1] < 2:
            print("Warning: Sector heatmap pivot table is too small.")
            return None

        # For a cleaner visualization, calculate the average for each sector
        sector_avg = pivoted.mean(axis=1).to_frame('Sector Avg')
        
        # Create figure and plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Use a diverging colormap centered at 0
        cmap = sns.diverging_palette(10, 133, as_cmap=True)
        
        # Calculate heatmap bounds for better color contrast
        vmin = max(pivoted.min().min() * 1.5, -5)  # Limit to -5% if data is less extreme
        vmax = min(pivoted.max().max() * 1.5, 5)   # Limit to +5% if data is less extreme
        
        # Plot the heatmap
        sns.heatmap(sector_avg, annot=True, cmap=cmap, center=0, 
                    fmt=".2f", linewidths=.5, ax=ax, vmin=vmin, vmax=vmax)
        
        plt.title("Sector Performance - Daily % Change")
        plt.tight_layout()
        
        return img_to_base64(fig)
    
    except Exception as e:
        print(f"Error generating sector heatmap: {e}")
        return None