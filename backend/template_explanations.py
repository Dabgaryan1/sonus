from music21 import harmony #harmony module contains tools for working with chords and harmonic relationships

#takes a chord name and determines which musical notes make up that chord
def get_chord_notes(chord_name):
    chord = harmony.ChordSymbol(chord_name)
    return [pitch.name for pitch in chord.pitches]


#get shared notes between previous and predicted chords
def get_shared_notes(previousChord, predictedChord):
    previousNotes = set(get_chord_notes(previousChord))
    predictedNotes = set(get_chord_notes(predictedChord))

    return previousNotes.intersection(predictedNotes)


#template based explanations
def generate_template_explanation(previousChord, predictedChord):
    sharedNotes = get_shared_notes(previousChord, predictedChord)
    count = len(sharedNotes)

    #Template 1: previous chord is the same as predicted chord
    if previousChord == predictedChord:
        return (
            f"{predictedChord} repeats the previous chord, "
            "maintaining harmonic continuity."
        )

    notes = ", ".join(sorted(sharedNotes))  #convert collection of notes into readable string

    #Template 2: previous chord and predicted chord share multiple notes
    if count >= 2:
        return (
            f"{predictedChord} shares {count} notes ({notes}) "
            f"with {previousChord}, which can help create a smooth transition."
        )

    #Template 3: previous chord and predicted chord share only 1 note
    elif count == 1:
        return (
            f"{predictedChord} shares the note {notes} "
            f"with {previousChord}, providing a common tone "
            "between the chords."
        )

    #Template 4: previous chord and predicted chord share no notes
    else:
        return (
            f"{predictedChord} shares no notes with {previousChord}, "
            "providing harmonic contrast."
        )