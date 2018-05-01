#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <strings.h>

#include "../server/server.h"
#include "client.h"
#include "ui.h"

#define SLEEP_TIME 5
#define FIND_PARENT_TIMEOUT 100

static client_child_t local_connections[MAX_CHILDREN];
static size_t current_number_children;
static uint32_t parent_number;
static pthread_mutex_t ui_lock = PTHREAD_MUTEX_INITIALIZER;
static char* server_address;
static uint16_t port;

void propagate_message(char* username, char* message, size_t originator) {
  for (size_t client = 0; client < current_number_children; client++) {
    if (client != originator) {
      size_t user_length = strlen(username);
      if (write(local_connections[client].prop_socket, &user_length, sizeof(size_t)) == sizeof(size_t)) {

        write(local_connections[client].prop_socket, username, strlen(username));
        
        size_t message_length = strlen(message);
        write(local_connections[client].prop_socket, &message_length, sizeof(size_t));
        write(local_connections[client].prop_socket, message, strlen(message));
      }
    }
  }
}

//listens for input from children (parent is included)
void* listen_to_child(void* args) {
  // Get index of child
  size_t child_index = (size_t) args;

  // Declare username variables
  size_t length_of_username = 0;

  // Declare message variables
  size_t length_of_message = 0;

  bool is_connected = true;
  while (is_connected) {
    if (read(local_connections[child_index].prop_socket, &length_of_username, sizeof(size_t)) != 0) {
      // make username
      char* username = (char*) malloc(sizeof(char) * (length_of_username + 1));
      memset(username, 0, sizeof(char) * (length_of_username + 1));
      read(local_connections[child_index].prop_socket,
           username,
           sizeof(char) * length_of_username);
      
      // make message
      read(local_connections[child_index].prop_socket, &length_of_message, sizeof(size_t));
      char* message = (char*) malloc(sizeof(char) * (length_of_message + 1));
      memset(message, 0, sizeof(char) * (length_of_message + 1));
      read(local_connections[child_index].prop_socket,
           message,
           sizeof(char) * length_of_message);

      // Add message to client ui
      pthread_mutex_lock(&ui_lock);
      ui_add_message(username, message);
      pthread_mutex_unlock(&ui_lock);
     
      // Disseminate message throughout server
      propagate_message(username, message, child_index);
      
      free(username);
      free(message);
    } else if (parent_number == client) {        
      // Reconnect to network since parent disappeared
      (void) connect_to_network(server_address, port);
      break;
    }
  }
  return NULL;
}

//creates the threads to listen to children (parent include)
void generate_connection_entry(int socket, size_t connection_num) {
  local_connections[connection_num].prop_socket = socket;
  pthread_create(&local_connections[connection_num].child_thread, NULL, listen_to_child, (void*) connection_num);
}

//accepts only children
void* accept_connections(void* args) {

  int listen_fd = *((int*) args);

  // Become a server socket
  listen(listen_fd, 2);

  while (true) {
    struct sockaddr_in child_addr;
    socklen_t child_addr_len = sizeof(struct sockaddr_in);
    int child_socket = accept(listen_fd, (struct sockaddr*)&child_addr, &child_addr_len);
    
    char ipstr[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &child_addr.sin_addr, ipstr, INET_ADDRSTRLEN);
    
    generate_connection_entry(child_socket, current_number_children);
    current_number_children++;
  }
  return NULL;
}

void disconnect(char* server_address, uint16_t port) {

  struct hostent* server = gethostbyname(server_address);
  if (server == NULL) {
    fprintf(stderr, "Unable to find host %s\n", server_address);
    return;
  }
  
  int closing_fd = socket(AF_INET, SOCK_STREAM, 0);
  if (closing_fd == -1) {
    perror("closing_fd failed");
    return;
  }
  
  struct sockaddr_in directory_addr = {
    .sin_family = AF_INET,
    .sin_port = htons(port)
  };

  bcopy((char*)server->h_addr_list[0], (char*)&directory_addr.sin_addr.s_addr, server->h_length);
  if (connect(closing_fd, (struct sockaddr*) &directory_addr, sizeof(struct sockaddr_in))) {
    perror("Failed to let directory server know about disconnection");
  } else {
    // Send disconnect message to server
    client_message disconnect = CLIENT_DISCONNECT;
    write(closing_fd, &disconnect, sizeof(client_message));
  }
  close(closing_fd);

  return;
}

