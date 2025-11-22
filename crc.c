#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define CRC_CCITT_POLY 0x1021
#define CRC_CCITT_INIT 0xFFFF

uint16_t calculate_crc16_ccitt(const unsigned char *data, size_t length) {
    uint16_t crc = CRC_CCITT_INIT;
    size_t i, j;

    for (i = 0; i < length; i++) {
        crc ^= (uint16_t)(data[i] << 8);

        for (j = 0; j < 8; j++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ CRC_CCITT_POLY;
            } else {
                crc = (crc << 1);
            }
            crc &= 0xFFFF;
        }
    }

    return crc;
}

int check_data_integrity(const unsigned char *data, size_t length) {
    uint16_t result = calculate_crc16_ccitt(data, length);
    return result == 0x0000;
}

int main() {
    const char *original_message = "Hello, CRC-CCITT!";
    size_t data_length = strlen(original_message);

    printf("--- CRC-CCITT (16-bit) Implementation ---\n\n");
    printf("Original Message: \"%s\" (Length: %zu bytes)\n", original_message, data_length);

    uint16_t checksum = calculate_crc16_ccitt((const unsigned char *)original_message, data_length);

    printf("Calculated CRC Checksum: 0x%04X\n\n", checksum);

    size_t frame_length = data_length + 2;
    unsigned char frame[frame_length];

    memcpy(frame, original_message, data_length);

    frame[data_length] = (unsigned char)(checksum >> 8);
    frame[data_length + 1] = (unsigned char)(checksum & 0xFF);

    printf("--- Transmission and Verification Simulation ---\n");
    printf("Full Frame Size (Data + CRC): %zu bytes\n", frame_length);

    printf("\n[Scenario A: Data is intact]\n");
    int intact_check = check_data_integrity(frame, frame_length);

    if (intact_check) {
        printf("Verification Status: PASS (Calculated CRC of frame is 0x0000)\n");
    } else {
        printf("Verification Status: FAIL (Calculated CRC of frame is 0x%04X)\n", calculate_crc16_ccitt(frame, frame_length));
    }

    printf("\n[Scenario B: Data is corrupted]\n");
    size_t error_index = 4;
    frame[error_index] ^= 0x01;

    printf("Corruption: Flipped a bit in byte index %zu.\n", error_index);

    int corrupted_check = check_data_integrity(frame, frame_length);

    if (corrupted_check) {
        printf("Verification Status: FAIL (Calculated CRC of frame is 0x0000, but data was corrupted! - This is a rare, undetected error case.)\n");
    } else {
        printf("Verification Status: FAIL (Calculated CRC of frame is 0x%04X). Error successfully detected.\n", calculate_crc16_ccitt(frame, frame_length));
    }

    return 0;
}
