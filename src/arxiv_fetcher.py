#!/usr/bin/env python3
"""
ArXiv Paper Fetcher
==================

Fetches latest papers from arXiv API with intelligent filtering.
"""

import asyncio
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import aiohttp
import re


@dataclass
class ArxivPaper:
    """Represents a paper from arXiv"""
    id: str
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published: datetime
    updated: datetime
    pdf_url: str
    arxiv_url: str
    primary_category: str
    
    def __post_init__(self):
        # Clean up title and abstract
        self.title = re.sub(r'\s+', ' ', self.title.strip())
        self.abstract = re.sub(r'\s+', ' ', self.abstract.strip())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'categories': self.categories,
            'published': self.published.isoformat(),
            'updated': self.updated.isoformat(),
            'pdf_url': self.pdf_url,
            'arxiv_url': self.arxiv_url,
            'primary_category': self.primary_category
        }


class ArxivFetcher:
    """Fetches and filters papers from arXiv"""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _parse_paper(self, entry: ET.Element) -> Optional[ArxivPaper]:
        """Parse a single paper entry from arXiv XML"""
        try:
            # Extract ID
            id_elem = entry.find('{http://www.w3.org/2005/Atom}id')
            if id_elem is None:
                return None
            
            paper_id = id_elem.text.split('/')[-1]
            
            # Extract title
            title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
            title = title_elem.text if title_elem is not None else ""
            
            # Extract authors
            authors = []
            for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                name_elem = author.find('{http://www.w3.org/2005/Atom}name')
                if name_elem is not None:
                    authors.append(name_elem.text)
            
            # Extract abstract
            abstract_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
            abstract = abstract_elem.text if abstract_elem is not None else ""
            
            # Extract categories
            categories = []
            primary_category = ""
            
            for category in entry.findall('{http://arxiv.org/schemas/atom}category'):
                term = category.get('term', '')
                if term:
                    categories.append(term)
            
            # Primary category
            primary_cat_elem = entry.find('{http://arxiv.org/schemas/atom}primary_category')
            if primary_cat_elem is not None:
                primary_category = primary_cat_elem.get('term', '')
            
            # Extract dates
            published_elem = entry.find('{http://www.w3.org/2005/Atom}published')
            updated_elem = entry.find('{http://www.w3.org/2005/Atom}updated')
            
            published = datetime.fromisoformat(published_elem.text.replace('Z', '+00:00')) if published_elem is not None else datetime.now()
            updated = datetime.fromisoformat(updated_elem.text.replace('Z', '+00:00')) if updated_elem is not None else published
            
            # Extract URLs
            pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
            arxiv_url = f"https://arxiv.org/abs/{paper_id}"
            
            return ArxivPaper(
                id=paper_id,
                title=title,
                authors=authors,
                abstract=abstract,
                categories=categories,
                published=published,
                updated=updated,
                pdf_url=pdf_url,
                arxiv_url=arxiv_url,
                primary_category=primary_category
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing paper entry: {e}")
            return None
    
    async def fetch_papers(self, 
                          categories: List[str] = None,
                          max_results: int = 100,
                          days_back: int = 7,
                          keywords: List[str] = None) -> List[ArxivPaper]:
        """
        Fetch papers from arXiv
        
        Args:
            categories: List of arXiv categories (e.g., ['cs.AI', 'cs.LG'])
            max_results: Maximum number of papers to fetch
            days_back: How many days back to search
            keywords: Keywords to search for in title/abstract
        """
        if not self.session:
            raise RuntimeError("ArxivFetcher must be used as async context manager")
        
        # Build search query
        query_parts = []
        
        # Add category filters
        if categories:
            cat_query = " OR ".join(f"cat:{cat}" for cat in categories)
            query_parts.append(f"({cat_query})")
        
        # Add keyword filters
        if keywords:
            keyword_query = " AND ".join(f'(ti:"{kw}" OR abs:"{kw}")' for kw in keywords)
            query_parts.append(f"({keyword_query})")
        
        # Combine query parts
        search_query = " AND ".join(query_parts) if query_parts else "cat:cs.AI"
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        self.logger.info(f"Fetching papers with query: {search_query}")
        
        try:
            async with self.session.get(self.BASE_URL, params=params) as response:
                if response.status != 200:
                    self.logger.error(f"ArXiv API error: {response.status}")
                    return []
                
                content = await response.text()
                
            # Parse XML response
            root = ET.fromstring(content)
            papers = []
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                paper = self._parse_paper(entry)
                if paper and paper.published >= start_date:
                    papers.append(paper)
            
            self.logger.info(f"Fetched {len(papers)} papers")
            return papers
            
        except Exception as e:
            self.logger.error(f"Error fetching papers: {e}")
            return []
    
    async def fetch_ai_papers(self, days_back: int = 1, max_results: int = 50) -> List[ArxivPaper]:
        """Fetch latest AI-related papers"""
        ai_categories = [
            'cs.AI',   # Artificial Intelligence
            'cs.LG',   # Machine Learning
            'cs.CL',   # Computation and Language
            'cs.CV',   # Computer Vision
            'cs.RO',   # Robotics
            'stat.ML'  # Machine Learning (stats)
        ]
        
        ai_keywords = [
            'artificial intelligence',
            'machine learning',
            'deep learning',
            'neural network',
            'large language model',
            'LLM',
            'transformer',
            'GPT',
            'BERT',
            'diffusion',
            'reinforcement learning',
            'computer vision',
            'natural language processing',
            'NLP'
        ]
        
        return await self.fetch_papers(
            categories=ai_categories,
            max_results=max_results,
            days_back=days_back,
            keywords=ai_keywords
        )
    
    def filter_papers(self, papers: List[ArxivPaper], 
                     exclude_keywords: List[str] = None,
                     min_relevance_score: float = 0.5) -> List[ArxivPaper]:
        """Filter papers based on various criteria"""
        filtered = []
        exclude_keywords = exclude_keywords or ['survey', 'review', 'tutorial']
        
        for paper in papers:
            # Check for excluded keywords
            text_to_check = (paper.title + " " + paper.abstract).lower()
            
            if any(keyword.lower() in text_to_check for keyword in exclude_keywords):
                continue
            
            # Add basic relevance scoring
            relevance_score = self._calculate_relevance_score(paper)
            if relevance_score >= min_relevance_score:
                filtered.append(paper)
        
        return filtered
    
    def _calculate_relevance_score(self, paper: ArxivPaper) -> float:
        """Calculate relevance score for a paper (basic version)"""
        # This is a simple scoring system - can be enhanced with AI
        score = 0.0
        
        high_value_keywords = [
            'breakthrough', 'novel', 'state-of-the-art', 'sota', 
            'significant', 'improvement', 'outperforms', 'beats',
            'first', 'new', 'innovative', 'groundbreaking'
        ]
        
        text = (paper.title + " " + paper.abstract).lower()
        
        # Boost score for high-value keywords
        for keyword in high_value_keywords:
            if keyword in text:
                score += 0.2
        
        # Boost for recent papers
        days_old = (datetime.now() - paper.published).days
        if days_old <= 1:
            score += 0.3
        elif days_old <= 3:
            score += 0.2
        elif days_old <= 7:
            score += 0.1
        
        # Boost for popular categories
        if paper.primary_category in ['cs.AI', 'cs.LG']:
            score += 0.2
        
        return min(score, 1.0)


# Example usage
async def main():
    """Example usage of ArxivFetcher"""
    logging.basicConfig(level=logging.INFO)
    
    async with ArxivFetcher() as fetcher:
        # Fetch latest AI papers
        papers = await fetcher.fetch_ai_papers(days_back=1, max_results=20)
        
        # Filter papers
        filtered_papers = fetcher.filter_papers(papers)
        
        print(f"Found {len(filtered_papers)} relevant papers:")
        for paper in filtered_papers[:5]:
            print(f"\n📄 {paper.title}")
            print(f"👥 Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
            print(f"🔗 {paper.arxiv_url}")
            print(f"📝 {paper.abstract[:200]}...")


if __name__ == "__main__":
    asyncio.run(main())