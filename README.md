# hdlplayground

Document, build and simulate hardware designs (MyHDL, VHDL, Verilog)

**This repository is no longer maintained. Don't use for new designs**

To run locally, you'll have to check out the code and build the docker container in Linux as follows:

```
docker build -t hdlpg .
```

Then run it:

```
docker run -it --rm -p 8888:8888 hdlpg jupyter notebook --ip 0.0.0.0 --no-browser
```

Add the `--device=/dev/bus/usb` option if you have a VersaECP5 board or other ECP5 based hardware you want to try programming.

