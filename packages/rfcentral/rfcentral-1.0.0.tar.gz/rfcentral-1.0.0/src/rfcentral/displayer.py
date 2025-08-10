from datetime import datetime

class ConsoleOutput():

    def __init__(self, power:float):
        self.power = power
        print(f'Frequency(Mhz)\t Power(dBm)\t time\t')

    def display(self, frequency:str, power:str, date_time:str): # FIXME make it tabular later
        if float(power) >= self.power:
            print('\a')
            print('\a')
            print('\a')
            print(f'\033[91m{frequency}\t\t {power}\t\t {date_time}\t\t \033[0m')
        else:
            print(f'\033[92m{frequency}\t\t {power}\t\t {date_time}\t\t \033[0m')

        print("\n")




if __name__ == "__main__":
    console = ConsoleOutput(60.00)
    console.display('105.55',"69")