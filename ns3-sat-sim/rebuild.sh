cd simulator || exit 1
./ns3 clean || exit 1
./ns3 configure -d optimized --enable-mpi || exit 1
./ns3 build || exit 1