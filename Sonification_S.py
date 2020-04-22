from data_input import ReadData
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo
from midi_group import MidiGroup, MidiNote
import random
# Sonification of Sofija's dataset


class Sonification_S:

    def __init__(self,file_name):
        self.data = ReadData(file_name).data_input
        self.pattern_mapping = {"U": "wanderer.mid", "L": "BACH.mid", "D": "come_write_a_fugue.mid",
                                "E": "alberti_bass.mid"}    # do pattern mapping at data processing
        self.pattern = self.get_pattern()
        self.output = []    # an array of output groups
        self.result = self.data_processor()
        self.final_call = self.midi_out()

    def get_pattern(self):
        d_pattern = {}
        for k,v in self.pattern_mapping.items():
            pattern = self.helper_get_pattern(v)
            d_pattern[k] = pattern
        return d_pattern

    def helper_get_pattern(self,pattern_name):
        mid = MidiFile(pattern_name)
        pattern = MidiGroup(pattern=True)
        if pattern_name is not "BACH.mid":
            pattern.triad = True

        prev_velocity = 0
        for i, track in enumerate(mid.tracks):  # i is the name of the track
            for msg in track:
                if msg.type is "note_on":
                    if msg.velocity > 0:
                        midi_note = MidiNote(note=msg.note, velocity=msg.velocity, note_on_time=msg.time)
                        if msg.velocity > prev_velocity:
                            midi_note.accent = True
                        pattern.midi_notes.append(midi_note)
                    else:
                        midi_note = pattern.midi_notes[-1]
                        if midi_note.note == msg.note:
                            midi_note.note_off_time = msg.time
                        else:
                            raise Exception("error in get_pattern: note_off without note_on")
        # pattern.triad_pattern = pattern.get_triad_pattern()
        triad_pattern = pattern.get_triad_pattern()

        pattern.get_grouping()
        return pattern

    def data_processor(self):

        for i in self.data:
            self.processor_within_group(i)
        return self.output

    def processor_within_group(self,data):
        # within one data entry
        pattern = self.pattern[data.location]
        midi_tempo = bpm2tempo(data.bpm)
        output_group = MidiGroup(tempo=midi_tempo, grouping=pattern.grouping,buddies=data.buddies,
                                 triad=pattern.triad,triad_pattern=pattern.triad_pattern)
        duration = data.duration
        chunk = (data.feeling_after - data.feeling_before) /duration
        last_bass = None
        for i in range(duration):
            # update threshold
            prev_threshold = int(data.feeling_before + i*chunk)
            threshold = (10-prev_threshold)/10
            # random walk for now
            if len(output_group.midi_notes) == 0:
                bass_note = random.choice(range(45,70))
                last_bass = bass_note
            else:
                bass_note = self.random_walk(last_bass)
                last_bass = bass_note
            self.within_unit(bass_note, pattern, threshold, output_group,data)
        self.output.append(output_group)

    def within_unit(self,bass_note, pattern,threshold,output_group,data):
        # output within one unit
        if not pattern.triad:
            prev_note = None
            for i in range(len(pattern.midi_notes)):
                velocity = data.bass_velocity + (15 if pattern.midi_notes[i].accent else 0)
                if i == 0:
                    new_midi_note = MidiNote(note=bass_note,velocity=velocity,
                                             note_on_time=pattern.midi_notes[i].note_on_time, note_off_time=pattern.midi_notes[i].note_off_time)
                    output_group.midi_notes.append(new_midi_note)
                    prev_note = bass_note
                else:
                    interval = pattern.midi_notes[i-1].note - pattern.midi_notes[i].note
                    curr_note = prev_note + interval
                    new_midi_note = MidiNote(note=curr_note, velocity=velocity,
                                             note_on_time=pattern.midi_notes[i].note_on_time,
                                             note_off_time=pattern.midi_notes[i].note_off_time)
                    output_group.midi_notes.append(new_midi_note)
                    prev_note = curr_note

        else:
            triad_pattern = output_group.triad_pattern
            triad = self.helper_choose_triad(threshold)
            try:
                for i in range(len(triad_pattern)):
                    velocity = data.bass_velocity + (15 if pattern.midi_notes[i].accent else 0)
                    curr_note = bass_note + triad[triad_pattern[i]]
                    new_midi_note = MidiNote(note=curr_note, velocity=velocity,
                                             note_on_time=pattern.midi_notes[i].note_on_time,
                                             note_off_time=pattern.midi_notes[i].note_off_time)
                    output_group.midi_notes.append(new_midi_note)
            except TypeError:
                print("type error at line 125")

    def helper_choose_triad(self,threshold):
        major = [0, 4, 7]
        minor = [0, 3, 7]
        diminished = [0, 3, 6]
        argumented = [0, 4, 8]
        random_num1 = random.random()
        if random_num1 > threshold:
            # mood 10/10
            prob_array = [(0, 0), (major, 0.65), (minor, 1)]  # interval in terms of the major scale
            random_num2 = random.random()
            for i in range(1, len(prob_array)):
                if (prob_array[i - 1][1] < random_num2) and random_num2 <= prob_array[i][1]:
                    triad = prob_array[i][0]
        else:
            # mood 1/10
            prob_array = [(0, 0), (major, 0.2), (minor, 0.6),(diminished,0.8),(argumented,1)]  # interval in terms of the major scale
            random_num2 = random.random()
            for i in range(1, len(prob_array)):
                if (prob_array[i - 1][1] < random_num2) and random_num2 <= prob_array[i][1]:
                    triad = prob_array[i][0]
        return triad    # return type is a list

    def random_walk(self,prev_note, step_range=5):

        step = (random.randint(0,step_range)) * (random.choice([1,-1]))
        curr_note = prev_note + step
        return curr_note

    def midi_out(self):
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)
        # do you change the program?
        track.append(Message('program_change', program=1, time=0))
        for i in self.result:
            # set tempo at each unit
            track.append(MetaMessage("set_tempo", tempo=i.tempo))
            counter = 0
            grouping = i.grouping
            chord_pattern = i.triad_pattern

            # for j in range(len(i.midi_notes)):
            while counter < len(i.midi_notes):
                inverted_sequence = []  # an array of inverted sequence (2D array)
                # interate in terms of units
                unit = i.midi_notes[counter:counter + grouping]
                if i.buddies > 0:
                    if i.triad:
                        # print("number of buddies", i.buddies)
                        sequence_to_invert = [a.note for a in unit]      # get sequence to invert
                        for b in range(i.buddies):
                            # print("b is",b)
                            inverted_sequence.append(self.inversion(sequence_to_invert=sequence_to_invert,
                                                                    chord_pattern=chord_pattern,order=b+1))
                    else:
                        pass
                # send midi note out
                if len(inverted_sequence) > 0:
                    # print("length of inverted sequence", len(inverted_sequence),inverted_sequence)
                    for j in range(len(unit)):
                        channel =unit[j].channel
                        # note on message
                        track.append(Message('note_on', note=unit[j].note, velocity=unit[j].velocity,
                                         time=int(unit[j].note_on_time * 0.75),channel=unit[j].channel))
                        for k in range(len(inverted_sequence)):
                            time = 0
                            # iterate through every element in a=inverted_sequence
                            track.append(Message('note_on', note=int(inverted_sequence[k][j]), velocity=unit[j].velocity-10,
                                                 time=time,channel=channel))

                        # note off message
                        track.append(Message('note_off', note=unit[j].note, velocity=unit[j].velocity,
                                             time=int(unit[j].note_off_time * 0.75), channel=unit[j].channel))
                        for k in range(len(inverted_sequence)):
                            # time = int(unit[j].note_off_time * 0.75) if k == len(inverted_sequence) - 1 else 0
                            time = 0
                            # iterate through every element in a=inverted_sequence
                            track.append(Message('note_off', note=int(inverted_sequence[k][j]),
                                                 velocity=unit[j].velocity-10, time=time, channel=channel))

                else:
                    # when no inverted sequence
                    for j in range(len(unit)):
                        track.append(Message('note_on', note=unit[j].note, velocity=unit[j].velocity,
                                             time=int(unit[j].note_on_time * 0.75),
                                             channel=unit[j].channel))
                        track.append(Message('note_off', note=unit[j].note, velocity=unit[j].velocity,
                                             time=int(unit[j].note_off_time * 0.75),
                                             channel=unit[j].channel))
                counter += grouping

            track.append(Message('note_on', note=1, velocity=0, time=240, channel=channel))
            track.append(Message('note_off', note=1, velocity=0, time=240, channel=channel))

        mid.save('Sonification_output.mid')
        print("midi file ready")

    def inversion(self,sequence_to_invert,chord_pattern, order):    #order = 1, first inversion
        # mapping chord degree to midi note
        d = {}
        inverted_sequence = []
        if len(sequence_to_invert) != len(chord_pattern):
            print("sequence_to_invert",sequence_to_invert)
            print("chord_pattern",chord_pattern)
            raise Exception("Invalid input for chord inversion")
        for i in range(len(sequence_to_invert)):
            # if d.get(d[chord_pattern[i]]) is None:
            if d.get(chord_pattern[i]) is None:
                d[chord_pattern[i]] = sequence_to_invert[i]
        # inverted_chord pattern
        inverted_chord_pattern = [i+order for i in chord_pattern]
        for i in inverted_chord_pattern:
            # if > 3:
            key = int(i % 3)
            octave = i // 3
            inverted_midi = int(d[key] + octave*12)
            inverted_sequence.append(inverted_midi)

        return inverted_sequence
        # only a sequence of midi note value

    # todo:humanize

test = Sonification_S("data_input.csv")

