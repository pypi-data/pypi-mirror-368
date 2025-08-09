import os
import matplotlib.pyplot as plt
import argparse

def main():
    min_loss = 9999.
    best = ""
    filenames = os.listdir(".")
    filenames = [f for f in filenames if "_loss.txt" in f]
    for filename in filenames:
        losses = np.fromfile(filename, dtype=int, sep='\n')
        meanloss = losses.mean()
        if meanloss < min_loss:
            min_loss = meanloss
            best = filename
    print(f"best: {best} mean loss: {min_loss}")



if __name__ == "__main__":
    main()
