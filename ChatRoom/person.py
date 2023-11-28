class Person:
    def __init__(self, name, ip, connected_time):
        self.name = name
        self.ip = ip
        self.connected_time = connected_time
    
    def __str__(self):
        return f"User {self.name} connected to server at {self.connected_time} with IP: {self.ip}"
    

        