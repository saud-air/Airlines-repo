import sys


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python delete_cluster.py <cluster_name>")
        sys.exit(1)

    cluster_name = sys.argv[1]
    print(f"Deleting cluster: {cluster_name}")


if __name__ == "__main__":
    main()
