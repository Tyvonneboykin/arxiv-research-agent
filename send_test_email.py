#!/usr/bin/env python3
"""
Send Test Email - ArXiv Research Agent
=====================================

Sends a test email digest to donvon@vonbase.com
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from arxiv_fetcher import ArxivFetcher, ArxivPaper
from claude_analyzer import ClaudeAnalyzer, PaperAnalysis
from digest_generator import DigestGenerator
from config_manager import ConfigManager


async def create_sample_data():
    """Create sample data for testing"""
    
    # Sample papers (these would normally come from arXiv)
    sample_papers = [
        ArxivPaper(
            id="2025.0001",
            title="Revolutionary Advances in Large Language Model Reasoning: A New Paradigm",
            authors=["Dr. Jane Smith", "Prof. John Doe", "Dr. Alice Johnson"],
            abstract="We present a novel approach to enhancing reasoning capabilities in large language models through a revolutionary architecture that combines symbolic reasoning with neural networks. Our method achieves state-of-the-art performance on complex reasoning benchmarks, improving accuracy by 40% over previous methods. This breakthrough has significant implications for AI safety, autonomous systems, and general artificial intelligence development.",
            categories=["cs.AI", "cs.LG"],
            published=datetime.now(),
            updated=datetime.now(),
            pdf_url="https://arxiv.org/pdf/2025.0001.pdf",
            arxiv_url="https://arxiv.org/abs/2025.0001",
            primary_category="cs.AI"
        ),
        ArxivPaper(
            id="2025.0002", 
            title="Efficient Multi-Agent Systems for Autonomous Coordination",
            authors=["Dr. Bob Wilson", "Dr. Carol Chen"],
            abstract="This paper introduces a novel framework for multi-agent coordination that significantly reduces computational overhead while maintaining optimal performance. Our approach uses decentralized decision-making with global optimization, achieving 60% faster convergence than existing methods. Applications include robotics, autonomous vehicles, and distributed AI systems.",
            categories=["cs.AI", "cs.RO"],
            published=datetime.now(),
            updated=datetime.now(), 
            pdf_url="https://arxiv.org/pdf/2025.0002.pdf",
            arxiv_url="https://arxiv.org/abs/2025.0002",
            primary_category="cs.AI"
        ),
        ArxivPaper(
            id="2025.0003",
            title="Breaking Through Vision-Language Understanding Barriers",
            authors=["Dr. David Lee", "Dr. Emma Rodriguez", "Prof. Michael Chang"],
            abstract="We present VisionLM-Ultra, a groundbreaking vision-language model that achieves human-level performance on complex visual reasoning tasks. Our model introduces a novel attention mechanism that bridges visual and textual representations more effectively than previous approaches. This advance opens new possibilities for autonomous systems, creative AI, and human-computer interaction.",
            categories=["cs.CV", "cs.CL"], 
            published=datetime.now(),
            updated=datetime.now(),
            pdf_url="https://arxiv.org/pdf/2025.0003.pdf",
            arxiv_url="https://arxiv.org/abs/2025.0003",
            primary_category="cs.CV"
        )
    ]
    
    # Sample analyses (these would normally come from Claude)
    sample_analyses = [
        PaperAnalysis(
            paper_id="2025.0001",
            relevance_score=0.95,
            significance_score=0.92,
            novelty_score=0.88,
            summary="This paper introduces a revolutionary reasoning architecture that combines symbolic and neural approaches, achieving 40% improvement in complex reasoning tasks.",
            key_insights=[
                "Novel hybrid architecture bridges symbolic and neural reasoning",
                "40% performance improvement on complex benchmarks",
                "Significant implications for AI safety and AGI development",
                "Could accelerate autonomous system capabilities"
            ],
            technical_details="The approach uses a dual-pathway architecture where symbolic reasoning modules guide neural network attention mechanisms, enabling more structured and interpretable reasoning processes.",
            potential_impact="This breakthrough could accelerate progress toward artificial general intelligence and improve AI safety through more interpretable reasoning processes.",
            implementation_difficulty="Expert - requires deep understanding of both symbolic AI and neural architectures",
            business_relevance="High - potential applications in autonomous systems, AI assistants, and decision-making platforms. Could create competitive advantages in enterprise AI solutions.",
            connections_to_other_work=["Neuro-symbolic AI", "Transformer architectures", "Chain-of-thought reasoning"],
            recommended_for=["AI researchers", "ML engineers", "AGI developers", "AI safety researchers"],
            tags=["reasoning", "neuro-symbolic", "breakthrough", "AGI", "safety"]
        ),
        PaperAnalysis(
            paper_id="2025.0002",
            relevance_score=0.88,
            significance_score=0.85,
            novelty_score=0.82,
            summary="Presents an efficient decentralized framework for multi-agent coordination with 60% faster convergence than existing methods.",
            key_insights=[
                "Decentralized decision-making with global optimization",
                "60% faster convergence than current methods",
                "Applicable to robotics and autonomous vehicles",
                "Reduces computational overhead significantly"
            ],
            technical_details="Uses a consensus-based algorithm with distributed optimization, allowing agents to coordinate without centralized control while maintaining system-wide efficiency.",
            potential_impact="Could enable more scalable and robust autonomous systems, particularly in robotics and IoT applications.",
            implementation_difficulty="Medium - requires understanding of distributed systems and optimization theory",
            business_relevance="High - direct applications in autonomous vehicles, drone swarms, and industrial automation. Could reduce infrastructure costs significantly.",
            connections_to_other_work=["Multi-agent reinforcement learning", "Consensus algorithms", "Distributed optimization"],
            recommended_for=["Robotics engineers", "Autonomous systems developers", "Distributed systems researchers"],
            tags=["multi-agent", "coordination", "efficiency", "robotics", "autonomous"]
        ),
        PaperAnalysis(
            paper_id="2025.0003",
            relevance_score=0.90,
            significance_score=0.87,
            novelty_score=0.85,
            summary="VisionLM-Ultra achieves human-level performance on visual reasoning through novel attention mechanisms bridging vision and language.",
            key_insights=[
                "Human-level performance on complex visual reasoning tasks",
                "Novel attention mechanism for vision-language integration",
                "Opens possibilities for creative AI applications",
                "Advances human-computer interaction capabilities"
            ],
            technical_details="Introduces cross-modal attention gates that dynamically weight visual and textual features based on task requirements, enabling more nuanced understanding of visual-linguistic relationships.",
            potential_impact="Could revolutionize applications requiring visual understanding, from autonomous navigation to creative content generation.",
            implementation_difficulty="Hard - requires expertise in computer vision, NLP, and multimodal architectures",
            business_relevance="Very High - applications in content creation, visual search, autonomous systems, and accessibility technologies. Large market potential.",
            connections_to_other_work=["CLIP", "DALL-E", "Multimodal transformers", "Visual question answering"],
            recommended_for=["Computer vision researchers", "Multimodal AI developers", "Product managers in AI"],
            tags=["vision-language", "multimodal", "breakthrough", "human-level", "creative-ai"]
        )
    ]
    
    return sample_papers, sample_analyses


async def send_test_digest():
    """Send a test digest email"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("🧪 Creating test ArXiv research digest...")
    
    # Create sample data
    papers, analyses = await create_sample_data()
    
    # Initialize components
    config = ConfigManager()
    digest_generator = DigestGenerator("output")
    
    # Generate HTML digest for viewing
    html_file = digest_generator.generate_html_digest(
        papers, analyses, 
        title="🧪 Test AI Research Digest - ArXiv Agent Demo"
    )
    logger.info(f"📄 Generated HTML test digest: {html_file}")
    
    # Generate email content
    email_content = digest_generator.generate_email_content(papers, analyses)
    
    # Email configuration for Gmail
    email_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'donvon@vonbase.com',  # This needs to be configured
        'password': '',  # This needs to be set via environment variable
        'from_email': 'donvon@vonbase.com'
    }
    
    # Check if email password is available
    email_password = os.getenv('ARXIV_AGENT_EMAIL_PASSWORD')
    if not email_password:
        logger.warning("⚠️  Email password not set in ARXIV_AGENT_EMAIL_PASSWORD environment variable")
        logger.info("📧 Email content preview:")
        print("\n" + "="*60)
        print(email_content)
        print("="*60)
        
        logger.info(f"📄 Full HTML digest saved to: {html_file}")
        logger.info("🔗 Open the HTML file in a browser to see the full digest")
        return False
    
    # Send test email
    email_config['password'] = email_password
    
    subject = f"🧪 Test AI Research Digest - {datetime.now().strftime('%Y-%m-%d')}"
    
    success = await digest_generator.send_email(
        subject=subject,
        content=email_content,
        to_email="donvon@vonbase.com",
        smtp_config=email_config
    )
    
    if success:
        logger.info("✅ Test email sent successfully to donvon@vonbase.com!")
    else:
        logger.error("❌ Failed to send test email")
    
    logger.info(f"📄 Full HTML digest saved to: {html_file}")
    return success


async def main():
    """Main function"""
    
    print("🤖 ArXiv Research Agent - Test Email")
    print("=" * 50)
    
    # Set API key if provided
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY not set - using sample data only")
    
    # Send test digest
    success = await send_test_digest()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("📧 Check donvon@vonbase.com for the test digest email")
    else:
        print("\n📄 Test digest generated (email not sent)")
        print("🔍 Check the output/ directory for HTML digest")


if __name__ == "__main__":
    asyncio.run(main())