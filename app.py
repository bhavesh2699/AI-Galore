from flask import Flask, render_template, request, redirect
import speech_recognition as sr
import audioread
import numpy as np
import wave
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

@app.route("/", methods=["GET", "POST"])
def index():
    transcript=getstring= ""
    word_count=hours=seconds=mins=0
    wpm=duration=0.0
    
    filler_list=['um', 'uh', 'er', 'ah', 'like', 'okay', 'right',  'you know', 'hello']
    if request.method == "POST":
        print("FORM DATA RECEIVED")

        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]

        with open('audio.wav', 'wb') as audio:
            file.save(audio)
        
        signal_wave = wave.open('audio.wav', 'r')
        sample_rate = 16000
        sig = np.frombuffer(signal_wave.readframes(sample_rate), dtype=np.int16)
        plt.figure(1)
        plot_a = plt.subplot(211)
        plot_a.plot(sig)
        plot_a.set_xlabel('sample rate * time')
        plot_a.set_ylabel('energy')
        plt.savefig('static/images/plot.png', dpi=400)
        
        with audioread.audio_open("audio.wav") as f:
            length_in_secs = int(f.duration)
            hours, mins, seconds = convert(length_in_secs)
            duration = float(mins)+float(seconds/60)
        #print(duration, hours, mins, seconds,length_in_secs)
        
        if file.filename == "":
            return redirect(request.url)
        if file:
            recognizer = sr.Recognizer()
            audioFile = sr.AudioFile("audio.wav")
            with audioFile as source:
                data = recognizer.record(source)
            try:
                transcript = recognizer.recognize_google(data, key = None, language = "en-IN")
            except sr.UnknownValueError:
                return render_template('index.html', transcript="Google Speech Recognition could not understand audio",wpm=wpm,word_count=word_count,hours=hours,mins=mins,seconds=seconds,duration=round(duration,1))
            except sr.RequestError as e:
                return render_template('index.html', transcript="Could not request results from Google Speech Recognition service",wpm=wpm,word_count=word_count,hours=hours,mins=mins,seconds=seconds,duration=round(duration,1))
            barGraph(transcript,filler_list)
            word_count=len(transcript.split())
            wpm=word_count//round(duration,1)
    return render_template('index.html', transcript=transcript,wpm=wpm,word_count=word_count,hours=hours,mins=mins,seconds=seconds,duration=round(duration,1))

def convert(seconds):
    hours = seconds // 3600
    seconds %= 3600
    mins = seconds // 60
    seconds %= 60
    return hours, mins, seconds

def barGraph(para,filler_list):
    fillers = {'um':0, 'uh':0, 'er':0, 'ah':0, 'like':0, 'okay':0, 'right':0,  'you know':0, 'hello':0} 
    r = re.compile('|'.join([r'\b%s\b' % w for w in filler_list]), flags=re.I)
    p=r.findall(para)
    if len(p)==0:
        plot(fillers)
    else:
        for ele in p:
            fillers[ele] = fillers.get(ele) + 1
        plot(fillers)

def plot(fillers):
    print(fillers)
    filler = list(fillers.keys()) 
    values = list(fillers.values()) 
    print(values)
    fig = plt.figure(figsize = (10, 5)) 
    plt.bar(filler, values, color ='maroon',  width = 0.4) 
    plt.xlabel("Filler words") 
    plt.ylabel("words frequency") 
    plt.savefig('static/images/graph.png', dpi=400)


@app.after_request
def add_header(response):
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
