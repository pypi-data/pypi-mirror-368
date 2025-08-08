# 🚀 Moja - ClickHouse AI Agent

A beautiful, intelligent CLI agent for ClickHouse database analysis and operations.

## ✨ Features

- 🤖 **AI-Powered**: Intelligent natural language interface for ClickHouse operations
- 📊 **Data Analysis**: Comprehensive table analysis with statistics and insights
- 📈 **Visualizations**: Create beautiful charts and graphs from query results
- 📥 **Data Loading**: Load CSV, JSON files into ClickHouse with auto-schema detection
- 📤 **Data Export**: Export query results to various formats (CSV, JSON, Parquet, Excel)
- 🔧 **Database Management**: Table optimization, system information, and more
- 🎨 **Beautiful CLI**: Rich, colorful interface with progress bars and tables

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/vish/moja.git
cd moja

# Install dependencies
pip install -r requirements.txt

# Set up your configuration
export OPENROUTER_API_KEY="your-api-key"
export CLICKHOUSE_HOST="localhost"
export CLICKHOUSE_PORT="8123"
```

## 🚀 Quick Start

### Interactive Chat Mode
```bash
python main.py chat
```

### Execute Single Query
```bash
python main.py query "SELECT * FROM my_table LIMIT 10"
```

### Analyze Table
```bash
python main.py analyze my_table --deep
```

### Load Data
```bash
python main.py load-data data.csv my_table
```

## 🔧 Configuration

Create a `.env` file or use environment variables:

```bash
# ClickHouse Configuration
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USERNAME=default
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DATABASE=default

# OpenRouter Configuration
OPENROUTER_API_KEY=your-api-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini
```

## 🤖 AI Capabilities

Moja understands natural language commands like:

- "Show me all tables in the database"
- "Analyze the user_events table and find patterns"
- "Create a bar chart showing sales by month"
- "Load the CSV file into a new table"
- "Export the query results to Excel"

## 🏗️ Architecture

Built with modern Python tools:
- **Typer**: Beautiful CLI interface
- **Rich**: Colorful terminal output
- **ClickHouse Connect**: Fast database connectivity
- **OpenRouter**: AI model access
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation

## 📖 Examples

### Data Analysis
```python
# Interactive session
python main.py chat

> "Analyze my sales_data table and show me the top products"
> "Create a line chart showing revenue trends over time"
> "Find any anomalies in the user behavior data"
```

### Batch Operations
```bash
# Load multiple files
python main.py load-data sales_2023.csv sales_data
python main.py load-data users.json user_profiles

# Analyze and export
python main.py analyze sales_data --deep
python main.py query "SELECT * FROM sales_data WHERE revenue > 1000" --format csv --save results.csv
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details.

---

Built with ❤️ for the ClickHouse community