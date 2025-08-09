#ifndef BRAHMA_COMMON_BRAHMA_LOGGING_H
#define BRAHMA_COMMON_BRAHMA_LOGGING_H

#include <brahma/brahma_config.hpp>
/* Internal Headers */
#include <brahma/interceptor.h>
#include <brahma/interface/interface.h>
/* External Headers */
#include <sys/types.h>
#include <unistd.h>

#include <chrono>
#include <string>

#define VA_ARGS(...) , ##__VA_ARGS__

inline std::string brahma_macro_get_time() {
  auto brahma_ts_millis =
      std::chrono::duration_cast<std::chrono::milliseconds>(
          std::chrono::system_clock::now().time_since_epoch())
          .count() %
      1000;
  auto brahma_ts_t = std::time(0);
  auto now = std::localtime(&brahma_ts_t);
  char brahma_ts_time_str[256];
  sprintf(brahma_ts_time_str, "%04d-%02d-%02d %02d:%02d:%02d.%ld",
          now->tm_year + 1900, now->tm_mon + 1, now->tm_mday, now->tm_hour,
          now->tm_min, now->tm_sec, brahma_ts_millis);
  return brahma_ts_time_str;
}

// #define BRAHMA_NOOP_MACRO do {} while (0)

//=============================================================================
#ifdef BRAHMA_LOGGER_NO_LOG
//=============================================================================
#define BRAHMA_LOGGER_INIT() BRAHMA_NOOP_MACRO
#define BRAHMA_LOG_PRINT(format, ...) fprintf(stdout, format, __VA_ARGS__);
#define BRAHMA_LOG_ERROR(format, ...) fprintf(stderr, format, __VA_ARGS__);
#define BRAHMA_LOG_WARN(format, ...) BRAHMA_NOOP_MACRO
#define BRAHMA_LOG_INFO(format, ...) BRAHMA_NOOP_MACRO
#define BRAHMA_LOG_DEBUG(format, ...) BRAHMA_NOOP_MACRO
#define BRAHMA_LOG_TRACE() BRAHMA_NOOP_MACRO
#define BRAHMA_LOG_TRACE_FORMAT(...) BRAHMA_NOOP_MACRO
#define BRAHMA_LOG_STDOUT_REDIRECT(fpath) BRAHMA_NOOP_MACRO
#define BRAHMA_LOG_STDERR_REDIRECT(fpath) BRAHMA_NOOP_MACRO
//=============================================================================
#else
//=============================================================================

#if defined(BRAHMA_LOGGER_CPP_LOGGER)  // CPP_LOGGER
// ---------------------------
#include <cpp-logger/clogger.h>

#define BRAHMA_LOG_STDOUT_REDIRECT(fpath) freopen((fpath), "a+", stdout);
#define BRAHMA_LOG_STDERR_REDIRECT(fpath) freopen((fpath), "a+", stderr);
#define BRAHMA_LOGGER_NAME "BRAHMA"

#define BRAHMA_INTERNAL_TRACE(file, line, function, name, logger_level) \
  cpp_logger_clog(logger_level, name, "[%s] %s [%s:%d]",                \
                  brahma_macro_get_time().c_str(), function, file, line);

#define BRAHMA_INTERNAL_TRACE_FORMAT(file, line, function, name, logger_level, \
                                     format, ...)                              \
  cpp_logger_clog(logger_level, name, "[%s] %s " format " [%s:%d]",            \
                  brahma_macro_get_time().c_str(), function, ##__VA_ARGS__,    \
                  file, line);

#define BRAHMA_LOG_PRINT(format, ...)                                        \
  BRAHMA_INTERNAL_TRACE_FORMAT(__FILE__, __LINE__, __FUNCTION__,             \
                               BRAHMA_LOGGER_NAME, CPP_LOGGER_PRINT, format, \
                               __VA_ARGS__);
#ifdef BRAHMA_LOGGER_LEVEL_TRACE
#define BRAHMA_LOGGER_INIT() \
  cpp_logger_clog_level(CPP_LOGGER_TRACE, BRAHMA_LOGGER_NAME);
#elif defined(BRAHMA_LOGGER_LEVEL_DEBUG)
#define BRAHMA_LOGGER_INIT() \
  cpp_logger_clog_level(CPP_LOGGER_DEBUG, BRAHMA_LOGGER_NAME);
#elif defined(BRAHMA_LOGGER_LEVEL_INFO)
#define BRAHMA_LOGGER_INIT() \
  cpp_logger_clog_level(CPP_LOGGER_INFO, BRAHMA_LOGGER_NAME);
