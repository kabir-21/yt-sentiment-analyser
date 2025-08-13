# YouTube Channel Sentiment Analyzer

A web application that analyzes the sentiment of YouTube video titles using advanced AI models. The app collects recent video titles from a specified YouTube channel and performs detailed sentiment analysis using ChatGPT or Gemini models.

## Features

- **YouTube Channel Input**: Accept channel names, URLs, or @usernames
- **Flexible Video Count**: Analyze 1-50 recent videos from any channel
- **Multiple AI Models**: Support for ChatGPT (OpenAI) and Gemini (Google)
- **Gemini Model Selection**: Choose from Gemini 2.5 Pro, Flash, or Flash Lite
- **User-Friendly API Key Input**: Enter API keys directly in the web interface
- **Flexible Input Methods**: Analyze YouTube channels or upload CSV files with video titles
- **Comprehensive Analysis**: 7-dimensional sentiment analysis including:
  - Overall sentiment (positive/negative/neutral)
  - Emotional arousal and valence
  - News framing perspective
  - Ideology score (-2 to +2)
  - Key topics and entities
  - Language mix detection
  - Agency subject identification
- **Beautiful UI**: Modern, responsive web interface
- **CSV Export**: Download analysis results as a structured CSV file
- **Real-time Statistics**: Visual summary of analysis results

## Prerequisites

Before running this application, you'll need:

1. **Python 3.8+** installed on your system
2. **YouTube Data API v3 Key** from Google Cloud Console
3. **OpenAI API Key** (for ChatGPT analysis)
4. **Google AI API Key** (for Gemini analysis)

## Setup Instructions

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd newslab
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get API Keys

#### YouTube Data API v3 Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3
4. Create credentials (API Key)
5. Copy the API key

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key

#### Google AI API Key (for Gemini)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key

### 4. Configure Environment Variables (Optional)

You can optionally create a `.env` file in the project root to set default API keys:

```bash
# Optional: Set default API keys (users can still override in UI)
YOUTUBE_API_KEY=your_youtube_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
```

**Note**: API keys can now be entered directly in the web interface, making this step optional.

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### 1. Access the Web Interface
Open your browser and navigate to `http://localhost:5000`

### 2. Choose Input Method and Configure Analysis

#### Option A: YouTube Channel Analysis
- **Input Method**: Select "YouTube Channel"
- **Channel Input**: Enter a YouTube channel name, URL, or @username
  - Examples: `PewDiePie`, `https://youtube.com/@PewDiePie`, `@PewDiePie`
- **Number of Videos**: Choose how many recent videos to analyze (1-50)
- **AI Model**: Select between ChatGPT or Gemini
- **Gemini Model** (if selected): Choose from Gemini 2.5 Pro, Flash, or Flash Lite
- **YouTube Data API Key**: Enter your YouTube Data API v3 key
- **AI Model API Key**: Enter your OpenAI or Google AI API key

#### Option B: CSV File Upload
- **Input Method**: Select "Upload CSV File"
- **CSV File**: Upload a CSV file containing video titles
  - CSV should have a column named "video_title" or "title"
- **AI Model**: Select between ChatGPT or Gemini
- **Gemini Model** (if selected): Choose from Gemini 2.5 Pro, Flash, or Flash Lite
- **AI Model API Key**: Enter your OpenAI or Google AI API key

### 3. Start Analysis
Click "Start Analysis" and wait for the results. The process may take a few minutes depending on the number of videos.

### 4. View Results
- **Statistics Cards**: Overview of analysis results
- **Detailed Table**: Complete analysis for each video title
- **CSV Download**: Export results with filename format: `<channel_name>_sentiment_analysis_<LLM_model>.csv`

## Analysis Framework

The application uses a sophisticated 7-dimensional analysis framework:

### 1. Sentiment
- **Positive**: Approval, optimism, favorable outcomes
- **Neutral**: Objective facts, no emotional bias
- **Negative**: Disapproval, pessimism, unfavorable outcomes

