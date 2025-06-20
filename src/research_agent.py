#!/usr/bin/env python3
"""
ArXiv Research Agent - Main Application
======================================

24/7 AI research agent that monitors arXiv, analyzes papers using Claude Code SDK,
and generates intelligent research digests.
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime, timedelta, time as dt_time
from pathlib import Path
from typing import Dict, List, Optional, Any
import schedule
import time
import threading

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from arxiv_fetcher import ArxivFetcher, ArxivPaper
from claude_analyzer import ClaudeAnalyzer, PaperAnalysis
from digest_generator import DigestGenerator
from config_manager import ConfigManager


class ResearchAgent:
    """Main research agent orchestrating all components"""
    
    def __init__(self, config_path: str = None):
        # Initialize configuration
        self.config = ConfigManager(config_path)
        
        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.arxiv_fetcher = None
        self.claude_analyzer = None
        self.digest_generator = None
        
        # Agent state
        self.running = False
        self.last_run = None
        self.run_count = 0
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("🤖 ArXiv Research Agent initialized")
    
    def setup_logging(self):
        """Setup logging based on configuration"""
        log_config = self.config.get_logging_config()
        
        # Create log directory
        log_dir = Path(log_config.main_log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_config.level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.main_log_file),
                logging.StreamHandler(sys.stdout) if log_config.console_enabled else logging.NullHandler()
            ]
        )
        
        # Setup log rotation
        from logging.handlers import RotatingFileHandler
        
        # Replace file handler with rotating handler
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                root_logger.removeHandler(handler)
        
        rotating_handler = RotatingFileHandler(
            log_config.main_log_file,
            maxBytes=log_config.max_size_mb * 1024 * 1024,
            backupCount=log_config.backup_count
        )
        rotating_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        root_logger.addHandler(rotating_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def initialize_components(self):
        """Initialize all agent components"""
        try:
            # Initialize Claude analyzer
            claude_config = self.config.get_claude_config()
            working_dir = claude_config.working_directory or str(Path.cwd())
            self.claude_analyzer = ClaudeAnalyzer(working_dir)
            
            # Initialize digest generator
            output_config = self.config.get_output_config()
            self.digest_generator = DigestGenerator(output_config.directory)
            
            self.logger.info("✅ All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize components: {e}")
            raise
    
    async def fetch_and_analyze_papers(self) -> tuple[List[ArxivPaper], List[PaperAnalysis]]:
        """Fetch papers and perform Claude analysis"""
        research_config = self.config.get_research_config()
        
        # Fetch papers
        self.logger.info("📚 Fetching papers from arXiv...")
        
        async with ArxivFetcher() as fetcher:
            papers = await fetcher.fetch_papers(
                categories=research_config.arxiv_categories,
                max_results=research_config.max_papers_per_day,
                days_back=research_config.days_back,
                keywords=research_config.interests
            )
            
            # Filter papers
            filtered_papers = fetcher.filter_papers(
                papers,
                exclude_keywords=research_config.exclude_keywords,
                min_relevance_score=research_config.min_relevance_score
            )
        
        self.logger.info(f"📊 Found {len(filtered_papers)} relevant papers out of {len(papers)} total")
        
        if not filtered_papers:
            self.logger.warning("No papers found matching criteria")
            return [], []
        
        # Analyze papers with Claude
        self.logger.info("🔍 Starting Claude analysis...")
        
        analyses = await self.claude_analyzer.analyze_paper_batch(
            filtered_papers[:10],  # Limit to top 10 for cost control
            research_interests=research_config.interests
        )
        
        # Filter by significance score
        significant_analyses = [
            analysis for analysis in analyses
            if analysis.significance_score >= research_config.min_significance_score
        ]
        
        self.logger.info(f"🎯 {len(significant_analyses)} papers passed significance threshold")
        
        return filtered_papers, significant_analyses
    
    async def generate_and_distribute_digest(self, papers: List[ArxivPaper], 
                                           analyses: List[PaperAnalysis]) -> Dict[str, Any]:
        """Generate digest in multiple formats and distribute"""
        if not papers or not analyses:
            self.logger.warning("No papers or analyses to generate digest")
            return {"status": "skipped", "reason": "no_content"}
        
        output_config = self.config.get_output_config()
        digest_files = {}
        
        # Generate digest formats
        if output_config.html:
            html_file = self.digest_generator.generate_html_digest(papers, analyses)
            digest_files['html'] = html_file
            self.logger.info(f"📄 Generated HTML digest: {html_file}")
        
        if output_config.markdown:
            md_file = self.digest_generator.generate_markdown_digest(papers, analyses)
            digest_files['markdown'] = md_file
            self.logger.info(f"📝 Generated Markdown digest: {md_file}")
        
        if output_config.json:
            json_file = self.digest_generator.save_json_digest(papers, analyses)
            digest_files['json'] = json_file
            self.logger.info(f"💾 Saved JSON data: {json_file}")
        
        # Send notifications
        notifications_sent = {}
        
        # Email notification
        email_config = self.config.get_email_config()
        if email_config.enabled and email_config.recipients:
            email_content = self.digest_generator.generate_email_content(papers, analyses)
            subject = email_config.subject_template.format(date=datetime.now().strftime("%Y-%m-%d"))
            
            for recipient in email_config.recipients:
                success = await self.digest_generator.send_email(
                    subject=subject,
                    content=email_content,
                    to_email=recipient,
                    smtp_config={
                        'smtp_server': email_config.smtp_server,
                        'smtp_port': email_config.smtp_port,
                        'username': email_config.username,
                        'password': email_config.password,
                        'from_email': email_config.from_email
                    }
                )
                notifications_sent[f'email_{recipient}'] = success
        
        # Discord notification
        discord_config = self.config.get_discord_config()
        if discord_config.enabled and discord_config.webhook_url:
            discord_content = self.digest_generator.generate_email_content(papers, analyses)[:1500]
            success = await self.digest_generator.send_discord_webhook(
                content=discord_content,
                webhook_url=discord_config.webhook_url
            )
            notifications_sent['discord'] = success
        
        return {
            "status": "success",
            "papers_count": len(papers),
            "analyses_count": len(analyses),
            "digest_files": digest_files,
            "notifications": notifications_sent,
            "timestamp": datetime.now().isoformat()
        }
    
    async def run_daily_digest(self) -> Dict[str, Any]:
        """Run the daily digest process"""
        start_time = time.time()
        self.logger.info("🚀 Starting daily digest generation...")
        
        try:
            # Fetch and analyze papers
            papers, analyses = await self.fetch_and_analyze_papers()
            
            if not analyses:
                return {
                    "status": "no_content",
                    "message": "No significant papers found today",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Generate and distribute digest
            result = await self.generate_and_distribute_digest(papers, analyses)
            
            # Update run statistics
            self.last_run = datetime.now()
            self.run_count += 1
            
            execution_time = time.time() - start_time
            self.logger.info(f"✅ Daily digest completed in {execution_time:.2f}s")
            
            result['execution_time'] = execution_time
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Daily digest failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_weekly_summary(self) -> Dict[str, Any]:
        """Run weekly trend analysis and summary"""
        self.logger.info("📈 Generating weekly research summary...")
        
        try:
            # This would analyze trends over the past week
            # For now, we'll run a regular digest with extended lookback
            research_config = self.config.get_research_config()
            
            # Temporarily extend lookback to 7 days
            original_days = research_config.days_back
            research_config.days_back = 7
            
            papers, analyses = await self.fetch_and_analyze_papers()
            
            # Restore original setting
            research_config.days_back = original_days
            
            if analyses:
                # Generate trend analysis
                trends = await self.claude_analyzer.identify_trends(analyses)
                
                # Generate special weekly digest
                result = await self.generate_and_distribute_digest(papers, analyses)
                result['trend_analysis'] = trends
                
                self.logger.info("✅ Weekly summary completed")
                return result
            else:
                return {
                    "status": "no_content",
                    "message": "No papers found for weekly summary"
                }
                
        except Exception as e:
            self.logger.error(f"❌ Weekly summary failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def schedule_tasks(self):
        """Schedule recurring tasks"""
        schedule_config = self.config.get_schedule_config()
        
        # Schedule daily digest
        if schedule_config.daily_digest_enabled:
            schedule.every().day.at(schedule_config.daily_digest_time).do(
                lambda: asyncio.create_task(self.run_daily_digest())
            )
            self.logger.info(f"📅 Scheduled daily digest at {schedule_config.daily_digest_time}")
        
        # Schedule weekly summary
        if schedule_config.weekly_summary_enabled:
            getattr(schedule.every(), schedule_config.weekly_summary_day.lower()).at(
                schedule_config.weekly_summary_time
            ).do(
                lambda: asyncio.create_task(self.run_weekly_summary())
            )
            self.logger.info(f"📅 Scheduled weekly summary on {schedule_config.weekly_summary_day} at {schedule_config.weekly_summary_time}")
    
    async def start_agent(self):
        """Start the research agent"""
        self.running = True
        
        await self.initialize_components()
        
        # Schedule tasks
        self.schedule_tasks()
        
        self.logger.info("🤖 Research Agent started - monitoring for scheduled tasks...")
        
        # Run scheduler in background thread
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # Keep main thread alive
        try:
            while self.running:
                await asyncio.sleep(10)
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        finally:
            self.running = False
            self.logger.info("🛑 Research Agent stopped")
    
    async def run_once(self) -> Dict[str, Any]:
        """Run digest generation once (for testing/manual execution)"""
        await self.initialize_components()
        return await self.run_daily_digest()


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ArXiv Research Agent")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--test", action="store_true", help="Test configuration and exit")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = ResearchAgent(args.config)
    
    if args.test:
        # Test configuration
        print("🧪 Testing configuration...")
        research_config = agent.config.get_research_config()
        print(f"✅ Research interests: {len(research_config.interests)}")
        print(f"✅ arXiv categories: {research_config.arxiv_categories}")
        print(f"✅ Output directory: {agent.config.get_output_config().directory}")
        
        # Test API key
        import os
        if os.getenv('ANTHROPIC_API_KEY'):
            print("✅ ANTHROPIC_API_KEY is set")
        else:
            print("⚠️  ANTHROPIC_API_KEY not set - add to environment")
        
        print("Configuration test completed!")
        return
    
    if args.once:
        # Run once and exit
        print("🚀 Running digest generation once...")
        result = await agent.run_once()
        print(f"Result: {result}")
    else:
        # Start continuous agent
        await agent.start_agent()


if __name__ == "__main__":
    asyncio.run(main())