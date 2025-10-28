# ប្រើ Python 3.10
FROM python:3.10-slim

# ដំឡើង ffmpeg ដែល yt-dlp ត្រូវការ
RUN apt-get update && apt-get install -y ffmpeg

# កំណត់ទីតាំងធ្វើការ
WORKDIR /app

# Copy requirements file ហើយដំឡើង packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy កូដទាំងអស់ចូលទៅក្នុង
COPY . .

# បញ្ជាឱ្យដំណើរការ Bot (ខ្ញុំបានប្តូរឈ្មោះ File ឱ្យត្រូវនឹងរបស់អ្នក)
CMD ["python", "tiktok_bot.py"]