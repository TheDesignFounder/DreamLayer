#!/usr/bin/env python3
"""
Simple startup script for run_registry.py
Fixes the ERR_CONNECTION_REFUSED issue
"""

import os
import sys

def start_run_registry():
    print('🚀 Starting Run Registry with Database Integration')
    print('=' * 50)
    
    try:
        # Import and start run_registry
        from run_registry import app
        
        print('✅ run_registry.py loaded successfully')
        print('📊 Database integration: ENABLED')
        print('🌐 Starting server on http://localhost:5005')
        print('📡 API endpoints available:')
        print('   - /api/runs (database-first)')
        print('   - /api/runs/enhanced/v2 (with ClipScore)')
        print('   - /api/database/stats')
        print('')
        print('🔗 Frontend can now connect to: http://localhost:5005/api/runs/enhanced/v2')
        print('=' * 50)
        
        # Start the Flask app
        app.run(host='0.0.0.0', port=5005, debug=False)
        
    except Exception as e:
        print(f'❌ Error starting run_registry: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    start_run_registry()
