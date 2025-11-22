#include <stdio.h>
#include <stdint.h>
#include <string.h>

// Constants for the Leaky Bucket Algorithm
#define BUCKET_CAPACITY 1000 // Max capacity in units (e.g., bytes or packets)
#define OUTPUT_RATE     100  // Fixed output rate in units/tick
#define SIMULATION_TICKS 10

// Simulated packet stream (units arriving at each time tick)
// This simulates bursty traffic
const int INCOMING_PACKETS[SIMULATION_TICKS] = {
    150, 400, 50, 600, 300, 10, 500, 50, 100, 200
};

void leaky_bucket_simulation() {
    int bucket_level = 0; // Current level of the bucket (initially empty)
    int total_attempted = 0;
    int total_accepted = 0;
    int total_dropped = 0;
    int total_sent = 0;
    int tick;

    printf("--- Leaky Bucket Congestion Control Simulation ---\n\n");
    printf("Configuration:\n");
    printf("  Bucket Capacity: %d units\n", BUCKET_CAPACITY);
    printf("  Output Rate (Leak Rate): %d units/tick\n", OUTPUT_RATE);
    printf("  Total Ticks: %d\n", SIMULATION_TICKS);
    printf("------------------------------------------------------------------\n");
    printf("| Tick | Incoming | Accepted | Dropped | Current Level | Sent Out |\n");
    printf("------------------------------------------------------------------\n");

    for (tick = 0; tick < SIMULATION_TICKS; tick++) {
        int incoming_packet = INCOMING_PACKETS[tick];
        int accepted_packet = 0;
        int dropped_packet = 0;
        int sent_out = 0;
        total_attempted += incoming_packet;

        // --- 1. Handle Incoming Packet (Check for Overflow) ---
        int space_available = BUCKET_CAPACITY - bucket_level;

        if (incoming_packet <= space_available) {
            // Packet fits entirely
            accepted_packet = incoming_packet;
            bucket_level += accepted_packet;
        } else {
            // Bucket overflow: accept only what fits, drop the rest.
            accepted_packet = space_available;
            dropped_packet = incoming_packet - accepted_packet;
            bucket_level = BUCKET_CAPACITY; // Bucket is now full
        }
        
        total_accepted += accepted_packet;
        total_dropped += dropped_packet;

        // --- 2. Drain the Bucket (Fixed Output Rate) ---
        if (bucket_level > 0) {
            // Send out at most the OUTPUT_RATE or whatever is left in the bucket
            if (bucket_level >= OUTPUT_RATE) {
                sent_out = OUTPUT_RATE;
                bucket_level -= OUTPUT_RATE;
            } else {
                sent_out = bucket_level;
                bucket_level = 0; // Bucket becomes empty
            }
            total_sent += sent_out;
        }

        // --- 3. Report Status ---
        printf("| %4d | %8d | %8d | %7d | %13d | %8d |\n",
               tick + 1,
               incoming_packet,
               accepted_packet,
               dropped_packet,
               bucket_level,
               sent_out);
    }
    printf("------------------------------------------------------------------\n");
    printf("\nSimulation Summary:\n");
    printf("Total Attempted Input: %d\n", total_attempted);
    printf("Total Accepted: %d\n", total_accepted);
    printf("Total Dropped: %d\n", total_dropped);
    printf("Total Sent (Smoothed Output): %d\n", total_sent);
    printf("Final Bucket Level: %d\n", bucket_level);
}

int main() {
    leaky_bucket_simulation();
    return 0;
}
