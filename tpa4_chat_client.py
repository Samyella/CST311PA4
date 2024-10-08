import socket as s
import threading
import logging

# Configure logging
logging.basicConfig(format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Global variables for the server address and port
server_name = '10.0.2.2'  # Updated to h4's IP
server_port = 12001

# Function to handle sending messages
def send_messages(client_socket):
    while True:
        user_input = input()  # Get user input
        if user_input.lower() == "bye":
            # Notify server that the client is leaving
            client_socket.send(user_input.encode())
            log.info("You have left the chat.")
            break  # Exit the loop to close the connection
        else:
            try:
                client_socket.send(user_input.encode())
            except Exception as e:
                log.error(f"Error sending message: {e}")
                break  # Exit on error

    client_socket.close()  # Close the socket after "bye" is sent

# Function to handle receiving messages
def receive_messages(client_socket):
    while True:
        try:
            # Receive and decode the message
            server_response = client_socket.recv(1024).decode()
            if not server_response:
                log.info("Server connection closed.")
                break
            log.info(server_response)  # Print received message
        except Exception as e:
            log.error("Error receiving message: %s", str(e))
            break

    client_socket.close()  # Close the socket on error or server disconnection

# Main function to run the client
def main():
    # Create a TCP socket
    client_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
    
    try:
        # Connect to the server
        client_socket.connect((server_name, server_port))
        log.info("Connected to the chat server.")
        
        # Start threads for sending and receiving messages
        send_thread = threading.Thread(target=send_messages, args=(client_socket,))
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        
        # Start both threads
        send_thread.start()
        receive_thread.start()
        
        # Wait for both threads to complete
        send_thread.join()
        receive_thread.join()

    except Exception as e:
        log.error("Error: %s", str(e))
        log.error("Unable to connect to server. Please ensure the server is running.")
    finally:
        client_socket.close()

# Entry point for the script
if __name__ == "__main__":
    main()
