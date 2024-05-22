from flask import Flask, request, render_template, send_file, after_this_request
import instaloader
import os
import shutil
import time

app = Flask(__name__)
L = instaloader.Instaloader()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    reel_url = request.form['url']
    try:
        short_code = reel_url.split('/')[4]
        post = instaloader.Post.from_shortcode(L.context, short_code)
        
        # Create a temporary directory to store the downloaded reel
        download_dir = f"reel_{int(time.time())}"
        os.makedirs(download_dir, exist_ok=True)
        
        # Download the reel to the temporary directory
        L.download_post(post, target=download_dir)
        
        # Find the downloaded reel video file
        for file_name in os.listdir(download_dir):
            if file_name.endswith('.mp4'):
                file_path = os.path.join(download_dir, file_name)
                
                @after_this_request
                def cleanup(response):
                    try:
                        shutil.rmtree(download_dir)
                    except Exception as e:
                        print(f"Error cleaning up: {e}")
                    return response
                
                # Send the file and ensure it is closed before cleanup
                response = send_file(file_path, as_attachment=True)
                response.call_on_close(lambda: shutil.rmtree(download_dir))
                return response
        
        return "Failed to find the downloaded reel."
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)
