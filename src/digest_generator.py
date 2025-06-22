#!/usr/bin/env python3
"""
Research Digest Generator
========================

Generates formatted research digests in multiple formats (HTML, Markdown, Email, Discord).
"""

import json
import logging
import smtplib
import ssl
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List, Dict, Any, Optional
import aiohttp

from arxiv_fetcher import ArxivPaper
from claude_analyzer import PaperAnalysis


class DigestGenerator:
    """Generates research digests in multiple formats"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or "output")
        
        # Ensure directory exists and handle Windows paths via WSL
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.logger = logging.getLogger(__name__)
            self.logger.info(f"📁 Output directory configured: {self.output_dir}")
        except Exception as e:
            self.logger = logging.getLogger(__name__)
            self.logger.error(f"❌ Failed to create output directory {self.output_dir}: {e}")
            # Fallback to local directory
            self.output_dir = Path("output")
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.logger.warning(f"⚠️  Using fallback directory: {self.output_dir}")
    
    def generate_html_digest(self, papers: List[ArxivPaper], 
                           analyses: List[PaperAnalysis],
                           title: str = "AI Research Digest") -> str:
        """Generate HTML digest"""
        
        # Combine papers and analyses
        paper_dict = {p.id: p for p in papers}
        combined_data = []
        
        for analysis in analyses:
            if analysis.paper_id in paper_dict:
                combined_data.append((paper_dict[analysis.paper_id], analysis))
        
        # Sort by significance score
        combined_data.sort(key=lambda x: x[1].significance_score, reverse=True)
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .stats {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .paper-card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
        }}
        .paper-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .paper-authors {{
            color: #7f8c8d;
            margin-bottom: 15px;
        }}
        .scores {{
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }}
        .score {{
            background: #ecf0f1;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .score.high {{ background: #2ecc71; color: white; }}
        .score.medium {{ background: #f39c12; color: white; }}
        .score.low {{ background: #e74c3c; color: white; }}
        .summary {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 3px solid #667eea;
        }}
        .insights {{
            margin: 15px 0;
        }}
        .insight-item {{
            background: #e8f4f8;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #3498db;
        }}
        .tags {{
            margin-top: 15px;
        }}
        .tag {{
            background: #667eea;
            color: white;
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 0.8em;
            margin-right: 8px;
            display: inline-block;
            margin-bottom: 5px;
        }}
        .links {{
            margin-top: 15px;
        }}
        .link {{
            display: inline-block;
            background: #34495e;
            color: white;
            padding: 8px 15px;
            text-decoration: none;
            border-radius: 5px;
            margin-right: 10px;
            margin-bottom: 5px;
        }}
        .link:hover {{
            background: #2c3e50;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>Generated on {date}</p>
    </div>
    
    <div class="stats">
        <h2>📊 Summary Statistics</h2>
        <p><strong>Papers Analyzed:</strong> {total_papers}</p>
        <p><strong>High Significance Papers:</strong> {high_sig_count}</p>
        <p><strong>Average Novelty Score:</strong> {avg_novelty:.2f}</p>
        <p><strong>Top Research Areas:</strong> {top_categories}</p>
    </div>
    
    <div class="papers">
        {papers_html}
    </div>
    
    <div class="footer">
        <p>Generated by AI Research Agent using Claude Code SDK</p>
        <p>This digest analyzed {total_papers} papers from arXiv</p>
    </div>
</body>
</html>
"""
        
        def get_score_class(score):
            if score >= 0.7:
                return "high"
            elif score >= 0.4:
                return "medium"
            else:
                return "low"
        
        # Generate papers HTML
        papers_html = ""
        for paper, analysis in combined_data:
            
            insights_html = ""
            for insight in analysis.key_insights:
                insights_html += f'<div class="insight-item">💡 {insight}</div>'
            
            tags_html = ""
            for tag in analysis.tags:
                tags_html += f'<span class="tag">{tag}</span>'
            
            papers_html += f"""
            <div class="paper-card">
                <div class="paper-title">{paper.title}</div>
                <div class="paper-authors">👥 {', '.join(paper.authors[:5])}{'...' if len(paper.authors) > 5 else ''}</div>
                
                <div class="scores">
                    <div class="score {get_score_class(analysis.significance_score)}">
                        Significance: {analysis.significance_score:.2f}
                    </div>
                    <div class="score {get_score_class(analysis.novelty_score)}">
                        Novelty: {analysis.novelty_score:.2f}
                    </div>
                    <div class="score {get_score_class(analysis.relevance_score)}">
                        Relevance: {analysis.relevance_score:.2f}
                    </div>
                </div>
                
                <div class="summary">
                    <strong>📝 Summary:</strong> {analysis.summary}
                </div>
                
                <div class="insights">
                    <strong>🔍 Key Insights:</strong>
                    {insights_html}
                </div>
                
                <div>
                    <strong>💼 Business Impact:</strong> {analysis.business_relevance}
                </div>
                
                <div>
                    <strong>🛠️ Implementation:</strong> {analysis.implementation_difficulty}
                </div>
                
                <div class="tags">
                    {tags_html}
                </div>
                
                <div class="links">
                    <a href="{paper.arxiv_url}" class="link" target="_blank">📄 arXiv</a>
                    <a href="{paper.pdf_url}" class="link" target="_blank">📥 PDF</a>
                </div>
            </div>
            """
        
        # Calculate statistics
        total_papers = len(analyses)
        high_sig_count = len([a for a in analyses if a.significance_score >= 0.7])
        avg_novelty = sum(a.novelty_score for a in analyses) / len(analyses) if analyses else 0
        
        # Get top categories
        all_tags = []
        for analysis in analyses:
            all_tags.extend(analysis.tags)
        
        from collections import Counter
        tag_counts = Counter(all_tags)
        top_categories = ", ".join([tag for tag, _ in tag_counts.most_common(5)])
        
        # Fill template
        html_content = html_template.format(
            title=title,
            date=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            total_papers=total_papers,
            high_sig_count=high_sig_count,
            avg_novelty=avg_novelty,
            top_categories=top_categories or "Various",
            papers_html=papers_html
        )
        
        # Save to file
        output_file = self.output_dir / f"digest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Generated HTML digest: {output_file}")
        return str(output_file)
    
    def generate_markdown_digest(self, papers: List[ArxivPaper], 
                               analyses: List[PaperAnalysis],
                               title: str = "AI Research Digest") -> str:
        """Generate Markdown digest"""
        
        # Combine and sort papers
        paper_dict = {p.id: p for p in papers}
        combined_data = []
        
        for analysis in analyses:
            if analysis.paper_id in paper_dict:
                combined_data.append((paper_dict[analysis.paper_id], analysis))
        
        combined_data.sort(key=lambda x: x[1].significance_score, reverse=True)
        
        # Generate markdown
        markdown_content = f"""# {title}
*Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}*

## 📊 Summary Statistics
- **Papers Analyzed:** {len(analyses)}
- **High Significance Papers:** {len([a for a in analyses if a.significance_score >= 0.7])}
- **Average Novelty Score:** {sum(a.novelty_score for a in analyses) / len(analyses):.2f if analyses else 0}

---

"""
        
        for i, (paper, analysis) in enumerate(combined_data, 1):
            score_emoji = "🔥" if analysis.significance_score >= 0.8 else "⭐" if analysis.significance_score >= 0.6 else "📄"
            
            markdown_content += f"""## {score_emoji} {i}. {paper.title}

**Authors:** {', '.join(paper.authors[:5])}{'...' if len(paper.authors) > 5 else ''}

**Scores:** Significance: {analysis.significance_score:.2f} | Novelty: {analysis.novelty_score:.2f} | Relevance: {analysis.relevance_score:.2f}

### 📝 Summary
{analysis.summary}

### 🔍 Key Insights
"""
            for insight in analysis.key_insights:
                markdown_content += f"- {insight}\n"
            
            markdown_content += f"""
### 💼 Business Impact
{analysis.business_relevance}

### 🛠️ Implementation
{analysis.implementation_difficulty}

**Tags:** {', '.join(analysis.tags)}

**Links:** [arXiv]({paper.arxiv_url}) | [PDF]({paper.pdf_url})

---

"""
        
        # Save to file
        output_file = self.output_dir / f"digest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        self.logger.info(f"Generated Markdown digest: {output_file}")
        return str(output_file)
    
    def generate_email_content(self, papers: List[ArxivPaper], 
                             analyses: List[PaperAnalysis]) -> str:
        """Generate email-friendly content"""
        
        # Sort by significance
        paper_dict = {p.id: p for p in papers}
        sorted_analyses = sorted(analyses, key=lambda x: x.significance_score, reverse=True)
        
        email_content = f"""📚 AI Research Digest - {datetime.now().strftime("%B %d, %Y")}

🔬 {len(analyses)} papers analyzed | 🔥 {len([a for a in analyses if a.significance_score >= 0.7])} high-significance papers

"""
        
        for i, analysis in enumerate(sorted_analyses[:5], 1):
            if analysis.paper_id in paper_dict:
                paper = paper_dict[analysis.paper_id]
                
                score_indicator = "🔥" if analysis.significance_score >= 0.8 else "⭐" if analysis.significance_score >= 0.6 else "📄"
                
                email_content += f"""{score_indicator} {i}. {paper.title}

👥 {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}
📊 Significance: {analysis.significance_score:.2f} | Novelty: {analysis.novelty_score:.2f}

📝 {analysis.summary}

💡 Key insight: {analysis.key_insights[0] if analysis.key_insights else 'Novel contribution to the field'}

🔗 Read more: {paper.arxiv_url}

---

"""
        
        email_content += f"""
📈 Generated by AI Research Agent
🤖 Powered by Claude Code SDK

Unsubscribe or modify preferences at your agent dashboard.
"""
        
        return email_content
    
    async def send_email(self, subject: str, content: str, 
                        to_email: str, smtp_config: Dict[str, Any]) -> bool:
        """Send email digest"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_config['from_email']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(content, 'plain'))
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port']) as server:
                server.starttls(context=context)
                server.login(smtp_config['username'], smtp_config['password'])
                server.sendmail(smtp_config['from_email'], to_email, msg.as_string())
            
            self.logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    async def send_discord_webhook(self, content: str, webhook_url: str) -> bool:
        """Send digest to Discord via webhook"""
        try:
            # Discord has a 2000 character limit, so we need to truncate
            if len(content) > 1900:
                content = content[:1900] + "...\n\n(Truncated - check full digest)"
            
            payload = {
                "content": content,
                "username": "AI Research Agent",
                "avatar_url": "https://cdn-icons-png.flaticon.com/512/4712/4712027.png"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 204:
                        self.logger.info("Discord webhook sent successfully")
                        return True
                    else:
                        self.logger.error(f"Discord webhook failed: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Failed to send Discord webhook: {e}")
            return False
    
    def save_json_digest(self, papers: List[ArxivPaper], 
                        analyses: List[PaperAnalysis]) -> str:
        """Save digest data as JSON for programmatic access"""
        
        digest_data = {
            "generated_at": datetime.now().isoformat(),
            "papers_count": len(papers),
            "analyses_count": len(analyses),
            "papers": [paper.to_dict() for paper in papers],
            "analyses": [analysis.to_dict() for analysis in analyses]
        }
        
        output_file = self.output_dir / f"digest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(digest_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved JSON digest: {output_file}")
        return str(output_file)


# Example usage
async def main():
    """Example usage of DigestGenerator"""
    import asyncio
    from arxiv_fetcher import ArxivFetcher
    from claude_analyzer import ClaudeAnalyzer
    
    logging.basicConfig(level=logging.INFO)
    
    # Fetch some papers (mock for example)
    papers = []  # Would come from ArxivFetcher
    analyses = []  # Would come from ClaudeAnalyzer
    
    generator = DigestGenerator()
    
    if papers and analyses:
        # Generate multiple formats
        html_file = generator.generate_html_digest(papers, analyses)
        md_file = generator.generate_markdown_digest(papers, analyses)
        json_file = generator.save_json_digest(papers, analyses)
        
        print(f"Generated digests:")
        print(f"  HTML: {html_file}")
        print(f"  Markdown: {md_file}")
        print(f"  JSON: {json_file}")
        
        # Example email content
        email_content = generator.generate_email_content(papers, analyses)
        print("\nEmail preview:")
        print(email_content[:500] + "...")


if __name__ == "__main__":
    asyncio.run(main())