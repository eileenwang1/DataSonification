class MidiGroup:
    def __init__(self, pattern=False, tempo=50000, triad=False, grouping=0,buddies=0,triad_pattern=None):
        self.tempo = tempo    # store tempo (in terms of midi)
        self.midi_notes = [] # an array of note objects
        self.triad = triad  # true for pattern alberti_bass and pattern fugue
        self.grouping = grouping    # int
        self.buddies = buddies
        self.pattern = pattern
        self.triad_pattern = triad_pattern

    def __sizeof__(self):
        return len(self.midi_notes)

    def get_grouping(self):
        if self.pattern:
            self.grouping = len(self.midi_notes)
        return self.grouping

    def get_triad_pattern(self):
        if self.pattern:
            triad_pattern = [0]
            root = self.midi_notes[0].note

            for i in range(1, len(self.midi_notes)):
                diff = self.midi_notes[i].note - root
                diff = int(diff % 12)
                octave = int(diff//12)
                if diff == 0:
                    triad_pattern.append(0+octave*3)
                elif abs(diff - 4) < abs(diff - 7):

                    # third
                    triad_pattern.append(1+octave*3)
                else:
                    # fifth
                    triad_pattern.append(2+octave*3)
            self.triad_pattern=triad_pattern

        return self.triad_pattern


class MidiNote:
    def __init__(self, note=0, velocity=0, channel=1, note_on_time=0, note_off_time=0, accent=False):
        self.note = note
        self.velocity = velocity
        self.channel = channel
        self.note_on_time = note_on_time
        self.note_off_time = note_off_time
        self.accent = accent    # the louder note
        # get pattern: only about time, not about relative

    def __str__(self):
        return "note: {},\t velocity:{},\t note_on_time:{},\tnote_off_time:{}\t".format\
            (self.note, self.velocity, self.note_on_time, self.note_off_time)
