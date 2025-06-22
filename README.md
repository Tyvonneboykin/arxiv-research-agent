# 🤖 ArXiv Research Agent

A sophisticated 24/7 AI-powered research assistant that monitors arXiv, analyzes papers using Claude Code SDK, and generates intelligent research digests.

## 🌟 Features

### 🔍 Intelligent Paper Analysis
- **Claude-powered analysis** of research papers with significance scoring
- **Relevance filtering** based on your research interests
- **Trend identification** across multiple papers
- **Key insight extraction** with business and technical impact assessment

### 📊 Multi-Format Outputs
- **Beautiful HTML digests** with interactive elements
- **Markdown summaries** for documentation
- **JSON data exports** for programmatic access
- **Email newsletters** with customizable templates

### 🔄 Automated Scheduling
- **Daily digests** at configurable times
- **Weekly trend summaries** with cross-paper analysis
- **Real-time monitoring** (optional) for breaking research

### 📧 Smart Notifications
- **Email integration** with SMTP support
- **Discord webhooks** for team notifications
- **Customizable alerting** based on significance thresholds

## 🚀 Quick Start

### 1. Setup

```bash
# Clone or create the project directory
cd /path/to/arxiv-research-agent

# Run the setup script
python setup.py
```

### 2. Configuration

Edit `.env` with your API keys:
```env
ANTHROPIC_API_KEY=your_claude_api_key_here
ARXIV_AGENT_EMAIL_USERNAME=your_email@example.com
ARXIV_AGENT_EMAIL_PASSWORD=your_app_password
ARXIV_AGENT_DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
```

Customize `config/config.yaml` for your research interests:
```yaml
research:
  interests:
    - "Large Language Models"
    - "AI Agents"
    - "Computer Vision"
  arxiv_categories:
    - "cs.AI"
    - "cs.LG"
    - "cs.CV"
```

### 3. Test & Run

```bash
# Test configuration
python src/research_agent.py --test

# Run once (for testing)
python src/research_agent.py --once

# Start 24/7 agent
python src/research_agent.py
```

### 4. Install as System Service (Optional)

```bash
# Install systemd service for 24/7 operation
sudo cp arxiv-research-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable arxiv-research-agent
sudo systemctl start arxiv-research-agent
```

## 💰 Cost Analysis

### Expected Monthly Costs
- **Light usage** (daily digest): ~$15-30/month
- **Heavy usage** (hourly monitoring): ~$50-100/month
- **Enterprise** (custom analysis): ~$100-200/month

### Cost Optimization
- Uses Claude 3.5 Haiku for simple analysis ($0.80/1M tokens)
- Intelligent filtering reduces API calls by 80%
- Configurable batch sizes and thresholds
- Caching prevents duplicate analysis

## 📁 Project Structure

```
arxiv-research-agent/
├── src/
│   ├── research_agent.py      # Main application
│   ├── arxiv_fetcher.py       # arXiv API integration
│   ├── claude_analyzer.py     # Claude Code SDK analysis
│   ├── digest_generator.py    # Multi-format output generation
│   └── config_manager.py      # Configuration management
├── config/
│   └── config.yaml           # Main configuration file
├── output/                   # Generated digests
├── logs/                     # Application logs
├── requirements.txt          # Python dependencies
├── setup.py                  # Setup script
└── README.md                # This file
```

## ⚙️ Configuration Options

### Research Configuration
```yaml
research:
  interests: ["AI topics you care about"]
  arxiv_categories: ["cs.AI", "cs.LG", "cs.CL"]
  filters:
    max_papers_per_day: 50
    min_significance_score: 0.4
```

### Scheduling
```yaml
schedule:
  daily_digest:
    enabled: true
    time: "09:00"
  weekly_summary:
    enabled: true
    day: "Monday"
    time: "08:00"
```

### Output Formats
```yaml
output:
  formats:
    html: true        # Rich interactive digests
    markdown: true    # Documentation-friendly
    json: true        # Programmatic access
    email: true       # Newsletter format
```

### Notifications
```yaml
notifications:
  email:
    enabled: true
    recipients: ["your-email@example.com"]
  discord:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/..."
```

## 🔧 Advanced Features

### Custom Analysis Prompts
Modify `claude_analyzer.py` to customize how papers are analyzed:
```python
# Add custom analysis criteria
analysis_prompt_template = """
Analyze this paper focusing on:
1. Commercial viability
2. Technical feasibility
3. Competitive advantages
...
"""
```

### Research Interest Learning
The agent can learn from your feedback over time:
```yaml
features:
  learning:
    enabled: true
    feedback_file: "feedback.json"
```

### Trend Analysis
Weekly summaries include trend identification:
- Emerging research directions
- Cross-paper connections
- Paradigm shifts and breakthroughs

## 📊 Sample Output

### Daily Digest Email
```
📚 AI Research Digest - June 20, 2025

🔥 5 high-significance papers found

🔥 1. "Revolutionary Reasoning in LLMs: A New Paradigm"
👥 Smith, J. et al.
📊 Significance: 0.95 | Novelty: 0.88

📝 Introduces a novel reasoning architecture that outperforms 
current state-of-the-art by 40% on complex reasoning tasks...

💡 Key insight: This approach could revolutionize how we think 
about AI reasoning capabilities...

🔗 Read more: https://arxiv.org/abs/2025.xxxx
```

### HTML Digest Features
- Beautiful responsive design
- Interactive paper cards
- Filterable by categories and scores
- Direct links to papers and PDFs
- Trend visualization (weekly summaries)

## 🛠️ Development

### Adding New Features
1. Create new modules in `src/`
2. Update configuration in `config/config.yaml`
3. Add tests in `tests/`
4. Update documentation

### Custom Paper Sources
Extend `arxiv_fetcher.py` to include other sources:
- bioRxiv for biology papers
- SSRN for economics/finance
- Custom RSS feeds
- Conference proceedings

### Custom Analysis Models
Replace or supplement Claude with other models:
- Local LLM integration
- Specialized domain models
- Custom scoring algorithms

## 🐛 Troubleshooting

### Common Issues

**API Key Not Working**
- Verify your Anthropic API key is valid
- Check `.env` file formatting
- Ensure sufficient API credits

**No Papers Found**
- Check arXiv categories are correct
- Adjust `min_relevance_score` threshold
- Verify research interests keywords

**Email Not Sending**
- Use app-specific passwords for Gmail
- Check SMTP settings and ports
- Verify firewall/network settings

**High Costs**
- Reduce `max_papers_per_day`
- Increase significance thresholds
- Use batch processing for non-urgent analysis

### Logs and Debugging
```bash
# View agent logs
tail -f logs/agent.log

# Check error logs
tail -f logs/errors.log

# Debug mode
ARXIV_AGENT_LOG_LEVEL=DEBUG python src/research_agent.py --once
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Related Projects

- [Claude Code SDK Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [arXiv API Documentation](https://arxiv.org/help/api)
- [Research Paper Management Tools](https://github.com/topics/research-papers)

## 💡 Use Cases

### Academic Researchers
- Stay current with latest developments
- Identify collaboration opportunities
- Track citation trends
- Monitor competing research

### Industry R&D Teams
- Competitive intelligence
- Technology scouting
- Investment decision support
- Patent landscape analysis

### AI Practitioners
- Learn about new techniques
- Understand implementation challenges
- Track benchmark improvements
- Discover practical applications

---

**Built with ❤️ using Claude Code SDK**

*Empowering researchers to stay ahead of the curve in AI development.*