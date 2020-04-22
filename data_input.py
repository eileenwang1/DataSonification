# read from file
# get pattern
# get a list of data objects
# return as an array of data groups


class ReadData:

    def __init__(self,file_name):
        self.data_input = self.read_file(file_name)

    def read_file(self,file_name):
        to_return = []
        f = open(file_name, "r")
        counter = 0
        while True:
            line = f.readline()
            counter += 1
            if counter == 1:
                pass
            else:
                if len(line) == 0:
                    break
                else:
                    line = line.strip()
                    l_line = line.split(",")
                    data = Data(idx=int(l_line[0]), num_chucks=int(float(l_line[1])), location=l_line[2],
                                days_to_ddl=int(l_line[3]),buddies=int(l_line[4]), music=l_line[5],
                                feeling_before=int(l_line[6]), feeling_after=int(l_line[7]))
                    to_return.append(data)
        f.close()
        return to_return


class Data:
    # idx,units (of half hours),Location,CSO Deadline,Study Buddies,Listening to Music,Feeling (1-10) Before,Feeling (1-10) After
    def __init__(self,idx,num_chucks,location,days_to_ddl,buddies,music,feeling_before, feeling_after):
        self.idx = idx
        self.duration = num_chucks * 3  # number of units
        self.location = location
        self.bpm = self.get_bpm(days_to_ddl)
        self.bass_velocity = self.get_velocity(days_to_ddl)
        self.buddies = buddies
        self.music = True if music == "Y" else False
        self.feeling_before = feeling_before
        self.feeling_after = feeling_after

    def get_bpm(self,days_to_ddl):
        upper = 180
        band = 120
        return int(upper-days_to_ddl*(band/8))

    def get_velocity(self,days_to_ddl):
        # range 60-100
        upper = 100
        band = 60
        return int(upper-days_to_ddl*(band/8))
