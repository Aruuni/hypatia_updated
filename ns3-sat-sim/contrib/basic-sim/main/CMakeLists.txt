build_lib(
  LIBNAME basic-sim-main-full
  SOURCE_FILES main-full.cc
  LIBRARIES_TO_LINK
    ${libbasic-sim}
)