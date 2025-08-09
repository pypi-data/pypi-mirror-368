//
// Created by haridev on 8/28/22.
//

#ifndef TAILORFS_INTERFACE_UTILITY_H
#define TAILORFS_INTERFACE_UTILITY_H
/* Internal Headers */
#include <brahma/enumeration.h>

/* External Headers */
#include <string>
#include <unordered_map>
#include <unordered_set>
namespace brahma {
class InterfaceUtility {
  std::unordered_map<brahma::InterfaceType, std::unordered_set<std::string>>
      filenames;
  std::unordered_map<brahma::InterfaceType, std::unordered_set<std::string>>
      excluded_filenames;

 public:
  InterfaceUtility() : filenames(), excluded_filenames() {}
  void exclude_file(const char *filename, brahma::InterfaceType interface);

  void include_file(const char *filename, brahma::InterfaceType interface);

  bool is_traced(const char *filename, brahma::InterfaceType interface);

  void track_file(const char *filename, brahma::InterfaceType interface);

  void untrack_file(const char *filename, brahma::InterfaceType interface);
};
}  // namespace brahma
#endif  // TAILORFS_INTERFACE_UTILITY_H
