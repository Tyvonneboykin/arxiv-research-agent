#!/usr/bin/env python3
"""
Claude Code SDK Paper Analyzer
==============================

Uses Claude Code SDK to intelligently analyze and summarize research papers.
"""

import asyncio
import logging
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

try:
    from claude_code_sdk import query, ClaudeCodeOptions
except ImportError:
    print("Error: claude-code-sdk not installed. Run: pip install claude-code-sdk")
    sys.exit(1)

from arxiv_fetcher import ArxivPaper


@dataclass
class PaperAnalysis:
    """Results of Claude's paper analysis"""
    paper_id: str
    relevance_score: float
    significance_score: float
    novelty_score: float
    summary: str
    key_insights: List[str]
    technical_details: str
    potential_impact: str
    implementation_difficulty: str
    business_relevance: str
    connections_to_other_work: List[str]
    recommended_for: List[str]  # audience types
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'paper_id': self.paper_id,
            'relevance_score': self.relevance_score,
            'significance_score': self.significance_score,
            'novelty_score': self.novelty_score,
            'summary': self.summary,
            'key_insights': self.key_insights,
            'technical_details': self.technical_details,
            'potential_impact': self.potential_impact,
            'implementation_difficulty': self.implementation_difficulty,
            'business_relevance': self.business_relevance,
            'connections_to_other_work': self.connections_to_other_work,
            'recommended_for': self.recommended_for,
            'tags': self.tags
        }


