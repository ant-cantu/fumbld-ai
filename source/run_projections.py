#!/usr/bin/env python3
"""
Simple execution script for generating NFL projections
Run this to generate projections with default settings
"""

import sys
from pathlib import Path

def run_projections():
    """Run projections with default settings"""
    try:
        # Import and run
        from get_projections import main
        
        print("🏈 Starting NFL Projections Generation...")
        print("=" * 50)
        
        main()
        
        print("=" * 50)
        print("✅ Projections generation completed!")
        
        # Show output file location
        current_dir = Path(__file__).parent
        from get_projections import ProjectionsGenerator
        
        gen = ProjectionsGenerator()
        print(f"📁 Output file: {gen.output_filepath}")
        
        if gen.output_filepath.exists():
            import pandas as pd
            df = pd.read_csv(gen.output_filepath)
            print(f"📊 Total projections: {len(df)}")
            print(f"🏆 Top projection: {df.iloc[0]['player_name']} - {df.iloc[0]['projected_points']:.2f} pts")
        
    except Exception as e:
        print(f"❌ Error running projections: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_projections()
