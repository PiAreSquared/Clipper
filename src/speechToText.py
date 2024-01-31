import whisper

model = whisper.load_model("base")
result = model.transcribe("../data/cutclip.mp4")
f = open("../data/cutclip.txt", "a")
f.write(result["text"])
f.close()