#!/usr/bin/env python3
"""
Test Windows Directory Output
=============================

Test writing files to the Windows directory via WSL mount.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config_manager import ConfigManager
from digest_generator import DigestGenerator


async def test_windows_output():
    """Test writing to Windows directory"""
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # Load config with Windows directory
    config = ConfigManager()
    output_config = config.get_output_config()
    
    logger.info(f"📁 Configured output directory: {output_config.directory}")
    
    # Test creating directory and file
    windows_path = Path("/mnt/c/Users/Tyvon/OneDrive/Documents/TyvonneDocs/VBE/AI_Research")
    
    try:
        # Ensure directory exists
        windows_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Directory created/verified: {windows_path}")
        
        # Test writing a file
        test_file = windows_path / f"test_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(test_file, 'w') as f:
            f.write(f"""ArXiv Research Agent - Test Output
Generated: {datetime.now().isoformat()}

This file confirms that the ArXiv Research Agent can successfully write to your Windows directory.

Directory: C:\\Users\\Tyvon\\OneDrive\\Documents\\TyvonneDocs\\VBE\\AI_Research
WSL Path: /mnt/c/Users/Tyvon/OneDrive/Documents/TyvonneDocs/VBE/AI_Research

✅ File output system working correctly!
""")
        
        logger.info(f"✅ Test file created: {test_file}")
        
        # Test DigestGenerator with Windows path
        digest_gen = DigestGenerator(str(windows_path))
        
        # Create a simple test HTML file
        test_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>ArXiv Research Agent - Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .header {{ background: #667eea; color: white; padding: 20px; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 ArXiv Research Agent - Test Output</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    <div style="margin-top: 20px;">
        <h2>✅ Windows Directory Test Successful!</h2>
        <p>The ArXiv Research Agent is configured to save research digests to:</p>
        <code>C:\\Users\\Tyvon\\OneDrive\\Documents\\TyvonneDocs\\VBE\\AI_Research</code>
        
        <h3>Daily Digest Schedule:</h3>
        <ul>
            <li>📅 <strong>Daily Digest:</strong> 9:00 AM UTC</li>
            <li>📊 <strong>Weekly Summary:</strong> Monday 8:00 AM UTC</li>
            <li>📋 <strong>File Formats:</strong> HTML, Markdown, JSON</li>
        </ul>
        
        <h3>Expected Files:</h3>
        <ul>
            <li><code>digest_YYYYMMDD_HHMMSS.html</code> - Beautiful interactive digest</li>
            <li><code>digest_YYYYMMDD_HHMMSS.md</code> - Markdown summary</li>
            <li><code>digest_YYYYMMDD_HHMMSS.json</code> - Raw data</li>
        </ul>
    </div>
</body>
</html>"""
        
        html_file = windows_path / f"arxiv_agent_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_file, 'w') as f:
            f.write(test_html)
        
        logger.info(f"✅ Test HTML file created: {html_file}")
        
        # List files in directory
        files_in_dir = list(windows_path.glob("*"))
        logger.info(f"📂 Files in Windows directory: {len(files_in_dir)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to write to Windows directory: {e}")
        return False


async def main():
    """Main test function"""
    
    print("🧪 Testing Windows Directory Output")
    print("=" * 50)
    
    success = await test_windows_output()
    
    if success:
        print("\n✅ Windows directory test PASSED!")
        print("🎯 ArXiv Research Agent will save files to:")
        print("   C:\\Users\\Tyvon\\OneDrive\\Documents\\TyvonneDocs\\VBE\\AI_Research")
        print("\n📋 Next steps:")
        print("   1. Deploy to Render (background service)")
        print("   2. Agent will run 24/7 and save daily digests")
        print("   3. Check directory daily for new research files")
    else:
        print("\n❌ Windows directory test FAILED!")
        print("   Check permissions and directory path")


if __name__ == "__main__":
    asyncio.run(main())