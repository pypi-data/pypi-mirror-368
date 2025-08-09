//
// Created by hariharan on 8/8/22.
//

#ifndef BRAHMA_POSIX_H
#define BRAHMA_POSIX_H
#include <brahma/brahma_config.hpp>
/* Internal Headers */
#include <brahma/interceptor.h>
#include <brahma/interface/interface.h>
/* External Headers */
#include <dirent.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <utime.h>

#include <cstdlib>
#include <stdexcept>

namespace brahma {
class POSIX : public Interface {
 private:
  static std::shared_ptr<POSIX> my_instance;

 public:
  static std::shared_ptr<POSIX> get_instance();

  POSIX() : Interface() {}

  virtual ~POSIX() {}
  template <typename C>
  size_t bind(const char *name, uint16_t priority);

  static int set_instance(std::shared_ptr<POSIX> instance_i);

  virtual int open(const char *pathname, int flags, ...);

  virtual int creat64(const char *path, mode_t mode);

  virtual int open64(const char *path, int flags, ...);

  virtual int close(int fd);

  virtual ssize_t write(int fd, const void *buf, size_t count);

  virtual ssize_t read(int fd, void *buf, size_t count);

  virtual off_t lseek(int fd, off_t offset, int whence);

  virtual off64_t lseek64(int fd, off64_t offset, int whence);

  virtual ssize_t pread(int fd, void *buf, size_t count, off_t offset);

  virtual ssize_t pread64(int fd, void *buf, size_t count, off64_t offset);

  virtual ssize_t pwrite(int fd, const void *buf, size_t count, off64_t offset);

  virtual ssize_t pwrite64(int fd, const void *buf, size_t count,
                           off64_t offset);

  virtual int fsync(int fd);

  virtual int fdatasync(int fd);

  virtual int openat(int dirfd, const char *pathname, int flags, ...);

  virtual int __xstat(int vers, const char *path, struct stat *buf);

  virtual int __xstat64(int vers, const char *path, struct stat64 *buf);

  virtual int __lxstat(int vers, const char *path, struct stat *buf);

  virtual int __lxstat64(int vers, const char *path, struct stat64 *buf);

  virtual int __fxstat(int vers, int fd, struct stat *buf);

  virtual int __fxstat64(int vers, int fd, struct stat64 *buf);

  virtual char *getcwd(char *buf, size_t size);

  virtual int mkdir(const char *pathname, mode_t mode);

  virtual int rmdir(const char *pathname);

  virtual int chdir(const char *path);

  virtual int link(const char *oldpath, const char *newpath);

  virtual int linkat(int fd1, const char *path1, int fd2, const char *path2,
                     int flag);

  virtual int unlink(const char *pathname);

  virtual int symlink(const char *path1, const char *path2);

  virtual int symlinkat(const char *path1, int fd, const char *path2);

  virtual ssize_t readlink(const char *path, char *buf, size_t bufsize);

  virtual ssize_t readlinkat(int fd, const char *path, char *buf,
                             size_t bufsize);

  virtual int rename(const char *oldpath, const char *newpath);

  virtual int chmod(const char *path, mode_t mode);

  virtual int chown(const char *path, uid_t owner, gid_t group);

  virtual int lchown(const char *path, uid_t owner, gid_t group);

  virtual int utime(const char *filename, const utimbuf *buf);

  virtual DIR *opendir(const char *name);

  virtual dirent *readdir(DIR *dir);

  virtual int closedir(DIR *dir);

  virtual void rewinddir(DIR *dir);

  virtual int fcntl(int fd, int cmd, ...);

  virtual int dup(int oldfd);

  virtual int dup2(int oldfd, int newfd);

  virtual int pipe(int pipefd[2]);

  virtual int mkfifo(const char *pathname, mode_t mode);

  virtual mode_t umask(mode_t mask);

  virtual int access(const char *path, int amode);

  virtual int faccessat(int fd, const char *path, int amode, int flag);

  virtual int remove(const char *pathname);

  virtual int truncate(const char *pathname, off_t length);

  virtual int ftruncate(int fd, off_t length);

  virtual int execl(const char *pathname, const char *arg, ...);

  virtual int execlp(const char *file, const char *arg, ...);

  virtual int execv(const char *pathname, char *const argv[]);

  virtual int execvp(const char *file, char *const argv[]);

  virtual int execvpe(const char *file, char *const argv[], char *const envp[]);

  virtual int fork();

  virtual void exit(int status);

  virtual void *mmap(void *addr, size_t length, int prot, int flags, int fd,
                     off_t offset);

