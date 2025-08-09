#ifndef gribjump_gribjump_version_h
#define gribjump_gribjump_version_h

#define gribjump_VERSION_STR "0.10.2"
#define gribjump_VERSION     "0.10.2"

#define gribjump_VERSION_MAJOR 0
#define gribjump_VERSION_MINOR 10
#define gribjump_VERSION_PATCH 2

#ifdef __cplusplus
extern "C" {
#endif

const char * gribjump_version();

unsigned int gribjump_version_int();

const char * gribjump_version_str();

const char * gribjump_git_sha1();

#ifdef __cplusplus
}
#endif

#endif
