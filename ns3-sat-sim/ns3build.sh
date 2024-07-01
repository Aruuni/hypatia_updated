rm -rf simulator
mkdir simulator
git clone -b ns-3.39 https://gitlab.com/nsnam/ns-3-dev simulator || exit 1
cp -r src simulator
cp -r contrib simulator
cp -r scratch simulator
cp -r ns3 simulator
