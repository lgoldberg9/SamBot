#ifndef __CLIENT_H__
#define __CLIENT_H__

#include <pthread.h>

#define MAX_CHILDREN 1000

typedef struct client_child_s {
  int prop_socket;
  pthread_t child_thread;
} client_child_t;

void propagate_message(char* username, char* message, size_t originator);

void* listen_to_child(void* args);

void* accept_connections(void* args);

void disconnect(char* server_address, uint16_t port);

int generate_listening_socket(int directory_fd, struct sockaddr_in dir_addr);

int connect_to_network(char* server_address, uint16_t port);

#endif