#elif defined(BRAHMA_LOGGER_LEVEL_WARN)
#define BRAHMA_LOGGER_INIT() \
  cpp_logger_clog_level(CPP_LOGGER_WARN, BRAHMA_LOGGER_NAME);
#else
#define BRAHMA_LOGGER_INIT() \
  cpp_logger_clog_level(CPP_LOGGER_ERROR, BRAHMA_LOGGER_NAME);
#endif

#ifdef BRAHMA_LOGGER_LEVEL_TRACE
#define BRAHMA_LOG_TRACE()                                                    \
  BRAHMA_INTERNAL_TRACE(__FILE__, __LINE__, __FUNCTION__, BRAHMA_LOGGER_NAME, \
                        CPP_LOGGER_TRACE);
#define BRAHMA_LOG_TRACE_FORMAT(format, ...)                                 \
  BRAHMA_INTERNAL_TRACE_FORMAT(__FILE__, __LINE__, __FUNCTION__,             \
                               BRAHMA_LOGGER_NAME, CPP_LOGGER_TRACE, format, \
                               __VA_ARGS__);
#else
#define BRAHMA_LOG_TRACE(...) BRAHMA_NOOP_MACRO
#define BRAHMA_LOG_TRACE_FORMAT(...) BRAHMA_NOOP_MACRO
#endif

#ifdef BRAHMA_LOGGER_LEVEL_DEBUG
#define BRAHMA_LOG_DEBUG(format, ...)                                        \
  BRAHMA_INTERNAL_TRACE_FORMAT(__FILE__, __LINE__, __FUNCTION__,             \
                               BRAHMA_LOGGER_NAME, CPP_LOGGER_DEBUG, format, \
                               __VA_ARGS__);
#else
#define BRAHMA_LOG_DEBUG(format, ...) BRAHMA_NOOP_MACRO
#endif

#ifdef BRAHMA_LOGGER_LEVEL_INFO
#define BRAHMA_LOG_INFO(format, ...)                                        \
  BRAHMA_INTERNAL_TRACE_FORMAT(__FILE__, __LINE__, __FUNCTION__,            \
                               BRAHMA_LOGGER_NAME, CPP_LOGGER_INFO, format, \
                               ##__VA_ARGS__);
#else
#define BRAHMA_LOG_INFO(format, ...) BRAHMA_NOOP_MACRO
#endif

#ifdef BRAHMA_LOGGER_LEVEL_WARN
#define BRAHMA_LOG_WARN(format, ...)                                        \
  BRAHMA_INTERNAL_TRACE_FORMAT(__FILE__, __LINE__, __FUNCTION__,            \
                               BRAHMA_LOGGER_NAME, CPP_LOGGER_WARN, format, \
                               __VA_ARGS__);
#else
#define BRAHMA_LOG_WARN(format, ...) BRAHMA_NOOP_MACRO
#endif

#ifdef BRAHMA_LOGGER_LEVEL_ERROR
#define BRAHMA_LOG_ERROR(format, ...)                                        \
  BRAHMA_INTERNAL_TRACE_FORMAT(__FILE__, __LINE__, __FUNCTION__,             \
                               BRAHMA_LOGGER_NAME, CPP_LOGGER_ERROR, format, \
                               __VA_ARGS__);
#else
#define BRAHMA_LOG_ERROR(format, ...) BRAHMA_NOOP_MACRO
#endif
#else
#define BRAHMA_LOGGER_INIT() BRAHMA_NOOP_MACRO
#define BRAHMA_LOG_PRINT(format, ...) fprintf(stdout, format, __VA_ARGS__);
#define BRAHMA_LOG_ERROR(format, ...) fprintf(stderr, format, __VA_ARGS__);
#define BRAHMA_LOG_WARN(format, ...) BRAHMA_NOOP_MACRO
#define BRAHMA_LOG_INFO(format, ...) BRAHMA_NOOP_MACRO
#define BRAHMA_LOG_DEBUG(format, ...) BRAHMA_NOOP_MACRO
#define BRAHMA_LOG_TRACE() BRAHMA_NOOP_MACRO
#define BRAHMA_LOG_TRACE_FORMAT(...) BRAHMA_NOOP_MACRO
#define BRAHMA_LOG_STDOUT_REDIRECT(fpath) BRAHMA_NOOP_MACRO
#define BRAHMA_LOG_STDERR_REDIRECT(fpath) BRAHMA_NOOP_MACRO
#endif  // BRAHMA_LOGGER_CPP_LOGGER
        // -----------------------------------------------

//=============================================================================
#endif  // BRAHMA_LOGGER_NO_LOG
        //=============================================================================

#endif /* BRAHMA_COMMON_BRAHMA_LOGGING_H */