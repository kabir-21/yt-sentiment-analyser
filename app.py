from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import csv
import io
import re
from datetime import datetime
import requests
from googleapiclient.discovery import build
from langchain.llms import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Configuration
YOUTUBE_API_KEY = app.config['YOUTUBE_API_KEY']

def extract_channel_id_with_key(channel_input, api_key):
    """Extract channel ID from various YouTube URL formats or channel name using provided API key"""
    if 'youtube.com/channel/' in channel_input:
        return channel_input.split('youtube.com/channel/')[1].split('/')[0]
    elif 'youtube.com/c/' in channel_input or 'youtube.com/user/' in channel_input:
        # For custom URLs, we'll need to search for the channel
        return None
    elif 'youtube.com/@' in channel_input:
        # Handle @username format
        username = channel_input.split('youtube.com/@')[1].split('/')[0]
        return search_channel_by_username_with_key(username, api_key)
    else:
        # Assume it's a channel name and search for it
        return search_channel_by_name_with_key(channel_input, api_key)

def extract_channel_id(channel_input):
    """Extract channel ID from various YouTube URL formats or channel name"""
    return extract_channel_id_with_key(channel_input, YOUTUBE_API_KEY)

def search_channel_by_username_with_key(username, api_key):
    """Search for channel ID by username using provided API key"""
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.search().list(
            part='snippet',
            q=username,
            type='channel',
            maxResults=1
        )
        response = request.execute()
        if response['items']:
            return response['items'][0]['snippet']['channelId']
    except Exception as e:
        print(f"Error searching for channel: {e}")
    return None

def search_channel_by_name_with_key(channel_name, api_key):
    """Search for channel ID by channel name using provided API key"""
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.search().list(
            part='snippet',
            q=channel_name,
            type='channel',
            maxResults=1
        )
        response = request.execute()
        if response['items']:
            return response['items'][0]['snippet']['channelId']
    except Exception as e:
        print(f"Error searching for channel: {e}")
    return None

def search_channel_by_username(username):
    """Search for channel ID by username"""
    return search_channel_by_username_with_key(username, YOUTUBE_API_KEY)

def search_channel_by_name(channel_name):
    """Search for channel ID by channel name"""
    return search_channel_by_name_with_key(channel_name, YOUTUBE_API_KEY)

def get_video_titles_with_key(channel_id, max_results, api_key):
    """Get recent video titles from a YouTube channel using provided API key"""
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # First, get the channel's uploads playlist
        request = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        )
        response = request.execute()
        
        if not response['items']:
            return []
        
        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get videos from the uploads playlist
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId=uploads_playlist_id,
            maxResults=max_results
        )
        response = request.execute()
        
        video_titles = []
        for item in response['items']:
            title = item['snippet']['title']
            # Clean video titles by removing newlines and extra whitespace
            cleaned_title = re.sub(r'\s+', ' ', title.strip().replace('\n', ' ').replace('\r', ' '))
            video_titles.append(cleaned_title)
        
        return video_titles
    except Exception as e:
        print(f"Error getting video titles: {e}")
        return []

def get_video_titles(channel_id, max_results=10):
    """Get recent video titles from a YouTube channel"""
    return get_video_titles_with_key(channel_id, max_results, YOUTUBE_API_KEY)

