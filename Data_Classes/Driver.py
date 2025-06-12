class Driver:
    def __init__(self, place, name, kart_id):
        self.place = place
        self.name = name
        self.kart_id = kart_id
        self.lap_time = []
    def get_place(self):
        return self.place
    def get_name(self):
        return self.name
    def get_kart_id(self):
        return self.kart_id
    def get_lap_time(self):
        return self.lap_time
    def set_place(self, place):
        self.place = place
    def set_new_kart_id(self, new_id):
        self.kart_id = new_id
    def add_time(self, time):
        self.lap_time.append(time)