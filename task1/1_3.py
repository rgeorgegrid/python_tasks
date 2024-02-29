import sys
from collections import defaultdict

def read_access_log(file_path):
    user_agents = defaultdict(int)
    total_requests = 0

    try:
        with open(file_path, 'r') as file:
            for line in file:
                total_requests += 1
                parts = line.split('"')
                if len(parts) >= 6:
                    user_agent = parts[5].strip()
                    user_agents[user_agent] += 1
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None

    return user_agents, total_requests

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <access_log_file>")
        return

    file_path = sys.argv[1]
    user_agents, total_requests = read_access_log(file_path)

    if user_agents is not None:
        print(f"Total number of different User Agents: {len(user_agents)}")
        print("User Agent statistics:")
        for agent, count in user_agents.items():
            print(f"{agent}: {count} requests")

        print(f"Total number of requests: {total_requests}")

if __name__ == "__main__":
    main()
