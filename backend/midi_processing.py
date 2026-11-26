import pretty_midi


def extract_midi_notes(midi_path):
    """
    Extract note information from a MIDI file.

    Returns a list of dictionaries containing:
    - pitch: MIDI note number
    - start: note start time in seconds
    - end: note end time in seconds
    - instrument: instrument index
    """
    midi_data = pretty_midi.PrettyMIDI(str(midi_path))
    notes = []

    for instrument_index, instrument in enumerate(midi_data.instruments):
        if instrument.is_drum:
            continue

        for note in instrument.notes:
            notes.append({
                "pitch": note.pitch,
                "start": note.start,
                "end": note.end,
                "instrument": instrument_index
            })

    notes.sort(key=lambda note: (note["start"], note["pitch"]))

    return notes


def group_notes_by_time(notes, tolerance=0.05):
    """
    Group notes that start within a small time tolerance.

    Returns groups containing pitches and timing information.
    This is intended for simple, block-chord MIDI files.
    """
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")

    if not notes:
        return []

    sorted_notes = sorted(
        notes,
        key=lambda note: (note["start"], note["pitch"])
    )

    groups = []
    current_group = []
    group_start = None

    for note in sorted_notes:
        if not current_group:
            current_group = [note]
            group_start = note["start"]
        elif note["start"] - group_start <= tolerance:
            current_group.append(note)
        else:
            groups.append({
                "pitches": sorted(set(n["pitch"] for n in current_group)),
                "start": float(min(n["start"] for n in current_group)),
                "end": float(max(n["end"] for n in current_group))
            })

            current_group = [note]
            group_start = note["start"]

    if current_group:
        groups.append({
            "pitches": sorted(set(n["pitch"] for n in current_group)),
            "start": float(min(n["start"] for n in current_group)),
            "end": float(max(n["end"] for n in current_group))
        })

    return groups


def identify_chord(pitches):
    """
    Identify a major or minor triad from MIDI pitches.

    Returns a raw chord label compatible with
    Hanna's chord encoder, or None if unidentified.
    """
    if not pitches:
        return None

    # Convert MIDI pitches to unique pitch classes (0-11).
    pitch_classes = {pitch % 12 for pitch in pitches}

    if len(pitch_classes) != 3:
        return None

    note_names = [
        "C", "C#", "D", "D#", "E", "F",
        "F#", "G", "G#", "A", "A#", "B"
    ]

    for root in range(12):
        major = {
            root,
            (root + 4) % 12,
            (root + 7) % 12
        }

        minor = {
            root,
            (root + 3) % 12,
            (root + 7) % 12
        }

        if pitch_classes == major:
            return note_names[root]

        if pitch_classes == minor:
            return note_names[root] + "min"

    return None


def extract_chord_progression(midi_path, tolerance=0.05):
    """
    Extract a chord progression from a MIDI file.

    Returns raw chord labels compatible with Hanna's
    encoder, along with start/end times.
    """
    notes = extract_midi_notes(midi_path)
    groups = group_notes_by_time(notes, tolerance=tolerance)

    progression = []

    for group in groups:
        chord = identify_chord(group["pitches"])

        # Skip note groups that cannot be identified.
        if chord is None:
            continue

        progression.append({
            "chord": chord,
            "start": group["start"],
            "end": group["end"]
        })

    return progression