### 2. Emotion
- **High Arousal Positive**: Joy, excitement, triumph
- **High Arousal Negative**: Anger, frustration, fear, outrage
- **Low Arousal Positive**: Calm, hope, relief, satisfaction
- **Low Arousal Negative**: Sadness, disappointment, concern
- **Mixed**: Conflicting emotional signals
- **Other**: Doesn't fit other categories

### 3. Frame
- **Conflict**: Disputes, disagreements, confrontations
- **Human Interest**: Individual stories, personal experiences
- **Responsibility**: Blame attribution, accountability
- **Morality**: Ethical considerations, values
- **Economic**: Financial implications, costs, benefits
- **Strategy**: Political maneuvering, tactics, campaigns
- **Justice/Rights**: Fairness, legal rights, advocacy
- **Other**: Doesn't fit other categories

### 4. Ideology Score (-2 to +2)
- **-2**: Strongly anti-government/pro-opposition
- **-1**: Mildly anti-government/pro-opposition
- **0**: Neutral, balanced reporting
- **+1**: Mildly pro-government
- **+2**: Strongly pro-government

### 5. Topics
Up to 3 key topics, named entities, or organizations mentioned

### 6. Language Mix
- **Hindi**: Primarily Hindi content
- **English**: Primarily English content
- **Hinglish**: Mix of Hindi and English
- **Other**: Other languages or mixes

### 7. Agency Subject
The main actor or entity driving the action (max 3 words)

## CSV Output Format

The exported CSV file contains 8 columns:
1. **Video Title**: Original video title
2. **Sentiment**: Overall sentiment classification
3. **Emotion**: Emotional arousal and valence
4. **Frame**: News framing perspective
5. **Ideology Score**: Political leaning score
6. **Topics**: Key topics and entities
7. **Language Mix**: Primary language used
8. **Agency Subject**: Main actor/entity

## API Endpoints

### POST /analyze
Analyze YouTube channel video titles

**Request Body:**
```json
{
  "input_method": "channel",
  "channel_input": "channel_name_or_url",
  "num_videos": 10,
  "llm_type": "chatgpt",
  "gemini_model": "gemini-2.5-flash",
  "youtube_api_key": "your_youtube_api_key",
  "llm_api_key": "your_llm_api_key"
}
```

**Response:**
```json
{
  "success": true,
  "results": [...],
  "total_analyzed": 10
}
```

### POST /analyze_csv
Analyze video titles from uploaded CSV file

**Request Body:** FormData with:
- `csv_file`: CSV file containing video titles
- `llm_type`: "chatgpt" or "gemini"
- `gemini_model`: Gemini model name (if using Gemini)
- `llm_api_key`: API key for the selected LLM

### POST /download_csv
Download analysis results as CSV

**Request Body:**
```json
{
  "results": [...],
  "channel_name": "channel_name",
  "llm_model": "model_name"
}
```

## Error Handling

The application includes comprehensive error handling for:
- Invalid YouTube channel inputs
- API key authentication failures
- Network connectivity issues
- Rate limiting
- Invalid video count requests

## Security Considerations

- API keys are transmitted securely over HTTPS
- No API keys are stored permanently
- Input validation prevents injection attacks
- Rate limiting prevents abuse

## Troubleshooting

### Common Issues

1. **"Could not find channel"**
   - Verify the channel name or URL is correct
   - Ensure the YouTube API key is valid
   - Check if the channel is public

2. **"Could not retrieve video titles"**
   - Channel may be private or have no videos
   - YouTube API quota may be exceeded
   - Network connectivity issues

3. **"Error analyzing sentiment"**
   - Verify the LLM API key is correct
   - Check API key permissions and quotas
   - Ensure the selected model is available

4. **Slow performance**
   - Reduce the number of videos to analyze
   - Check network connectivity
   - Verify API response times

### API Quotas

- **YouTube Data API**: 10,000 units per day (free tier)
- **OpenAI API**: Varies by plan
- **Google AI API**: Varies by plan

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation
3. Open an issue on GitHub

## Changelog

### Version 1.0.0
- Initial release
- Support for ChatGPT and Gemini models
- 7-dimensional sentiment analysis
- CSV export functionality
- Modern web interface
