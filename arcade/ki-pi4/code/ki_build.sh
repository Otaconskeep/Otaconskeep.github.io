# 1. get the newer MAME 2003-Plus source
cd ~ && git clone https://github.com/libretro/mame2003-plus-libretro.git
cd mame2003-plus-libretro            # built from master @ 2a60eda

# 2. compile ON the Pi - one job at a time
make -j1 platform=rpi4               # -j3 ran OUT OF MEMORY on 2 GB

# 3. install as its OWN core (stock lr-mame2003-plus untouched)
sudo mkdir -p /opt/retropie/libretrocores/lr-mame2003-plus-ki
sudo cp mame2003_plus_libretro.so \
        /opt/retropie/libretrocores/lr-mame2003-plus-ki/

# 4. add it to /opt/retropie/configs/arcade/emulators.cfg (one line):
lr-mame2003-plus-ki = "/opt/retropie/emulators/retroarch/bin/retroarch
    -L /opt/retropie/libretrocores/lr-mame2003-plus-ki/mame2003_plus_libretro.so
    --config /opt/retropie/configs/arcade/retroarch.cfg %ROM%"

# 5. ROMs in ~/RetroPie/roms/arcade/
#    kinst.zip  + kinst/kinst.chd       kinst2.zip + its CHD folder
