
import datetime
import time
import os

def main():
    print("Python Date & Time Application")
    print("==============================")
    
    # Print current date and time when the container starts
    current_time = datetime.datetime.now()
    print(f"Container started at: {current_time}")
    
    # Keep running and printing the time every 5 seconds
    while True:
        now = datetime.datetime.now()
        print(f"Current date and time: {now}")
        print(f"UTC time: {datetime.datetime.utcnow()}")
        print(f"Timestamp: {int(time.time())}")
        print("-------------------------------")
        
        # Sleep for 5 seconds
        time.sleep(5)

if __name__ == "__main__":
    # Check if running in container
    print(f"Running in container: {os.environ.get('HOSTNAME', 'Unknown')}")
    main()