class ClaudeAnalyzer:
    """Uses Claude Code SDK for intelligent paper analysis"""
    
    def __init__(self, working_dir: str = None):
        self.working_dir = working_dir or os.getcwd()
        self.logger = logging.getLogger(__name__)
        
        # Configure Claude options
        self.claude_options = ClaudeCodeOptions(
            cwd=self.working_dir,
            permission_mode="acceptEdits",
            max_turns=3,
            max_thinking_tokens=8000
        )
        
        # Analysis templates
        self.analysis_prompt_template = """
You are an expert AI research analyst. Analyze the following research paper and provide a comprehensive analysis.

Paper Information:
Title: {title}
Authors: {authors}
Abstract: {abstract}
Categories: {categories}
arXiv ID: {arxiv_id}

Please analyze this paper and provide the following information in JSON format:

{{
    "relevance_score": <float 0-1 indicating how relevant this is to current AI trends>,
    "significance_score": <float 0-1 indicating potential significance to the field>,
    "novelty_score": <float 0-1 indicating how novel/groundbreaking this work is>,
    "summary": "<2-3 sentence summary of the main contribution>",
    "key_insights": ["<insight 1>", "<insight 2>", "<insight 3>"],
    "technical_details": "<technical explanation for experts>",
    "potential_impact": "<assessment of potential real-world impact>",
    "implementation_difficulty": "<assessment: Easy/Medium/Hard/Expert and why>",
    "business_relevance": "<how this could affect commercial AI applications>",
    "connections_to_other_work": ["<related paper/concept 1>", "<related paper/concept 2>"],
    "recommended_for": ["<audience type 1>", "<audience type 2>"],
    "tags": ["<tag1>", "<tag2>", "<tag3>"]
}}

Focus on:
1. What makes this work novel or significant
2. How it advances the state of the art
3. Practical implications and applications
4. Technical innovations and methodologies
5. Potential limitations or concerns

Be concise but thorough. Provide honest assessments of significance and relevance.
"""
        
        self.batch_analysis_prompt = """
You are an expert AI research analyst reviewing multiple papers to identify trends and highlight the most important work.

Papers to analyze:
{papers_info}

Please provide:
1. Overall trends and themes you notice across these papers
2. Rank the top 5 most significant papers and explain why
3. Identify any breakthrough or paradigm-shifting work
4. Note any concerning developments or limitations
5. Predict future research directions based on these papers

Format your response as structured analysis focusing on actionable insights for AI researchers and practitioners.
"""
    
    async def analyze_paper(self, paper: ArxivPaper, 
                           research_interests: List[str] = None) -> Optional[PaperAnalysis]:
        """Analyze a single paper using Claude"""
        try:
            # Prepare the prompt
            prompt = self.analysis_prompt_template.format(
                title=paper.title,
                authors=", ".join(paper.authors),
                abstract=paper.abstract,
                categories=", ".join(paper.categories),
                arxiv_id=paper.id
            )
            
            if research_interests:
                prompt += f"\n\nUser's research interests: {', '.join(research_interests)}"
                prompt += "\nConsider relevance to these specific interests in your analysis."
            
            self.logger.info(f"Analyzing paper: {paper.title[:50]}...")
            
            # Query Claude
            responses = []
            async for message in query(prompt=prompt, options=self.claude_options):
                if hasattr(message, 'content'):
                    if isinstance(message.content, str):
                        responses.append(message.content)
                    elif hasattr(message.content, '__iter__'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                responses.append(block.text)
            
            if not responses:
                self.logger.error(f"No response from Claude for paper {paper.id}")
                return None
            
            # Parse the JSON response
            full_response = " ".join(responses)
            
            # Extract JSON from response
            json_start = full_response.find('{')
            json_end = full_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                self.logger.error(f"No JSON found in Claude response for paper {paper.id}")
                return None
            
            json_str = full_response[json_start:json_end]
            analysis_data = json.loads(json_str)
            
            # Create PaperAnalysis object
            analysis = PaperAnalysis(
                paper_id=paper.id,
                relevance_score=analysis_data.get('relevance_score', 0.5),
                significance_score=analysis_data.get('significance_score', 0.5),
                novelty_score=analysis_data.get('novelty_score', 0.5),
                summary=analysis_data.get('summary', ''),
                key_insights=analysis_data.get('key_insights', []),
                technical_details=analysis_data.get('technical_details', ''),
                potential_impact=analysis_data.get('potential_impact', ''),
                implementation_difficulty=analysis_data.get('implementation_difficulty', ''),
                business_relevance=analysis_data.get('business_relevance', ''),
                connections_to_other_work=analysis_data.get('connections_to_other_work', []),
                recommended_for=analysis_data.get('recommended_for', []),
                tags=analysis_data.get('tags', [])
            )
            
            self.logger.info(f"Successfully analyzed paper {paper.id}")
            return analysis
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error for paper {paper.id}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error analyzing paper {paper.id}: {e}")
            return None
    
    async def analyze_paper_batch(self, papers: List[ArxivPaper], 
                                 research_interests: List[str] = None) -> List[PaperAnalysis]:
        """Analyze multiple papers concurrently"""
        tasks = []
        
        # Limit concurrent requests to avoid rate limiting
        semaphore = asyncio.Semaphore(3)
        
        async def analyze_with_semaphore(paper):
            async with semaphore:
                return await self.analyze_paper(paper, research_interests)
        
        for paper in papers:
            task = asyncio.create_task(analyze_with_semaphore(paper))
            tasks.append(task)
        
        # Wait for all analyses to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and None results
        analyses = []
        for result in results:
            if isinstance(result, PaperAnalysis):
                analyses.append(result)
            elif isinstance(result, Exception):
                self.logger.error(f"Analysis task failed: {result}")
        
        return analyses
    
    async def identify_trends(self, analyses: List[PaperAnalysis]) -> Dict[str, Any]:
        """Use Claude to identify trends across multiple paper analyses"""
        if not analyses:
            return {"trends": [], "top_papers": [], "predictions": []}
        
        # Prepare papers info for batch analysis
        papers_info = []
        for analysis in analyses:
            paper_info = {
                "id": analysis.paper_id,
                "summary": analysis.summary,
                "significance_score": analysis.significance_score,
                "novelty_score": analysis.novelty_score,
                "tags": analysis.tags,
                "key_insights": analysis.key_insights
            }
            papers_info.append(paper_info)
        
        prompt = self.batch_analysis_prompt.format(
            papers_info=json.dumps(papers_info, indent=2)
        )
        
        try:
            responses = []
            async for message in query(prompt=prompt, options=self.claude_options):
                if hasattr(message, 'content'):
                    if isinstance(message.content, str):
                        responses.append(message.content)
                    elif hasattr(message.content, '__iter__'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                responses.append(block.text)
            
            trend_analysis = " ".join(responses)
            
            return {
                "analysis_date": datetime.now().isoformat(),
                "papers_analyzed": len(analyses),
                "trend_analysis": trend_analysis
            }
            
        except Exception as e:
            self.logger.error(f"Error in trend analysis: {e}")
            return {"error": str(e)}
    
    def rank_papers(self, analyses: List[PaperAnalysis], 
                   criteria: str = "overall") -> List[Tuple[ArxivPaper, PaperAnalysis]]:
        """Rank papers based on various criteria"""
        
        if criteria == "relevance":
            key_func = lambda x: x.relevance_score
        elif criteria == "significance":
            key_func = lambda x: x.significance_score
        elif criteria == "novelty":
            key_func = lambda x: x.novelty_score
        else:  # overall
            key_func = lambda x: (x.significance_score + x.novelty_score + x.relevance_score) / 3
        
        ranked_analyses = sorted(analyses, key=key_func, reverse=True)
        return ranked_analyses
    
    async def generate_daily_insights(self, analyses: List[PaperAnalysis]) -> str:
        """Generate daily insights summary using Claude"""
        if not analyses:
            return "No papers analyzed today."
        
        # Get top papers
        top_papers = self.rank_papers(analyses)[:5]
        
        # Prepare summary data
        summary_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "papers_analyzed": len(analyses),
            "top_papers": [
                {
                    "id": analysis.paper_id,
                    "summary": analysis.summary,
                    "significance": analysis.significance_score,
                    "key_insights": analysis.key_insights[:2]
                }
                for analysis in top_papers
            ]
        }
        
        prompt = f"""
Create a daily AI research insights summary for {summary_data['date']}.

Data: {json.dumps(summary_data, indent=2)}

Please create a well-formatted daily digest including:
1. Executive summary of key developments
2. Highlight the most significant papers with brief explanations
3. Emerging trends or patterns
4. Key takeaways for AI practitioners
5. Notable quotes or insights

Keep it engaging and actionable. Format in markdown.
"""
        
        try:
            responses = []
            async for message in query(prompt=prompt, options=self.claude_options):
                if hasattr(message, 'content'):
                    if isinstance(message.content, str):
                        responses.append(message.content)
                    elif hasattr(message.content, '__iter__'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                responses.append(block.text)
            
            return " ".join(responses)
            
        except Exception as e:
            self.logger.error(f"Error generating daily insights: {e}")
            return f"Error generating insights: {e}"


# Example usage
async def main():
    """Example usage of ClaudeAnalyzer"""
    logging.basicConfig(level=logging.INFO)
    
    # This would normally come from arxiv_fetcher
    from arxiv_fetcher import ArxivFetcher
    
    async with ArxivFetcher() as fetcher:
        papers = await fetcher.fetch_ai_papers(days_back=1, max_results=5)
        
    if papers:
        analyzer = ClaudeAnalyzer()
        
        # Analyze first paper
        analysis = await analyzer.analyze_paper(papers[0])
        if analysis:
            print(f"Analysis for: {papers[0].title}")
            print(f"Significance: {analysis.significance_score:.2f}")
            print(f"Summary: {analysis.summary}")
            print(f"Key insights: {analysis.key_insights}")


if __name__ == "__main__":
    asyncio.run(main())