  virtual void *mmap64(void *addr, size_t length, int prot, int flags, int fd,
                       off64_t offset);
  
  virtual int munmap(void *addr, size_t len);

  virtual int msync(void *addr, size_t len, int flags);

  virtual long sysconf(int name);

  virtual int madvise(void *addr, size_t length, int advice);

  virtual int mprotect(void *addr, size_t length, int prot);

  virtual int mlock(const void *addr, size_t len);
  
  virtual int munlock(const void *addr, size_t len);

  virtual int mlockall(int flags);

  virtual int munlockall(void);

  /* Handler Definitions */
  GOTCHA_MACRO_VAR(open)
  GOTCHA_MACRO_VAR(creat64)
  GOTCHA_MACRO_VAR(open64)
  GOTCHA_MACRO_VAR(close)
  GOTCHA_MACRO_VAR(write)
  GOTCHA_MACRO_VAR(read)
  GOTCHA_MACRO_VAR(lseek)
  GOTCHA_MACRO_VAR(lseek64)
  GOTCHA_MACRO_VAR(pread)
  GOTCHA_MACRO_VAR(pread64)
  GOTCHA_MACRO_VAR(pwrite)
  GOTCHA_MACRO_VAR(pwrite64)
  GOTCHA_MACRO_VAR(fsync)
  GOTCHA_MACRO_VAR(fdatasync)
  GOTCHA_MACRO_VAR(openat)
  GOTCHA_MACRO_VAR(__xstat)
  GOTCHA_MACRO_VAR(__xstat64)
  GOTCHA_MACRO_VAR(__lxstat)
  GOTCHA_MACRO_VAR(__lxstat64)
  GOTCHA_MACRO_VAR(__fxstat)
  GOTCHA_MACRO_VAR(__fxstat64)
  GOTCHA_MACRO_VAR(getcwd)
  GOTCHA_MACRO_VAR(mkdir)
  GOTCHA_MACRO_VAR(rmdir)
  GOTCHA_MACRO_VAR(chdir)
  GOTCHA_MACRO_VAR(link)
  GOTCHA_MACRO_VAR(linkat)
  GOTCHA_MACRO_VAR(unlink)
  GOTCHA_MACRO_VAR(symlink)
  GOTCHA_MACRO_VAR(symlinkat)
  GOTCHA_MACRO_VAR(readlink)
  GOTCHA_MACRO_VAR(readlinkat)
  GOTCHA_MACRO_VAR(rename)
  GOTCHA_MACRO_VAR(chmod)
  GOTCHA_MACRO_VAR(chown)
  GOTCHA_MACRO_VAR(lchown)
  GOTCHA_MACRO_VAR(utime)
  GOTCHA_MACRO_VAR(opendir)
  GOTCHA_MACRO_VAR(readdir)
  GOTCHA_MACRO_VAR(closedir)
  GOTCHA_MACRO_VAR(rewinddir)
  GOTCHA_MACRO_VAR(fcntl)
  GOTCHA_MACRO_VAR(dup)
  GOTCHA_MACRO_VAR(dup2)
  GOTCHA_MACRO_VAR(pipe)
  GOTCHA_MACRO_VAR(mkfifo)
  GOTCHA_MACRO_VAR(umask)
  GOTCHA_MACRO_VAR(access)
  GOTCHA_MACRO_VAR(faccessat)
  GOTCHA_MACRO_VAR(remove)
  GOTCHA_MACRO_VAR(truncate)
  GOTCHA_MACRO_VAR(ftruncate)
  GOTCHA_MACRO_VAR(execl)
  GOTCHA_MACRO_VAR(execlp)
  GOTCHA_MACRO_VAR(execv)
  GOTCHA_MACRO_VAR(execvp)
  GOTCHA_MACRO_VAR(execvpe)
  GOTCHA_MACRO_VAR(fork)
  GOTCHA_MACRO_VAR(exit)
  GOTCHA_MACRO_VAR(mmap)
  GOTCHA_MACRO_VAR(mmap64)
  GOTCHA_MACRO_VAR(munmap)
  GOTCHA_MACRO_VAR(msync)
  GOTCHA_MACRO_VAR(sysconf)
  GOTCHA_MACRO_VAR(madvise)
  GOTCHA_MACRO_VAR(mprotect)
  GOTCHA_MACRO_VAR(mlock)
  GOTCHA_MACRO_VAR(munlock)
  GOTCHA_MACRO_VAR(mlockall)
  GOTCHA_MACRO_VAR(munlockall)
};

}  // namespace brahma

