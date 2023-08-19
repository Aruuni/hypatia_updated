rm -rf simulator
mkdir simulator
git clone https://github.com/nsnam/ns-3-dev-git.git simulator || exit 1
cp -r src simulator
cp -r contrib simulator
cp -r scratch simulator
cp -r ns3 simulator
bash build.sh