/*
this code build on https://github.com/ashriram/linux-kernel-module-cheat/blob/7a5ca339a356fff98c1537f0b2c5e960757924d8/userland/pagemap_dump.c
with adjusments for only swap area
*/
#define _XOPEN_SOURCE 700
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

#define _POSIX_C_SOURCE 200809L

typedef struct {
    uint64_t offset : 50;
    unsigned int type : 5;
} SwappedEntry;
int pagemap_get_swapped_entry(SwappedEntry *entry, int pagemap_fd, uintptr_t vaddr)
{
	size_t nread;
	ssize_t ret;
	uint64_t data;

	nread = 0;
	while (nread < sizeof(data)) {
		ret = pread(pagemap_fd, &data, sizeof(data),
				(vaddr / sysconf(_SC_PAGE_SIZE)) * sizeof(data) + nread);
		nread += ret;
		if (ret <= 0) {
			return 1;
		}
	}
	uint64_t swapped = (data >> 62) & 1;
	if (swapped == 1)  { 
		entry->type = (data >> 0) & 0x1F;
		entry->offset = (data >> 5) & 0x1FFFFFFFFFFFFULL;
		return 1;
	}
	return 0;
}


int main(int argc, char **argv)
{
	char buffer[BUFSIZ];
	char maps_file[BUFSIZ];
	char pagemap_file[BUFSIZ];
	int maps_fd;
	int offset = 0;
	int pagemap_fd;
	pid_t pid;

	if (argc < 2) {
		printf("Usage: %s pid\n", argv[0]);
		return EXIT_FAILURE;
	}
	pid = strtoull(argv[1], NULL, 0);
	snprintf(maps_file, sizeof(maps_file), "/proc/%ju/maps", (uintmax_t)pid);
	snprintf(pagemap_file, sizeof(pagemap_file), "/proc/%ju/pagemap", (uintmax_t)pid);
	maps_fd = open(maps_file, O_RDONLY);
	if (maps_fd < 0) {
		perror("open maps");
		return EXIT_FAILURE;
	}
	pagemap_fd = open(pagemap_file, O_RDONLY);
	if (pagemap_fd < 0) {
		perror("open pagemap");
		return EXIT_FAILURE;
	}
    printf("+------------------+------------------+------------------+------------------+\n");
    printf("|       vaddr      |      PTE-offset  |     PTE-type     |    Redis-key     |\n");
    printf("+------------------+------------------+------------------+------------------+\n");

	for (;;) {
		ssize_t length = read(maps_fd, buffer + offset, sizeof buffer - offset);
		if (length <= 0) break;
		length += offset;
		for (size_t i = offset; i < (size_t)length; i++) {
			uintptr_t low = 0, high = 0;
			if (buffer[i] == '\n' && i) {
				const char *lib_name;
				size_t y;
				/* Parse a line from maps. Each line contains a range that contains many pages. */
				{
					size_t x = i - 1;
					while (x && buffer[x] != '\n') x--;
					if (buffer[x] == '\n') x++;
					while (buffer[x] != '-' && x < sizeof buffer) {
						char c = buffer[x++];
						low *= 16;
						if (c >= '0' && c <= '9') {
							low += c - '0';
						} else if (c >= 'a' && c <= 'f') {
							low += c - 'a' + 10;
						} else {
						    break;
						}
					}
					while (buffer[x] != '-' && x < sizeof buffer) x++;
					if (buffer[x] == '-') x++;
					while (buffer[x] != ' ' && x < sizeof buffer) {
						char c = buffer[x++];
						high *= 16;
						if (c >= '0' && c <= '9') {
							high += c - '0';
						} else if (c >= 'a' && c <= 'f') {
							high += c - 'a' + 10;
						} else {
							break;
						}
					}
					lib_name = 0;
					for (int field = 0; field < 4; field++) {
						x++;
						while(buffer[x] != ' ' && x < sizeof buffer) x++;
					}
					while (buffer[x] == ' ' && x < sizeof buffer) x++;
					y = x;
					while (buffer[y] != '\n' && y < sizeof buffer) y++;
					buffer[y] = 0;
					lib_name = buffer + x;
				}
				/* Get info about all pages in this page range with pagemap. */
				{
					SwappedEntry entry;
					for (uintptr_t addr = low; addr < high; addr += sysconf(_SC_PAGE_SIZE)) {
						/* TODO always fails for the last page (vsyscall), why? pread returns 0. */
						
						if (pagemap_get_swapped_entry(&entry, pagemap_fd, addr)) {
							printf("| 0x%-14jx | %-16llu | %-16u | %-16llu |\n",
								(uintmax_t)addr,
								(uintmax_t)entry.offset,
								entry.type,
								(uintmax_t)entry.offset * 8

							);
						}
					}
				}
				buffer[y] = '\n';
			}
		}
	}
	close(maps_fd);
	close(pagemap_fd);
	return EXIT_SUCCESS;
}