GOTCHA_MACRO_TYPEDEF_OPEN(open, int, (const char *pathname, int flags, ...),
                          (pathname, flags, mode), flags, brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(creat64, int, (const char *path, mode_t mode),
                     (path, mode), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF_OPEN(open64, int, (const char *path, int flags, ...),
                          (path, flags, mode), flags, brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(close, int, (int fd), (fd), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(write, ssize_t, (int fd, const void *buf, size_t count),
                     (fd, buf, count), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(read, ssize_t, (int fd, void *buf, size_t count),
                     (fd, buf, count), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(lseek, off_t, (int fd, off_t offset, int whence),
                     (fd, offset, whence), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(lseek64, off64_t, (int fd, off64_t offset, int whence),
                     (fd, offset, whence), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(pread, ssize_t,
                     (int fd, void *buf, size_t count, off_t offset),
                     (fd, buf, count, offset), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(pread64, ssize_t,
                     (int fd, void *buf, size_t count, off64_t offset),
                     (fd, buf, count, offset), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(pwrite, ssize_t,
                     (int fd, const void *buf, size_t count, off_t offset),
                     (fd, buf, count, offset), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(pwrite64, ssize_t,
                     (int fd, const void *buf, size_t count, off64_t offset),
                     (fd, buf, count, offset), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(fsync, int, (int fd), (fd), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(fdatasync, int, (int fd), (fd), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF_OPEN(openat, int,
                          (int dirfd, const char *pathname, int flags, ...),
                          (dirfd, pathname, flags, mode), flags, brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(__xstat, int,
                     (int vers, const char *path, struct stat *buf),
                     (vers, path, buf), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(__xstat64, int,
                     (int vers, const char *path, struct stat64 *buf),
                     (vers, path, buf), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(__lxstat, int,
                     (int vers, const char *path, struct stat *buf),
                     (vers, path, buf), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(__lxstat64, int,
                     (int vers, const char *path, struct stat64 *buf),
                     (vers, path, buf), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(__fxstat, int, (int vers, int fd, struct stat *buf),
                     (vers, fd, buf), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(__fxstat64, int, (int vers, int fd, struct stat64 *buf),
                     (vers, fd, buf), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(getcwd, char *, (char *buf, size_t size), (buf, size),
                     brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(mkdir, int, (const char *pathname, mode_t mode),
                     (pathname, mode), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(rmdir, int, (const char *pathname), (pathname),
                     brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(chdir, int, (const char *path), (path), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(link, int, (const char *oldpath, const char *newpath),
                     (oldpath, newpath), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(linkat, int,
                     (int fd1, const char *path1, int fd2, const char *path2,
                      int flag),
                     (fd1, path1, fd2, path2, flag), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(unlink, int, (const char *pathname), (pathname),
                     brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(symlink, int, (const char *path1, const char *path2),
                     (path1, path2), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(symlinkat, int,
                     (const char *path1, int fd, const char *path2),
                     (path1, fd, path2), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(readlink, ssize_t,
                     (const char *path, char *buf, size_t bufsize),
                     (path, buf, bufsize), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(readlinkat, ssize_t,
                     (int fd, const char *path, char *buf, size_t bufsize),
                     (fd, path, buf, bufsize), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(rename, int, (const char *oldpath, const char *newpath),
                     (oldpath, newpath), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(chmod, int, (const char *path, mode_t mode), (path, mode),
                     brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(chown, int, (const char *path, uid_t owner, gid_t group),
                     (path, owner, group), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(lchown, int, (const char *path, uid_t owner, gid_t group),
                     (path, owner, group), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(utime, int, (const char *filename, const utimbuf *buf),
                     (filename, buf), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(opendir, DIR *, (const char *name), (name), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(readdir, struct dirent *, (DIR * dir), (dir),
                     brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(closedir, int, (DIR * dir), (dir), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(rewinddir, void, (DIR * dir), (dir), brahma::POSIX)
typedef int (*fcntl_fptr)(int fd, int cmd, ...);
inline int fcntl_wrapper(int fd, int cmd, ...) {
  if (cmd == F_DUPFD || cmd == F_DUPFD_CLOEXEC || cmd == F_SETFD ||
      cmd == F_SETFL || cmd == F_SETOWN) {  // arg: int
    va_list arg;
    va_start(arg, cmd);
    int val = va_arg(arg, int);
    va_end(arg);
    int v = brahma::POSIX::get_instance()->fcntl(fd, cmd, val);
    return v;
  } else if (cmd == F_GETFD || cmd == F_GETFL || cmd == F_GETOWN) {
    int v = brahma::POSIX::get_instance()->fcntl(fd, cmd);
    return v;
  } else if (cmd == F_SETLK || cmd == F_SETLKW || cmd == F_GETLK) {
    va_list arg;
    va_start(arg, cmd);
    struct flock *lk = va_arg(arg, struct flock *);
    va_end(arg);
    int v = brahma::POSIX::get_instance()->fcntl(fd, cmd, lk);
    return v;
  } else {  // assume arg: void, cmd==F_GETOWN_EX || cmd==F_SETOWN_EX
            // ||cmd==F_GETSIG || cmd==F_SETSIG)
    int v = brahma::POSIX::get_instance()->fcntl(fd, cmd);
    return v;
  }
}
gotcha_wrappee_handle_t get_fcntl_handle();
GOTCHA_MACRO_TYPEDEF(dup, int, (int oldfd), (oldfd), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(dup2, int, (int oldfd, int newfd), (oldfd, newfd),
                     brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(pipe, int, (int pipefd[2]), (pipefd), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(mkfifo, int, (const char *pathname, mode_t mode),
                     (pathname, mode), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(umask, mode_t, (mode_t mask), (mask), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(access, int, (const char *path, int amode), (path, amode),
                     brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(faccessat, int,
                     (int fd, const char *path, int amode, int flag),
                     (fd, path, amode, flag), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(remove, int, (const char *pathname), (pathname),
                     brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(truncate, int, (const char *pathname, off_t length),
                     (pathname, length), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(ftruncate, int, (int fd, off_t length), (fd, length),
                     brahma::POSIX)
GOTCHA_MACRO_TYPEDEF_EXECL(execl, int,
                           (const char *pathname, const char *arg, ...),
                           (pathname, arg, val), arg, brahma::POSIX)
GOTCHA_MACRO_TYPEDEF_EXECL(execlp, int,
                           (const char *pathname, const char *arg, ...),
                           (pathname, arg, val), arg, brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(execv, int, (const char *pathname, char *const argv[]),
                     (pathname, argv), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(execvp, int, (const char *pathname, char *const argv[]),
                     (pathname, argv), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(execvpe, int,
                     (const char *pathname, char *const argv[],
                      char *const envp[]),
                     (pathname, argv, envp), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(fork, int, (), (), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(exit, void,
                     (int status),
                     (status), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(mmap, void *,
                     (void *addr, size_t length, int prot, int flags, int fd,
                      off_t offset),
                     (addr, length, prot, flags, fd, offset), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(mmap64, void *,
                     (void *addr, size_t length, int prot, int flags, int fd,
                      off64_t offset),
                     (addr, length, prot, flags, fd, offset), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(munmap, int,
                     (void *addr, size_t len),
                     (addr, len), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(msync, int,
                     (void *addr, size_t len, int flags),
                     (addr, len, flags), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(sysconf, long,
                     (int name),
                     (name), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(madvise, int,
                     (void *addr, size_t length, int advice),
                     (addr, length, advice), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(mprotect, int,
                     (void *addr, size_t length, int prot),
                     (addr, length, prot), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(mlock, int,
                     (const void *addr, size_t length),
                     (addr, length), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(munlock, int,
                     (const void *addr, size_t length),
                     (addr, length), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(mlockall, int,
                     (int flags),
                     (flags), brahma::POSIX)
GOTCHA_MACRO_TYPEDEF(munlockall, int, (), (), brahma::POSIX)

template <typename C>
size_t brahma::POSIX::bind(const char *name, uint16_t priority) {
  GOTCHA_BINDING_MACRO(open, POSIX);
  GOTCHA_BINDING_MACRO(creat64, POSIX);
  GOTCHA_BINDING_MACRO(open64, POSIX);
  GOTCHA_BINDING_MACRO(close, POSIX);
  GOTCHA_BINDING_MACRO(write, POSIX);
  GOTCHA_BINDING_MACRO(read, POSIX);
  GOTCHA_BINDING_MACRO(lseek, POSIX);
  GOTCHA_BINDING_MACRO(lseek64, POSIX);
  GOTCHA_BINDING_MACRO(pread, POSIX);
  GOTCHA_BINDING_MACRO(pread64, POSIX);
  GOTCHA_BINDING_MACRO(pwrite, POSIX);
  GOTCHA_BINDING_MACRO(pwrite64, POSIX);
  GOTCHA_BINDING_MACRO(fsync, POSIX);
  GOTCHA_BINDING_MACRO(fdatasync, POSIX);
  GOTCHA_BINDING_MACRO(openat, POSIX);
  GOTCHA_BINDING_MACRO(__xstat, POSIX);
  GOTCHA_BINDING_MACRO(__xstat64, POSIX);
  GOTCHA_BINDING_MACRO(__lxstat, POSIX);
  GOTCHA_BINDING_MACRO(__lxstat64, POSIX);
  GOTCHA_BINDING_MACRO(__fxstat, POSIX);
  GOTCHA_BINDING_MACRO(__fxstat64, POSIX);
  GOTCHA_BINDING_MACRO(getcwd, POSIX);
  GOTCHA_BINDING_MACRO(mkdir, POSIX);
  GOTCHA_BINDING_MACRO(rmdir, POSIX);
  GOTCHA_BINDING_MACRO(chdir, POSIX);
  GOTCHA_BINDING_MACRO(link, POSIX);
  GOTCHA_BINDING_MACRO(linkat, POSIX);
  GOTCHA_BINDING_MACRO(unlink, POSIX);
  GOTCHA_BINDING_MACRO(symlink, POSIX);
  GOTCHA_BINDING_MACRO(symlinkat, POSIX);
  GOTCHA_BINDING_MACRO(readlink, POSIX);
  GOTCHA_BINDING_MACRO(readlinkat, POSIX);
  GOTCHA_BINDING_MACRO(rename, POSIX);
  GOTCHA_BINDING_MACRO(chmod, POSIX);
  GOTCHA_BINDING_MACRO(chown, POSIX);
  GOTCHA_BINDING_MACRO(lchown, POSIX);
  GOTCHA_BINDING_MACRO(utime, POSIX);
  GOTCHA_BINDING_MACRO(opendir, POSIX);
  GOTCHA_BINDING_MACRO(readdir, POSIX);
  GOTCHA_BINDING_MACRO(closedir, POSIX);
  GOTCHA_BINDING_MACRO(rewinddir, POSIX);
  GOTCHA_BINDING_MACRO(fcntl, POSIX);
  GOTCHA_BINDING_MACRO(dup, POSIX);
  GOTCHA_BINDING_MACRO(dup2, POSIX);
  GOTCHA_BINDING_MACRO(pipe, POSIX);
  GOTCHA_BINDING_MACRO(mkfifo, POSIX);
  GOTCHA_BINDING_MACRO(umask, POSIX);
  GOTCHA_BINDING_MACRO(access, POSIX);
  GOTCHA_BINDING_MACRO(faccessat, POSIX);
  GOTCHA_BINDING_MACRO(remove, POSIX);
  GOTCHA_BINDING_MACRO(truncate, POSIX);
  GOTCHA_BINDING_MACRO(ftruncate, POSIX);
  GOTCHA_BINDING_MACRO(execl, POSIX);
  GOTCHA_BINDING_MACRO(execlp, POSIX);
  GOTCHA_BINDING_MACRO(execv, POSIX);
  GOTCHA_BINDING_MACRO(execvp, POSIX);
  GOTCHA_BINDING_MACRO(execvpe, POSIX);
  GOTCHA_BINDING_MACRO(fork, POSIX);
  GOTCHA_BINDING_MACRO(exit, POSIX);
  GOTCHA_BINDING_MACRO(mmap, POSIX);
  GOTCHA_BINDING_MACRO(mmap64, POSIX);
  GOTCHA_BINDING_MACRO(munmap, POSIX);
  GOTCHA_BINDING_MACRO(msync, POSIX);
  GOTCHA_BINDING_MACRO(sysconf, POSIX);
  GOTCHA_BINDING_MACRO(madvise, POSIX);
  GOTCHA_BINDING_MACRO(mprotect, POSIX);
  GOTCHA_BINDING_MACRO(mlock, POSIX);
  GOTCHA_BINDING_MACRO(munlock, POSIX);
  GOTCHA_BINDING_MACRO(mlockall, POSIX);
  GOTCHA_BINDING_MACRO(munlockall, POSIX);
  num_bindings = bindings.size();
  if (num_bindings > 0) {
    char tool_name[64];
    sprintf(tool_name, "%s_posix", name);
    gotcha_binding_t *raw_bindings = bindings.data();
    gotcha_wrap(raw_bindings, num_bindings, tool_name);
    gotcha_set_priority(tool_name, priority);
  }
  return num_bindings;
}

#endif  // BRAHMA_POSIX_H