int generate_listening_socket(int directory_fd, struct sockaddr_in dir_addr) {
  // Generate listening fd
  int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
  if (listen_fd == -1) {
    perror("socket failed");
    exit(2);
  }
    
  // Set up client options for successive connections
  struct sockaddr_in listen_addr = dir_addr;
  listen_addr.sin_port = htons(0);
  
  // Bind to the specified address
  if (bind(listen_fd, (struct sockaddr*) &listen_addr, sizeof(struct sockaddr_in))) {
    perror("bind");
    exit(2);
  }
  
  // Get the listening socket info so we can find out which port we're using
  socklen_t listen_addr_size = sizeof(struct sockaddr_in);
  getsockname(listen_fd, (struct sockaddr *) &listen_addr, &listen_addr_size);

  // Send explicit new port number for other clients to connect to this client
  write(directory_fd, &listen_addr.sin_port, sizeof(uint16_t));

  return listen_fd;
}

//connects to server, then connects to parent
int connect_to_network(char* server_address, uint16_t port) {
  
  struct hostent* server = gethostbyname(server_address);
  if (server == NULL) {
    fprintf(stderr, "Unable to find host %s\n", server_address);
    exit(1);
  }
  
  int directory_fd = socket(AF_INET, SOCK_STREAM, 0);
  if (directory_fd == -1) {
    perror("socket failed");
    exit(2);
  }
  
  struct sockaddr_in addr = {
    .sin_family = AF_INET,
    .sin_port = htons(port)
  };

  // ect with server
  bcopy((char*)server->h_addr_list[0], (char*)&addr.sin_addr.s_addr, server->h_length);
  if (connect(directory_fd, (struct sockaddr*) &addr, sizeof(struct sockaddr_in))) {
    perror("connect failed");
    exit(2);
  }

  client_message join = CLIENT_JOIN;
  // Tell the server that we would like to join
  write(directory_fd, &join, sizeof(client_message));

  int uid;
  read(directory_fd, &uid, sizeof(int));

  if (uid > 0) {
    connection_options_t* client_buffer =
      (connection_options_t*) malloc(sizeof(connection_options_t) * uid);

    // Read list of clients to connect to from directory
    read(directory_fd, client_buffer, sizeof(connection_options_t) * uid);
    
    int p2p_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (p2p_fd == -1) {
      perror("socket failed");
      exit(2);
    }

    // Seed rng using time
    srand(time(NULL));

    //connecting to parent
    for (int connection_try = 0; connection_try < FIND_PARENT_TIMEOUT; connection_try++) {
      // Randomly select a potential parent from the client_array
      struct sockaddr_in parent_addr = client_buffer[rand() % uid].client_addr;

      // Force connect to root for now
      //struct sockaddr_in parent_addr = client_buffer[0].client_addr;
      
      if (connect(p2p_fd, (struct sockaddr*) &parent_addr, sizeof(struct sockaddr_in)) == 0) {
        // Add parent as first child of this client
        generate_connection_entry(p2p_fd, current_number_children);
        parent_number = current_number_children;
        current_number_children++;
        break;
      } else {
        //perror("connection failed");
      }
    }
    free(client_buffer);
  }

  int listen_fd = generate_listening_socket(directory_fd, addr);
  
  close(directory_fd);

  return listen_fd;
}

int main(int argc, char** argv) {
  
  if (argc != 4) {
    fprintf(stderr, "Usage: %s <username> <server address> <port>\n", argv[0]);
    exit(EXIT_FAILURE);
  }
  
  char* local_user = argv[1];
  server_address = argv[2];
  port = (uint16_t) atoi(argv[3]);

  //connect to server, then connect to parent
  int listen_fd = connect_to_network(server_address, port);
  
  pthread_t accept_children;
  
  pthread_create(&accept_children, NULL, accept_connections, &listen_fd);
    
  // Initialize the chat client's user interface.
  ui_init();
  
  // Add a test message
  ui_add_message(NULL, "Type your message and hit <ENTER> to post.");

  // Loop forever and ever and ever and ever and ever
  bool connected = true;
  while (connected) {
    
    // Read a message from the UI
    char* message = ui_read_input();
    
    // If the message is a quit command, shut down. Otherwise print the message
    if (strcmp(message, "\\quit") == 0) {
      // disconnect from network
      disconnect(server_address, port);
      connected = false;
    } else if (strlen(message) > 0) {
      // Add the message to the UI
      ui_add_message(local_user, message);
      
      // Propagate message to all connected children
      size_t originator = -1;
      propagate_message(local_user, message, originator);
    }
    // Free the message
    free(message);
  }
  
  // Clean up the UI
  ui_shutdown();
  
  return 0;
}
