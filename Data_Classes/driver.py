class Driver:
    def __init__(self, place, name, kart_id):
        self.place = place
        self.name = name
        self.kart_id = kart_id
        self.lap_times = []

    def get_place(self):
        return self.place

    def get_name(self):
        return self.name

    def get_kart_id(self):
        return self.kart_id

    def get_lap_times(self):
        return self.lap_times

    def set_place(self, place):
        self.place = place

    def set_new_kart_id(self, new_id):
        self.kart_id = new_id

    def add_time(self, time):
        self.lap_times.append(time)

    def to_dict(self):
        return {
            'place': self.place,
            'name': self.name,
            'kart_id': self.kart_id,
            'lap_times': self.lap_times
        }

    @classmethod
    def from_dict(cls, data):
        driver = cls(
            place=data['place'],
            name=data['name'],
            kart_id=data['kart_id']
        )
        driver.lap_times = data['lap_times']
        return driver
