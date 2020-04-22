# DataSonification

This project read a dataset in csv format and outputs music in midi format.

## Files
* data_input.csv: The input dataset. The data here is randomized in order the protect the privacy of the original data. The dataset is a record of working on a particular project over the time span of 3 weeks.
* main.py: the main program. Run this program and you will get a sonification of "data_input.csv".
** data_input.py and midi_group.py: header files that defines dependent classes used in main.py.
* Sonification_output.mid: the sonification of the input dataset in midi format.
* others: the rest are demonstrations of the motives and mapping techniques used in the sonification.

## Data mapping
* location: work location is mapped to a motive, because a location is a setting for work and a motif is a setting for music. A motif is a basic musical unit. The examples for four motives used are at below. ".mid" file can be opened by a midi play (such a GarageBand). ".mscz" displays the score as well as plays the score in sound. ".mscz" can be opened by MuseScore.

	* alberti_bass.mid, alberti_bass.mscz: Alberti-bass is widely used in classical music. An example of the use is Mozart's Piano Sonata No. 16 in C Major, K.545 
	* B-A-C-H.mscz BACH.mid: a motif that form's the family name of Johann Sebastian Bach. It is famously used by Bach and many composers after him.
	* wanderer.mid, wanderer.mscz: from the opening sequence of The Wonderer's Fantasy by Franz Schubert
	* come_write_a_fugue.mid come_write_a_fugue.mscz: from Glenn Gould's song "So you Want to Write a Fugue?"
* days to deadline: velocity and amplitude. The closer to deadline, the faster and louder the music is.
* companion: number of voices using chord inversion. To learn more about chord inversion, see "Example_ChordInversion.mscz".
* mood: harmonic quality. To learn more about chord inversion, see "Example_TriadQuality.mscz".
		
