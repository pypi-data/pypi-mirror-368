//
// Created by hariharan on 8/8/22.
//

#ifndef BRAHMA_STDIO_H
#define BRAHMA_STDIO_H

#include <brahma/brahma_config.hpp>
/* Internal Headers */
#include <brahma/interceptor.h>
#include <brahma/interface/interface.h>
/* External Headers */
#include <cstdio>
#include <stdexcept>

namespace brahma {
class STDIO : public Interface {
 private:
  static std::shared_ptr<STDIO> my_instance;

 public:
  static std::shared_ptr<STDIO> get_instance() {
    if (my_instance == nullptr) {
      BRAHMA_LOG_INFO("STDIO class not intercepted but used", "");
      my_instance = std::make_shared<STDIO>();
    }
    return my_instance;
  }
  STDIO() : Interface() {}
  virtual ~STDIO(){};
  static int set_instance(std::shared_ptr<STDIO> instance_i) {
    if (instance_i != nullptr) {
      my_instance = instance_i;
      return 0;
    } else {
      BRAHMA_LOG_ERROR("%s instance_i is not set", "STDIO");
      throw std::runtime_error("instance_i is not set");
    }
  }

  template <typename C>
  size_t bind(const char *name, uint16_t priority);

  virtual FILE *fopen(const char *path, const char *mode);
  virtual FILE *fopen64(const char *path, const char *mode);
  virtual int fclose(FILE *fp);
  virtual size_t fread(void *ptr, size_t size, size_t nmemb, FILE *stream);
  virtual size_t fwrite(const void *ptr, size_t size, size_t nmemb,
                        FILE *stream);
  virtual long ftell(FILE *fp);
  virtual int fseek(FILE *stream, long offset, int whence);
  virtual FILE *fdopen(int fd, const char *mode);
  virtual int fileno(FILE *stream);
  virtual FILE *tmpfile(void);
  virtual int fseeko(FILE *stream, off_t offset, int whence);
  virtual off_t ftello(FILE *stream);


  GOTCHA_MACRO_VAR(fopen)
  GOTCHA_MACRO_VAR(fopen64)
  GOTCHA_MACRO_VAR(fclose)
  GOTCHA_MACRO_VAR(fread)
  GOTCHA_MACRO_VAR(fwrite)
  GOTCHA_MACRO_VAR(ftell)
  GOTCHA_MACRO_VAR(fseek)
  GOTCHA_MACRO_VAR(fdopen)
  GOTCHA_MACRO_VAR(fileno)
  GOTCHA_MACRO_VAR(tmpfile)
  GOTCHA_MACRO_VAR(fseeko)
  GOTCHA_MACRO_VAR(ftello)
};

}  // namespace brahma
GOTCHA_MACRO_TYPEDEF(fopen, FILE *, (const char *path, const char *mode),
                     (path, mode), brahma::STDIO)

GOTCHA_MACRO_TYPEDEF(fopen64, FILE *, (const char *path, const char *mode),
                     (path, mode), brahma::STDIO)

GOTCHA_MACRO_TYPEDEF(fclose, int, (FILE * fp), (fp), brahma::STDIO)

GOTCHA_MACRO_TYPEDEF(fread, size_t,
                     (void *ptr, size_t size, size_t nmemb, FILE *stream),
                     (ptr, size, nmemb, stream), brahma::STDIO)

GOTCHA_MACRO_TYPEDEF(fwrite, size_t,
                     (const void *ptr, size_t size, size_t nmemb, FILE *stream),
                     (ptr, size, nmemb, stream), brahma::STDIO)

GOTCHA_MACRO_TYPEDEF(ftell, long, (FILE * stream), (stream), brahma::STDIO)

GOTCHA_MACRO_TYPEDEF(fseek, int, (FILE * stream, long offset, int whence),
                     (stream, offset, whence), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(fdopen, FILE *, (int fd, const char *mode), (fd, mode),
                     brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(fileno, int, (FILE * stream), (stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(tmpfile, FILE *, (void), (), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(fseeko, int, (FILE * stream, off_t offset, int whence),
                     (stream, offset, whence), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(ftello, off_t, (FILE * stream), (stream), brahma::STDIO)


template <typename C>
size_t brahma::STDIO::bind(const char *name, uint16_t priority) {
  GOTCHA_BINDING_MACRO(fopen, STDIO);
  GOTCHA_BINDING_MACRO(fopen64, STDIO);
  GOTCHA_BINDING_MACRO(fclose, STDIO);
  GOTCHA_BINDING_MACRO(fread, STDIO);
  GOTCHA_BINDING_MACRO(fwrite, STDIO);
  GOTCHA_BINDING_MACRO(ftell, STDIO);
  GOTCHA_BINDING_MACRO(fseek, STDIO);
  GOTCHA_BINDING_MACRO(tmpfile, STDIO);
  GOTCHA_BINDING_MACRO(fseeko, STDIO);
  GOTCHA_BINDING_MACRO(ftello, STDIO);
  GOTCHA_BINDING_MACRO(fdopen, STDIO);
  GOTCHA_BINDING_MACRO(fileno, STDIO);
  num_bindings = bindings.size();
  if (num_bindings > 0) {
    char tool_name[64];
    sprintf(tool_name, "%s_stdio", name);
    gotcha_binding_t *raw_bindings = bindings.data();
    gotcha_wrap(raw_bindings, num_bindings, tool_name);
    gotcha_set_priority(tool_name, priority);
  }
  return num_bindings;
}
#endif  // BRAHMA_STDIO_H
