#!/usr/bin/env python3
"""
Minimal script to create start_agent.py during build
"""

start_agent_content = '''#!/usr/bin/env python3
import os
import sys
import logging
import asyncio
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_paths():
    project_root = Path(__file__).parent.absolute()
    src_dir = project_root / "src"
    
    for path in [str(project_root), str(src_dir)]:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    os.environ['PYTHONPATH'] = ':'.join([str(project_root), str(src_dir)])

async def main():
    logger.info("🚀 Starting ArXiv Research Agent...")
    
    setup_paths()
    
    try:
        from research_agent import main as agent_main
        await agent_main()
    except Exception as e:
        logger.error(f"❌ Agent failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
'''

with open('start_agent.py', 'w') as f:
    f.write(start_agent_content)

os.chmod('start_agent.py', 0o755)
print("✅ Created start_agent.py")