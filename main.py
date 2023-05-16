import json, requests
import pyttsx3, pyaudio, vosk

tts = pyttsx3.init('sapi5')

voices = tts.getProperty('voices')
tts.setProperty('voices', 'en')

for voice in voices:
    print(voice.name)
    if voice.name == 'Microsoft Zira Desktop - English (United States)':
        tts.setProperty('voice', voice.id)

model = vosk.Model('model_small_ru')
record = vosk.KaldiRecognizer(model, 16000)
pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16,
                 channels=1,
                 rate=16000,
                 input=True,
                 frames_per_buffer=8000)
stream.start_stream()


def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if record.AcceptWaveform(data) and len(data) > 0:
            answer = json.loads(record.Result())
            if answer['text']:
                yield answer['text']


def speak(say):
    tts.say(say)
    tts.runAndWait()

def speak_key(key):
    if key in jData:
        jKey = jData[key]
        speak(jKey)
    else:
        speak('Error. Create joke first') 

def joke_text():
    jText = ''
    if len(jData)>0:
        if jData['type']=='single':
           jText = jData['joke']
        else:
            jText = jData['setup'] + '\n' + jData['delivery']
    return jText

    
speak('starting')
print('start...')
url = 'https://v2.jokeapi.dev/joke/Any?safe-mode'
jData ={}
for text in listen():
    match text:
        case 'закрыть':
            speak('closing. Good Buy')
            quit()
        case 'создать': #"создать" (генерация новой шутки)
            res = requests.get(url)
            if res:
                jData = res.json()
                speak('Joke created')
            else:
               print('Response Failed')
               speak('Response Failed')
        case 'тип': #"тип" (высказывание или диалог)
            speak_key('type')
        case 'прочесть': #"прочесть"
            jText = joke_text()
            if len(jText)>0:
                speak(jText)
            else:
                speak('Error. Create joke first')   
        case 'категория': #"категория" (сказать категорию)
            speak_key('category')
        case 'сохранить': #"записать" (дописать шутку в конец заранее созданного файла)
            jText = joke_text()
            if len(jText)>0:
                with open('jokes.txt', 'a') as f:
                    f.write('-----------------\n')
                    f.write(jText + '\n')
                speak('Joke saved')  
            else:
                speak('Error. Create joke first')
        case 'забыть': #"забыть" (забыть шутку)
            jData = {}
            speak('Joke clear')
        case _:
            speak('Unknown command')
            print(f'Команда "{text}" не распознана')
        
