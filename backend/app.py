from flask import Flask, request, jsonify
import librosa, os, tempfile
from mutagen import File as AudioFile

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze_song():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    tmp = tempfile.NamedTemporaryFile(delete=False)
    file.save(tmp.name)

    try:
        
        audio_meta = AudioFile(tmp.name)
        bitrate = getattr(audio_meta.info, "bitrate", None)
        if bitrate:
            bitrate = bitrate / 1000

       
        y, sr = librosa.load(tmp.name)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        energy = float(sum(abs(y)) / len(y))
        spectral_centroid = float(librosa.feature.spectral_centroid(y=y, sr=sr).mean())

        os.unlink(tmp.name)

        return jsonify({
            "bitrate_kbps": bitrate,
            "tempo_bpm": tempo,
            "energy": energy,
            "spectral_centroid": spectral_centroid
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
