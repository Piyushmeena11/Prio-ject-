import os
from flask import Flask, request, jsonify, render_template
from yt_dlp import YoutubeDL

app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html')

@app.route('/get_video_info', methods=['POST'])
def get_video_info():
    """
    Extracts direct video URLs from a given YouTube link.
    This endpoint takes a JSON payload with a 'url' key.
    """
    youtube_url = request.json.get('url')
    if not youtube_url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best[ext=mp4]/best' # Prioritize mp4 format
        }
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            
            # Extract relevant information
            formats = info_dict.get('formats', [])
            direct_links = []
            for f in formats:
                # We only want direct HTTP video links
                if f.get('url') and f.get('vcodec') != 'none':
                    direct_links.append({
                        'quality': f.get('format_note', 'N/A'),
                        'url': f.get('url'),
                        'ext': f.get('ext')
                    })

            if not direct_links:
                 return jsonify({'error': 'Could not extract any direct video links.'}), 500

            return jsonify({
                'title': info_dict.get('title', 'N/A'),
                'thumbnail': info_dict.get('thumbnail', 'N/A'),
                'links': direct_links
            })

    except Exception as e:
        # Log the error for debugging
        print(f"Error processing URL: {youtube_url}\n{e}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    # Heroku will use a Gunicorn server; this is for local development
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
