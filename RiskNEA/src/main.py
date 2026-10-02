from managers import LocalPlayManager, TrainingManager, SimulationManager

def main():
    while True:
        inp = input("How would you like to use this program?(PLAY/SIMULATE/TRAIN/EXIT)").lower() 
        if inp == "play":
            LocalPlayManager().play()
        elif inp == "simulate": 
            SimulationManager().simulate()
        elif inp == "train":    
            TrainingManager().learn()
        elif inp == "exit":
            break
        else:
            print("Your input was not recognised!")

if __name__ == "__main__": main()

