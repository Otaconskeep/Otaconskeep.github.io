# Tekken 3 + Tekken Tag: ReSys12 (Namco System 12), GPL-3
mkdir -p ~/resys12-build && cd ~/resys12-build
git clone https://github.com/Reyanon/ReSys12.git   # built @ fc52321

# the Vita front-end is swapped for a small Linux/SDL2 one
# (main_linux.c + rs12_threads_linux.c + Makefile in ./port)
cd port && make RS12=../ReSys12        # -> ./resys12

sudo mkdir -p /opt/retropie/emulators/resys12
sudo cp resys12 /opt/retropie/emulators/resys12/

# arcade/emulators.cfg
resys12 = "/opt/retropie/emulators/resys12/resys12 %ROM%"

# ROM sets: tekken3.zip (tekken3je1)   tektagt.zip (tektagtuc1)
# test speed:  resys12 tektagt.zip --bench 3000
