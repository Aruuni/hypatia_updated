# Main information
echo "Hypatia: build"
echo ""
echo "It is highly recommend you use a recent Linux operating system (e.g., Ubuntu 20 or higher)."
echo "Python version 3.7+ is required."
echo ""

# ns3-sat-sim
echo "Rebuilding ns3-sat-sim..."
cd ns3-sat-sim || exit 1
# Can be skipped by travis as building is also called in running of tests

bash rebuild.sh || exit 1
  # For optimized: bash build.sh --optimized || exit 1

cd .. || exit 1

# Confirmation build is finished
echo ""
echo "Hypatia modules have been built."