def load_prompt():
    """Load the analysis prompt from prompt.txt"""
    try:
        with open('prompt.txt', 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error loading prompt: {e}")
        return ""

def analyze_sentiment_with_llm(video_title, llm_type, api_key, gemini_model="gemini-2.5-flash"):
    """Analyze sentiment using the specified LLM"""
    prompt_template = load_prompt()
    
    print(f"title: {video_title}")
    print(f"model: {gemini_model}")

    try:
        if llm_type == 'chatgpt':
            llm = OpenAI(api_key=api_key, temperature=0)
            prompt = PromptTemplate(
                input_variables=["title"],
                template=prompt_template
            )
            formatted_prompt = prompt.format(title=video_title)
            response = llm.invoke(formatted_prompt)
            print(f"response: {response}")
            
        elif llm_type == 'gemini':
            llm = ChatGoogleGenerativeAI(
                model=gemini_model,
                google_api_key=api_key,
                temperature=0
            )
            prompt = PromptTemplate(
                input_variables=["title"],
                template=prompt_template
            )
            formatted_prompt = prompt.format(title=video_title)
            response = llm.invoke(formatted_prompt)
            print(f"response: {response}")
        else:
            return None
            
        # Extract content from response object
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
            
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return None
            
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        input_method = data.get('input_method', 'channel')
        channel_input = data.get('channel_input', '')
        num_videos = int(data.get('num_videos', app.config['DEFAULT_VIDEOS_COUNT']))
        llm_type = data.get('llm_type')
        gemini_model = data.get('gemini_model', 'gemini-2.5-flash')
        youtube_api_key = data.get('youtube_api_key', '')
        llm_api_key = data.get('llm_api_key')
        
        # Validate inputs
        if input_method == 'channel':
            if not channel_input or not channel_input.strip():
                return jsonify({'error': 'Channel input is required.'}), 400
                
            if not youtube_api_key or not youtube_api_key.strip():
                return jsonify({'error': 'YouTube API key is required.'}), 400
        
        if not llm_api_key or not llm_api_key.strip():
            return jsonify({'error': 'LLM API key is required.'}), 400
            
        if num_videos < 1 or num_videos > app.config['MAX_VIDEOS_PER_ANALYSIS']:
            return jsonify({'error': f'Number of videos must be between 1 and {app.config["MAX_VIDEOS_PER_ANALYSIS"]}.'}), 400
            
        if llm_type not in ['chatgpt', 'gemini']:
            return jsonify({'error': 'Invalid LLM type. Choose from: chatgpt, gemini'}), 400
        
        if input_method == 'channel':
            # Extract channel ID using the provided YouTube API key
            channel_id = extract_channel_id_with_key(channel_input, youtube_api_key)
            if not channel_id:
                return jsonify({'error': 'Could not find channel. Please check the channel name or URL and YouTube API key.'}), 400
            
            # Get video titles using the provided YouTube API key
            video_titles = get_video_titles_with_key(channel_id, num_videos, youtube_api_key)
            if not video_titles:
                return jsonify({'error': 'Could not retrieve video titles. Please check the channel and YouTube API key.'}), 400
            
            channel_name = channel_input.replace(' ', '_').replace('@', '').replace('/', '_').replace(':', '_')
        else:
            return jsonify({'error': 'Invalid input method. Use /analyze_csv for CSV uploads.'}), 400
        
        # Analyze each video title using the provided LLM API key
        results = []
        for title in video_titles:
            analysis = analyze_sentiment_with_llm(title, llm_type, llm_api_key, gemini_model)
            if analysis:
                results.append({
                    'video_title': title,
                    'sentiment': analysis.get('sentiment', ''),
                    'emotion': analysis.get('emotion', ''),
                    'frame': analysis.get('frame', ''),
                    'ideology_score': analysis.get('ideology_score', ''),
                    'topics': ', '.join(analysis.get('topics', [])),
                    'language_mix': analysis.get('language_mix', ''),
                    'agency_subject': analysis.get('agency_subject', '')
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_analyzed': len(results),
            'channel_name': channel_name,
            'llm_model': gemini_model if llm_type == 'gemini' else llm_type
        })
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/analyze_csv', methods=['POST'])
def analyze_csv():
    """Analyze video titles from uploaded CSV file"""
    try:
        if 'csv_file' not in request.files:
            return jsonify({'error': 'No CSV file uploaded.'}), 400
        
        csv_file = request.files['csv_file']
        if csv_file.filename == '':
            return jsonify({'error': 'No CSV file selected.'}), 400
        
        llm_type = request.form.get('llm_type')
        gemini_model = request.form.get('gemini_model', 'gemini-2.5-flash')
        llm_api_key = request.form.get('llm_api_key')
        
        # Validate inputs
        if not llm_api_key or not llm_api_key.strip():
            return jsonify({'error': 'AI Model API key is required.'}), 400
            
        if llm_type not in ['chatgpt', 'gemini']:
            return jsonify({'error': 'Invalid LLM type. Choose from: chatgpt, gemini'}), 400
        
        # Read CSV file
        import pandas as pd
        from io import StringIO
        
        try:
            # Read the CSV content
            csv_content = csv_file.read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_content))
            
            # Find the video title column
            title_column = None
            for col in df.columns:
                if 'title' in col.lower() or 'video' in col.lower():
                    title_column = col
                    break
            
            if title_column is None:
                return jsonify({'error': 'No video title column found. Please ensure your CSV has a column named "video_title" or "title".'}), 400
            
            video_titles = df[title_column].dropna().tolist()
            # Clean video titles by removing newlines and extra whitespace
            video_titles = [re.sub(r'\s+', ' ', title.strip().replace('\n', '').replace('\r', ' ')) for title in video_titles if title]
            print(f"video_titles: {video_titles}")
            if not video_titles:
                return jsonify({'error': 'No video titles found in the CSV file.'}), 400
                
        except Exception as e:
            return jsonify({'error': f'Error reading CSV file: {str(e)}'}), 400
        
        # Analyze each video title
        results = []
        for title in video_titles:
            analysis = analyze_sentiment_with_llm(title, llm_type, llm_api_key, gemini_model)
            if analysis:
                results.append({
                    'video_title': title,
                    'sentiment': analysis.get('sentiment', ''),
                    'emotion': analysis.get('emotion', ''),
                    'frame': analysis.get('frame', ''),
                    'ideology_score': analysis.get('ideology_score', ''),
                    'topics': ', '.join(analysis.get('topics', [])),
                    'language_mix': analysis.get('language_mix', ''),
                    'agency_subject': analysis.get('agency_subject', '')
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_analyzed': len(results),
            'channel_name': csv_file.filename.replace('.csv', ''),
            'llm_model': gemini_model if llm_type == 'gemini' else llm_type
        })
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/download_csv', methods=['POST'])
def download_csv():
    try:
        data = request.get_json()
        results = data.get('results', [])
        channel_name = data.get('channel_name', 'unknown_channel')
        llm_model = data.get('llm_model', 'unknown_model')
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Video Title', 'Sentiment', 'Emotion', 'Frame', 
            'Ideology Score', 'Topics', 'Language Mix', 'Agency Subject'
        ])
        
        # Write data
        for result in results:
            writer.writerow([
                result['video_title'],
                result['sentiment'],
                result['emotion'],
                result['frame'],
                result['ideology_score'],
                result['topics'],
                result['language_mix'],
                result['agency_subject']
            ])
        
        output.seek(0)
        
        # Create response with CSV file
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{channel_name}_sentiment_analysis_{llm_model}.csv'
        )
        
    except Exception as e:
        return jsonify({'error': f'Error generating CSV: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
