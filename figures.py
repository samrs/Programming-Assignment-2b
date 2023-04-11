import matplotlib.pyplot as plt


def plot_figures():
    n_values = [4, 8, 12, 16, 24]
    times_taken = [2, 6, 4, 7, 2]
    plt.plot(n_values, times_taken)
    plt.title("Window size (N) vs. time taken to complete file transfer")
    plt.xlabel("Window size (N)")
    plt.ylabel("Time taken (seconds)")
    plt.savefig("plot_a.png")
    plt.close()
    retransmission_values = [8, 43, 19, 42, 7]
    plt.plot(n_values, retransmission_values)
    plt.title("Window size(N) vs. # of retransmissions")
    plt.xlabel("Window size (N)")
    plt.ylabel("# of retransmissions")
    plt.savefig("plot_b.png")
    plt.close()
    timeout_values = [2, 6, 4, 7, 2]
    plt.plot(n_values, timeout_values)
    plt.title("Window size(N) vs. # of timeout")
    plt.xlabel("Window size (N)")
    plt.ylabel("# of timeout")
    plt.savefig("plot_c.png")
    plt.close()


if __name__ == "__main__":
    try:
        plot_figures()
    except KeyboardInterrupt:
        print("Shutting down")
