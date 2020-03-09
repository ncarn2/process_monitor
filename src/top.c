#include <dirent.h>
#include <limits.h>
#include <stdio.h>
#include <unistd.h>

int main() {

    char cwd[PATH_MAX];

    if (chdir("/proc"))
    {
        printf("chdir() to /proc failed\n");
        return 1;
    } 

    int failed = read_proc();

    return 0;
}

int read_proc() {
    DIR *d;
    struct dirent *dir;
    d = opendir("/proc");
    if (d) {
        while ((dir = readdir(d)) != NULL) {
            printf("%s\n", dir->d_name);
        }
        closedir(d);
    }
    return 0;
}
