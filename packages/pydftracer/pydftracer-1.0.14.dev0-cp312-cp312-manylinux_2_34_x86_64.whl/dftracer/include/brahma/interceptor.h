//
// Created by hariharan on 8/8/22.
//

#ifndef BRAHMA_INTERCEPTOR_H
#define BRAHMA_INTERCEPTOR_H

#include <brahma/brahma_config.hpp>
/* Internal Headers */
#include <brahma/logging.h>
/* External Headers */
#include <gotcha/gotcha.h>

#include <cstdarg>
#include <memory>

#define GOTCHA_BINDING_MACRO(fname, CLASS)                      \
  if constexpr (!std::is_same_v<decltype(&C::fname),            \
                                decltype(&CLASS::fname)>) {     \
    gotcha_binding_t binding = {#fname, (void*)fname##_wrapper, \
                                &fname##_brahma_handle};        \
    bindings.push_back(binding);                                \
  }

#define GOTCHA_MACRO_TYPEDEF(name, ret, args, args_val, class_name) \
  typedef ret(*name##_fptr) args;                                   \
  inline ret name##_wrapper args {                                  \
    return class_name::get_instance()->name args_val;               \
  }
#define GOTCHA_MACRO_TYPEDEF_OPEN(name, ret, args, args_val, start, \
                                  class_name)                       \
  typedef ret(*name##_fptr) args;                                   \
  inline ret name##_wrapper args {                                  \
    va_list _args;                                                  \
    va_start(_args, start);                                         \
    int mode = va_arg(_args, int);                                  \
    va_end(_args);                                                  \
    ret v = class_name::get_instance()->name args_val;              \
    return v;                                                       \
  }

#define GOTCHA_MACRO_TYPEDEF_EXECL(name, ret, args, args_val, start, \
                                   class_name)                       \
  typedef ret(*name##_fptr) args;                                    \
  inline ret name##_wrapper args {                                   \
    va_list _args;                                                   \
    va_start(_args, start);                                          \
    char* val = va_arg(_args, char*);                                \
    va_end(_args);                                                   \
    ret v = class_name::get_instance()->name args_val;               \
    return v;                                                        \
  }

#define GOTCHA_MACRO_VAR(name) gotcha_wrappee_handle_t name##_brahma_handle;

#define BRAHMA_WRAPPER(name) name##_wrapper;

#define BRAHMA_UNWRAPPED_FUNC(name, ret, args)                                \
  BRAHMA_LOG_INFO("[BRAHMA]\tFunction %s() not wrapped. Calling Original.\n", \
                  #name);                                                     \
  name##_fptr name##_wrappee =                                                \
      (name##_fptr)gotcha_get_wrappee(name##_brahma_handle);                  \
  ret result = name##_wrappee args;

#define BRAHMA_UNWRAPPED_FUNC_VOID(name, args)                                \
  BRAHMA_LOG_INFO("[BRAHMA]\tFunction %s() not wrapped. Calling Original.\n", \
                  #name);                                                     \
  name##_fptr name##_wrappee =                                                \
      (name##_fptr)gotcha_get_wrappee(name##_brahma_handle);                  \
  name##_wrappee args;
#define BRAHMA_MAP_OR_FAIL(func_)                                      \
  auto __real_##func_ =                                                \
      (func_##_fptr)gotcha_get_wrappee(func_##_brahma_handle); \
  assert(__real_##func_ != NULL)

#endif  // BRAHMA_INTERCEPTOR_H
