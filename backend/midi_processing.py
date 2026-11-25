import pretty_midi

#im not sure how files will be uploaded, 
#but if google colab is used keep this
#if not delete and change to needed thing
from google.colab import files
upladed = files.upload()

#Grab the filename of the uploaded file
midi_path = list(uploaded.keys())[0]

#load MIDI file into PretyMIDI object
midi_data = pretty_midi.PrettyMIDI(midi_path)

#variables 
chords = []
current_chord = []
sec = 0.05

#parsing through the file
for instrument in midi_data.instruments:
    for note in instrument.notes:
        #check if the note is already in the current chord
        if note.pitch not in current_chord:
            current_chord.append(note.pitch)
        
        #check if the note is still being played
        if note.end > sec:
            sec += 0.05
        else:
            #if the note has ended, add the current chord to the list of chords and reset the current chord
            chords.append(current_chord)
            current_chord = []
            sec += 0.05
        
        #turn notes in chord [] into chord names
        for chord in chords:
            names = [pretty_midi.note_number_to_name(n.pitch) for n in chord]
            
